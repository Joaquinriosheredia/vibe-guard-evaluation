// Search and selection of PREREGISTRATION.md, run once, after the pre-registration is merged and
// FROZEN.json is filled. Writes search-raw/, exclusions-resolved.json and the frozen, ordered
// candidates.json (subpools java-A..java-D, python-A, python-B) with the metadata exclusions
// applied (3a used before, 3b own, 3c toy keywords, 3c2 study repositories, 3d pool overlap).
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

// PREREGISTRATION.md, "Java pool": T1 = test-corpus-3's 11 topics, T2 = 14 new ones.
export const JAVA_T1 = ['spring-boot', 'spring-kafka', 'kafka', 'apache-kafka', 'spring-webflux', 'webflux',
  'project-reactor', 'reactor', 'reactive', 'spring-cloud', 'microservices'];
export const JAVA_T2 = ['spring', 'spring-boot-3', 'spring-cloud-stream', 'kafka-streams', 'kafka-consumer',
  'kafka-producer', 'event-driven', 'event-driven-architecture', 'event-sourcing', 'cqrs',
  'r2dbc', 'reactive-programming', 'reactive-streams', 'rsocket'];
export const JAVA_SUBPOOLS = {
  'java-A': { topics: JAVA_T1, stars: '>=50' },
  'java-B': { topics: JAVA_T2, stars: '>=50' },
  'java-C': { topics: [...JAVA_T1, ...JAVA_T2], stars: '20..49' },
  'java-D': { topics: [...JAVA_T1, ...JAVA_T2], stars: '10..19' },
};
export const PYTHON_B_TOPICS = ['fastapi', 'aiohttp', 'starlette', 'litestar', 'sanic', 'quart'];
export const POOLS = ['java-A', 'java-B', 'java-C', 'java-D', 'python-A', 'python-B'];
export const isJava = (pool) => pool.startsWith('java-');

export function tokens(text) {
  return (text ?? '').replace(/([a-z0-9])([A-Z])/g, '$1 $2').toLowerCase().split(/[^a-z0-9]+/).filter(Boolean);
}
const repoName = (repo) => repo.name ?? repo.full_name.split('/')[1];
export const toyKeyword = (repo) => [...tokens(repoName(repo)), ...tokens(repo.description)].find((t) => TOY.has(t)) ?? null;

// Exclusion c2 (REVIEW-CRITERIA.md v1 §2.4, copied verbatim in PREREGISTRATION.md).
const STUDY_LAST = new Set(['study', 'studies', 'learning', 'notes']);
const STUDY_NOT_BEFORE = new Set('machine deep reinforcement federated transfer meta active contrastive online incremental'.split(' '));
const STUDY_PAIRS = ['study notes', 'learning notes', 'for learning', 'for study', 'learning purpose',
  'learning purposes', 'learning project', 'study project'];
const STUDY_SUBSTRINGS = ['学习笔记', '学习记录', '学习项目', '练手'];
const STUDY_TOPICS = new Set(['study', 'studies', 'study-notes', 'learning-notes', 'notes']);

/** c2: the first clause that holds ("name", "description" or "topics") with what matched, else null. */
export function studyRepository(repo) {
  const name = repoName(repo).toLowerCase().split(/[^a-z0-9]+/).filter(Boolean); // no camelCase split
  const last = name.at(-1);
  if (STUDY_LAST.has(last) && !STUDY_NOT_BEFORE.has(name.at(-2))) return `name token "${last}"`;
  const t = tokens(repo.description); // split as in the toy filter
  const pairs = new Set(t.slice(1).map((w, i) => `${t[i]} ${w}`));
  const pair = STUDY_PAIRS.find((p) => pairs.has(p));
  if (pair) return `description "${pair}"`;
  const desc = (repo.description ?? '').toLowerCase();
  const sub = STUDY_SUBSTRINGS.find((s) => desc.includes(s));
  if (sub) return `description "${sub}"`;
  const topic = (repo.topics ?? []).map((x) => x.toLowerCase()).find((x) => STUDY_TOPICS.has(x));
  return topic ? `topic "${topic}"` : null;
}

/** The exact query strings, in order, per subpool. `<D>` = selection date (UTC) minus 183 days. */
export function queries(selectionDate) {
  const d = new Date(selectionDate);
  d.setUTCDate(d.getUTCDate() - 183);
  const cutoff = d.toISOString().slice(0, 10);
  const q = (lang, stars) => `language:${lang} fork:false archived:false is:public size:100..1000000 pushed:>=${cutoff} stars:${stars}`;
  const out = { cutoff };
  for (const [pool, { topics, stars }] of Object.entries(JAVA_SUBPOOLS)) out[pool] = topics.map((t) => `topic:${t} ${q('Java', stars)}`);
  out['python-A'] = [`topic:fastapi ${q('Python', '>=100')}`];
  out['python-B'] = PYTHON_B_TOPICS.map((t) => `topic:${t} ${q('Python', '>=50')}`);
  return out;
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
 * 3c2 study repository, 3d overlap (a repository in the Java pool is kept there only, in its first
 * Java subpool; one in python-A is not repeated in python-B). `earlier` holds the ids of the
 * subpools already listed, in the order java-A..D, python-A, python-B.
 */
export function metadataExclusion(repo, pool, { usedIds, usedNames, earlier }) {
  if (usedIds.has(repo.id) || usedNames.has(repo.full_name.toLowerCase())) return '3a used before';
  if (repo.owner.login.toLowerCase() === OWNER) return '3b own repository';
  const toy = toyKeyword(repo);
  if (toy) return `3c toy keyword "${toy}"`;
  const study = studyRepository(repo);
  if (study) return `3c2 study repository: ${study}`;
  const first = Object.entries(earlier).find(([, ids]) => ids.has(repo.id))?.[0];
  if (first && isJava(first)) return `3d in the ${first} pool: kept there only`;
  if (first === 'python-A' && pool === 'python-B') return '3d in the python-A pool: kept there only';
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
    earlier: {},
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
      size_kb: r.size, pushed_at: r.pushed_at, description: r.description, topics: r.topics ?? [],
      queries: matched.map((m) => m + 1), exclusion: metadataExclusion(r, pool, ctx),
    }));
    ctx.earlier[pool] = new Set(pools[pool].map((c) => c.id));
  }

  const truncated = Object.fromEntries(POOLS.map((p) => [p, totals[p].map((t, i) => (t > 1000 ? i + 1 : null)).filter(Boolean)]));
  writeJson(candidatesPath, { selectedAt, cutoff: q.cutoff, queries: Object.fromEntries(POOLS.map((p) => [p, q[p]])), total_count: totals, truncated, pools });
  for (const pool of POOLS) {
    const eligible = pools[pool].filter((c) => !c.exclusion).length;
    console.log(`${pool}: total_count ${totals[pool].join('+')}, ${pools[pool].length} unique, ${eligible} eligible by metadata; truncated queries ${truncated[pool].join(', ') || 'none'}`);
  }
}
