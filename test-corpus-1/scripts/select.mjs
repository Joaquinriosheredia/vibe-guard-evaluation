// Step 1 of the pre-registration: the search, run once. Writes search-raw/, the resolved
// exclusion list (exclusions-resolved.json) and the frozen, ordered candidates.json with the
// metadata exclusions (3a used before, 3b own, 3c toy keywords, 3d pool overlap) applied.
//
//   node scripts/select.mjs
import { existsSync, mkdirSync } from 'fs';
import { join } from 'path';
import { pathToFileURL } from 'url';
import { DIR, gh, readJson, sleep, writeJson } from './lib.mjs';

const OWNER = 'joaquinriosheredia';
// D6 (decided 2026-10-14): fixed keyword list, matched against the tokens of the name and
// the description (split on camelCase and on any non-alphanumeric character, lowercased).
export const TOY_KEYWORDS = [
  'tutorial', 'tutorials', 'example', 'examples', 'sample', 'samples', 'demo', 'demos',
  'course', 'courses', 'workshop', 'boilerplate', 'template', 'templates', 'starter',
  'starters', 'scaffold', 'interview', 'exercise', 'exercises', 'homework', 'awesome',
  'cheatsheet', 'kata', 'playground', 'bootcamp',
];
const TOY = new Set(TOY_KEYWORDS);

export function tokens(text) {
  return (text ?? '').replace(/([a-z0-9])([A-Z])/g, '$1 $2').toLowerCase().split(/[^a-z0-9]+/).filter(Boolean);
}
export const toyKeyword = (repo) => [...tokens(repo.name), ...tokens(repo.description)].find((t) => TOY.has(t)) ?? null;

export function queries(selectionDate) {
  const d = new Date(selectionDate);
  d.setUTCDate(d.getUTCDate() - 183);
  const cutoff = d.toISOString().slice(0, 10);
  const common = `fork:false archived:false is:public stars:>=100 size:100..1000000 pushed:>=${cutoff}`;
  return { cutoff, java: `topic:spring-boot language:Java ${common}`, python: `topic:fastapi language:Python ${common}` };
}

async function search(pool, q, rawDir) {
  const items = [];
  let total = null;
  for (let page = 1; page <= 10; page++) {
    const path = `/search/repositories?q=${encodeURIComponent(q)}&sort=stars&order=desc&per_page=100&page=${page}`;
    const { status, body } = await gh(path);
    if (status !== 200) throw new Error(`search ${pool} page ${page}: HTTP ${status} ${JSON.stringify(body)}`);
    writeJson(join(rawDir, `${pool}-page-${page}.json`), { fetchedAt: new Date().toISOString(), path, body });
    total ??= body.total_count;
    items.push(...body.items);
    if (body.items.length < 100 || items.length >= 1000) break;
    await sleep(3000); // search API: 30 requests/minute
  }
  return { total, items };
}

async function resolveExclusions() {
  const out = [];
  const list = readJson(join(DIR, 'exclusions.json')).repositories;
  for (let i = 0; i < list.length; i += 8) {
    const chunk = await Promise.all(list.slice(i, i + 8).map(async (e) => {
      const { status, body } = await gh(`/repos/${e.name}`);
      return status === 200 ? { name: e.name, id: body.id, current: body.full_name } : { name: e.name, id: null, current: null, status };
    }));
    out.push(...chunk);
  }
  return out;
}

// The search runs only when this file is executed directly (never on import).
if (import.meta.url === pathToFileURL(process.argv[1] ?? '').href) await main();

async function main() {
  const candidatesPath = join(DIR, 'candidates.json');
  if (existsSync(candidatesPath)) { console.error('candidates.json exists: the search is run once (pre-registration, step 2)'); process.exit(2); }

  const selectedAt = new Date().toISOString();
  const q = queries(selectedAt);
  const rawDir = join(DIR, 'search-raw');
  mkdirSync(rawDir, { recursive: true });

  const resolved = await resolveExclusions();
  writeJson(join(DIR, 'exclusions-resolved.json'), { resolvedAt: new Date().toISOString(), repositories: resolved });
  const usedIds = new Set(resolved.filter((r) => r.id).map((r) => r.id));
  const usedNames = new Set(resolved.flatMap((r) => [r.name, r.current]).filter(Boolean).map((n) => n.toLowerCase()));

  const pools = {};
  const totals = {};
  const seen = new Set();
  for (const pool of ['java', 'python']) {
    const { total, items } = await search(pool, q[pool], rawDir);
    totals[pool] = total;
    const ordered = [...items].sort((a, b) => b.stargazers_count - a.stargazers_count || a.full_name.toLowerCase().localeCompare(b.full_name.toLowerCase()));
    pools[pool] = ordered.map((r, rank) => {
      let exclusion = null;
      if (usedIds.has(r.id) || usedNames.has(r.full_name.toLowerCase())) exclusion = '3a used before';
      else if (r.owner.login.toLowerCase() === OWNER) exclusion = '3b own repository';
      else if (toyKeyword(r)) exclusion = `3c toy keyword "${toyKeyword(r)}"`;
      else if (seen.has(r.id)) exclusion = '3d in both pools: kept in the java pool only';
      seen.add(r.id);
      return {
        rank: rank + 1, id: r.id, full_name: r.full_name, stars: r.stargazers_count, default_branch: r.default_branch,
        size_kb: r.size, pushed_at: r.pushed_at, description: r.description, exclusion,
      };
    });
    await sleep(3000);
  }

  writeJson(candidatesPath, { selectedAt, cutoff: q.cutoff, queries: { java: q.java, python: q.python }, total_count: totals, pools });
  for (const pool of ['java', 'python']) {
    const eligible = pools[pool].filter((c) => !c.exclusion).length;
    console.log(`${pool}: total_count ${totals[pool]}, ${pools[pool].length} read, ${eligible} eligible by metadata`);
  }
}
