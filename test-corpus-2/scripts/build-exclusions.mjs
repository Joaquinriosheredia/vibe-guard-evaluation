// Builds exclusions.json: every repository used before in any vibe-guard corpus, trial, audit,
// fixture or label, and every repository test-corpus-1 processed (EXCLUSION-SOURCES.md). Reads
// each source with `git show` at the pinned commit, never from a working tree, and makes no
// network call. Its output is committed with the pre-registration, before the search.
//
//   node scripts/build-exclusions.mjs <python-vibe-guard> <java-vibe-guard> <vibe-guard> <vibe-guard-scan> <vibe-guard-evaluation>
import { join } from 'path';
import { pathToFileURL } from 'url';
import { DIR, git, writeJson } from './lib.mjs';

// `text`: every GitHub URL in any file whose path matches (markdown, fixtures, tests).
export const SOURCES = {
  'python-vibe-guard': { commit: '4af3ce75f4b896a77c94e58b685fad4f5c6ff669', lists: [
    'research/datasets/100-repos.json', 'research/datasets/250-repos.json', 'research/datasets/1000-repos.json',
    'validation/aggregate.json', 'validation/breakdown.json',
  ], text: [/^README\.md$/, /^research\/.*\.md$/, /^validation\/[^/]*\.md$/, /^tests\//, /^demo\//] },
  'java-vibe-guard': { commit: 'a4c5380761ded82da6581dca79d02f39ff057a18', lists: ['validation/repos.json', 'validation/b0-corpus/corpus.json'],
    text: [/^README\.md$/, /^validation\/.*\.md$/, /^cli\/test-fixtures\//, /^cli\/test\//, /^mcp-server\/src\/test\//] },
  'vibe-guard': { commit: '97ed6564f2acd0d3662584267ea461cbc1603fa2', lists: [], text: [/^docs\/.*\.md$/, /^[^/]*\.md$/] },
  'vibe-guard-scan': { commit: 'f39dc7dcc2180a28cacd125039bba40e5be97bb4', lists: [], text: [/\.md$/, /^test\//] },
  'vibe-guard-evaluation': { commit: 'b0242054b8d4c08b1c1a8d8fa94d6aed3f6b7fc0', lists: [
    'test-corpus-1/exclusions.json', 'test-corpus-1/corpus.json', 'test-corpus-1/dev-labels.json',
  ], text: [/^test-corpus-1\/.*\.md$/] },
};
// The development set of the 2026-10-12 trial (vibe-guard docs/ensayo-auditoria-2026-10-12/).
const TRIAL = ['halo-dev/halo', 'YunaiV/ruoyi-vue-pro', 'open-webui/open-webui'];
// validation/breakdown.json names four repositories by their short name only.
const BREAKDOWN_SHORT = { fastapi: 'tiangolo/fastapi', celery: 'celery/celery', aiohttp: 'aio-libs/aiohttp', httpx: 'encode/httpx' };
const OWN = 'joaquinriosheredia';
const NAME_RE = /^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$/;
const URL_RE = /github\.com\/([A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+)/g;

/** Repository names in a JSON list: every `repo`, `full_name` and `name` holding "owner/name". */
export function namesInList(path, data) {
  const out = [];
  const visit = (x) => {
    if (Array.isArray(x)) x.forEach(visit);
    else if (x && typeof x === 'object') {
      for (const k of ['repo', 'full_name', 'name']) if (typeof x[k] === 'string' && NAME_RE.test(x[k])) out.push(x[k]);
      for (const v of Object.values(x)) if (v && typeof v === 'object') visit(v);
    }
  };
  visit(data);
  if (path === 'validation/breakdown.json') out.push(...Object.keys(data.repos ?? {}).map((k) => BREAKDOWN_SHORT[k]).filter(Boolean));
  return out;
}

export const namesInText = (text) => [...text.matchAll(URL_RE)].map((m) => m[1]);

export function normalize(name) {
  const n = name.replace(/\.git$/, '').replace(/[.]+$/, '');
  return NAME_RE.test(n) && !n.toLowerCase().startsWith(`${OWN}/`) ? n : null;
}

// Runs only when executed directly (never on import): see test/import-is-inert.test.mjs.
if (import.meta.url === pathToFileURL(process.argv[1] ?? '').href) await main();

async function main() {
  const repos = process.argv.slice(2);
  const keys = Object.keys(SOURCES);
  if (repos.length !== keys.length) { console.error(`usage: build-exclusions.mjs ${keys.map((k) => `<${k}>`).join(' ')}`); process.exit(2); }
  const local = Object.fromEntries(keys.map((k, i) => [k, repos[i]]));

  const found = new Map(); // lowercase full name → { name, sources:Set }
  const add = (raw, source) => {
    const name = normalize(raw);
    if (!name) return;
    const key = name.toLowerCase();
    if (!found.has(key)) found.set(key, { name, sources: new Set() });
    found.get(key).sources.add(source);
  };

  for (const [repo, src] of Object.entries(SOURCES)) {
    const cwd = local[repo];
    const commit = git(['rev-parse', `${src.commit}^{commit}`], { cwd }).trim();
    const at = `${repo}@${commit.slice(0, 7)}`;
    const files = git(['ls-tree', '-r', '--name-only', commit], { cwd }).split('\n').filter(Boolean);
    for (const path of src.lists) {
      for (const n of namesInList(path, JSON.parse(git(['show', `${commit}:${path}`], { cwd })))) add(n, `${at}:${path}`);
    }
    for (const path of files.filter((f) => src.text.some((re) => re.test(f)))) {
      let text;
      try { text = git(['show', `${commit}:${path}`], { cwd }); } catch { continue; } // binary or unreadable
      for (const n of namesInText(text)) add(n, `${at}:${path} (URL)`);
    }
  }
  for (const n of TRIAL) add(n, 'vibe-guard audit trial 2026-10-12 (development set)');
  add('nysenate/OpenLegislation', 'vibe-guard docs/FASE-3-b0-found-in-wild-openlegislation.md (named)');

  const entries = [...found.values()].sort((a, b) => a.name.toLowerCase().localeCompare(b.name.toLowerCase()))
    .map((e) => ({ name: e.name, sources: [...e.sources].sort() }));
  const sources = Object.fromEntries(Object.entries(SOURCES).map(([k, v]) => [k, { ...v, text: v.text.map(String) }]));
  writeJson(join(DIR, 'exclusions.json'), { builtAt: new Date().toISOString(), sources, count: entries.length, repositories: entries });
  console.log(`exclusions.json: ${entries.length} repositories`);
}
