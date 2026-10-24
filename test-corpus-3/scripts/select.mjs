// Search and selection of PREREGISTRATION.md, run once, after the pre-registration is merged and
// FROZEN.json is filled. Writes search-raw/, exclusions-resolved.json and the frozen, ordered
// candidates.json (pools java, python-A, python-B) with the metadata exclusions applied
// (3a used before, 3b own, 3c toy keywords, 3d pool overlap).
//
//   node scripts/select.mjs
import { existsSync, mkdirSync } from 'fs';
import { join } from 'path';
import { pathToFileURL } from 'url';
import { DIR, gh, loadFrozen, readJson, sleep, writeJson } from './lib.mjs';

const OWNER = 'joaquinriosheredia';
// The fixed toy-keyword list of test-corpus-1 (D6), unchanged.
export const TOY_KEYWORDS = [
  'tutorial', 'tutorials', 'example', 'examples', 'sample', 'samples', 'demo', 'demos',
  'course', 'courses', 'workshop', 'boilerplate', 'template', 'templates', 'starter',
  'starters', 'scaffold', 'interview', 'exercise', 'exercises', 'homework', 'awesome',
  'cheatsheet', 'kata', 'playground', 'bootcamp',
];
const TOY = new Set(TOY_KEYWORDS);

export const JAVA_TOPICS = ['spring-boot', 'spring-kafka', 'kafka', 'apache-kafka', 'spring-webflux', 'webflux',
  'project-reactor', 'reactor', 'reactive', 'spring-cloud', 'microservices'];
export const PYTHON_B_TOPICS = ['fastapi', 'aiohttp', 'starlette', 'litestar', 'sanic', 'quart'];
export const POOLS = ['java', 'python-A', 'python-B'];

export function tokens(text) {
  return (text ?? '').replace(/([a-z0-9])([A-Z])/g, '$1 $2').toLowerCase().split(/[^a-z0-9]+/).filter(Boolean);
}
export const toyKeyword = (repo) => [...tokens(repo.name), ...tokens(repo.description)].find((t) => TOY.has(t)) ?? null;

/** The exact query strings, in order, per pool. `<D>` = selection date (UTC) minus 183 days. */
export function queries(selectionDate) {
  const d = new Date(selectionDate);
  d.setUTCDate(d.getUTCDate() - 183);
  const cutoff = d.toISOString().slice(0, 10);
  const common = (stars) => `fork:false archived:false is:public stars:>=${stars} size:100..1000000 pushed:>=${cutoff}`;
  return {
    cutoff,
    java: JAVA_TOPICS.map((t) => `topic:${t} language:Java ${common(50)}`),
    'python-A': [`topic:fastapi language:Python ${common(100)}`],
    'python-B': PYTHON_B_TOPICS.map((t) => `topic:${t} language:Python ${common(50)}`),
  };
}

/** Union of search results by repository id; stars descending, ties by full_name (case-insensitive). */
export function orderUnion(resultLists) {
  const byId = new Map();
  resultLists.forEach((items, qi) => {
    for (const r of items) {
      if (!byId.has(r.id)) byId.set(r.id, { repo: r, matched: [] });
      byId.get(r.id).matched.push(qi);
    }
  });
  return [...byId.values()].sort((a, b) => b.repo.stargazers_count - a.repo.stargazers_count
    || a.repo.full_name.toLowerCase().localeCompare(b.repo.full_name.toLowerCase()));
}

/**
 * Metadata exclusion of one candidate, first match wins: 3a used before, 3b own, 3c toy keyword,
 * 3d overlap (a repository in the java pool is kept there only; one in python-A is not repeated in python-B).
 */
export function metadataExclusion(repo, pool, { usedIds, usedNames, javaIds, pythonAIds }) {
  if (usedIds.has(repo.id) || usedNames.has(repo.full_name.toLowerCase())) return '3a used before';
  if (repo.owner.login.toLowerCase() === OWNER) return '3b own repository';
  const toy = toyKeyword(repo);
  if (toy) return `3c toy keyword "${toy}"`;
  if (pool !== 'java' && javaIds.has(repo.id)) return '3d in the java pool: kept there only';
  if (pool === 'python-B' && pythonAIds.has(repo.id)) return '3d in the python-A pool: kept there only';
  return null;
}

async function search(name, q, rawDir) {
  const items = [];
  let total = null;
  for (let page = 1; page <= 10; page++) {
    const path = `/search/repositories?q=${encodeURIComponent(q)}&sort=stars&order=desc&per_page=100&page=${page}`;
    const { status, body } = await gh(path);
    if (status !== 200) throw new Error(`search ${name} page ${page}: HTTP ${status} ${JSON.stringify(body)}`);
    writeJson(join(rawDir, `${name}-page-${page}.json`), { fetchedAt: new Date().toISOString(), query: q, path, body });
    total ??= body.total_count;
    items.push(...body.items);
    await sleep(3000); // search API: 30 requests/minute
    if (body.items.length < 100 || items.length >= 1000) break;
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
  loadFrozen(); // refuses while FROZEN.json has a TO-FILL value
  const candidatesPath = join(DIR, 'candidates.json');
  if (existsSync(candidatesPath)) { console.error('candidates.json exists: the search is run once'); process.exit(2); }

  const selectedAt = new Date().toISOString();
  const q = queries(selectedAt);
  const rawDir = join(DIR, 'search-raw');
  mkdirSync(rawDir, { recursive: true });

  const resolved = await resolveExclusions();
  writeJson(join(DIR, 'exclusions-resolved.json'), { resolvedAt: new Date().toISOString(), repositories: resolved });
  const ctx = {
    usedIds: new Set(resolved.filter((r) => r.id).map((r) => r.id)),
    usedNames: new Set(resolved.flatMap((r) => [r.name, r.current]).filter(Boolean).map((n) => n.toLowerCase())),
    javaIds: new Set(), pythonAIds: new Set(),
  };

  const pools = {};
  const totals = {};
  for (const pool of POOLS) {
    const lists = [];
    totals[pool] = [];
    for (const [i, query] of q[pool].entries()) {
      const { total, items } = await search(`${pool}-q${i + 1}`, query, rawDir);
      totals[pool].push(total);
      lists.push(items);
    }
    pools[pool] = orderUnion(lists).map(({ repo: r, matched }, rank) => ({
      rank: rank + 1, id: r.id, full_name: r.full_name, stars: r.stargazers_count, default_branch: r.default_branch,
      size_kb: r.size, pushed_at: r.pushed_at, description: r.description, queries: matched.map((m) => m + 1),
      exclusion: metadataExclusion(r, pool, ctx),
    }));
    for (const c of pools[pool]) (pool === 'java' ? ctx.javaIds : pool === 'python-A' ? ctx.pythonAIds : new Set()).add(c.id);
  }

  writeJson(candidatesPath, { selectedAt, cutoff: q.cutoff, queries: { java: q.java, 'python-A': q['python-A'], 'python-B': q['python-B'] }, total_count: totals, pools });
  for (const pool of POOLS) {
    const eligible = pools[pool].filter((c) => !c.exclusion).length;
    console.log(`${pool}: total_count ${totals[pool].join('+')}, ${pools[pool].length} unique, ${eligible} eligible by metadata`);
  }
}
