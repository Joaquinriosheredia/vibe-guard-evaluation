// Builds exclusions.json: every repository used before in any corpus, trial or audit
// (EXCLUSION-SOURCES.md). Reads each source from a pinned commit (`git show`), never from a
// working tree. Run before the search; its output is committed with the pre-registration.
//
//   node scripts/build-exclusions.mjs <python-vibe-guard> <java-vibe-guard> <vibe-guard>
import { DIR, git, writeJson } from './lib.mjs';
import { join } from 'path';
import { pathToFileURL } from 'url';

export const SOURCES = {
  'python-vibe-guard': { commit: '2511da27906f0eed1767d4cf1d05bbc79f87c22d', lists: [
    'research/datasets/100-repos.json', 'research/datasets/250-repos.json', 'research/datasets/1000-repos.json',
    'validation/aggregate.json', 'validation/breakdown.json',
  ], markdown: [/^README\.md$/, /^research\/.*\.md$/, /^validation\/[^/]*\.md$/] },
  'java-vibe-guard': { commit: 'a4c5380', lists: ['validation/repos.json', 'validation/b0-corpus/corpus.json'],
    markdown: [/^README\.md$/, /^validation\/.*\.md$/] },
  'vibe-guard': { commit: 'eb88a8d', lists: [], markdown: [/^docs\/.*\.md$/, /^STATUS\.md$/, /^DECISIONS\.md$/] },
};
// The development set of the 2026-10-12 trial (vibe-guard docs/ensayo-auditoria-2026-10-12/).
const TRIAL = ['halo-dev/halo', 'YunaiV/ruoyi-vue-pro', 'open-webui/open-webui'];
// validation/breakdown.json names four repositories by their short name only.
const BREAKDOWN_SHORT = { fastapi: 'tiangolo/fastapi', celery: 'celery/celery', aiohttp: 'aio-libs/aiohttp', httpx: 'encode/httpx' };
const OWN = 'joaquinriosheredia';
const NAME_RE = /^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$/;
const URL_RE = /github\.com\/([A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+)/g;

const found = new Map(); // lowercase full name → { name, sources:Set }
function add(name, source) {
  name = name.replace(/\.git$/, '').replace(/[.]+$/, '');
  if (!NAME_RE.test(name) || name.toLowerCase().startsWith(`${OWN}/`)) return;
  const key = name.toLowerCase();
  if (!found.has(key)) found.set(key, { name, sources: new Set() });
  found.get(key).sources.add(source);
}

function namesInList(path, data) {
  const out = [];
  const visit = (x) => {
    if (Array.isArray(x)) x.forEach(visit);
    else if (x && typeof x === 'object') {
      if (typeof x.repo === 'string') out.push(x.repo);
      if (typeof x.full_name === 'string') out.push(x.full_name);
      for (const v of Object.values(x)) if (v && typeof v === 'object') visit(v);
    }
  };
  visit(data);
  if (path === 'validation/breakdown.json') out.push(...Object.keys(data.repos ?? {}).map((k) => BREAKDOWN_SHORT[k]).filter(Boolean));
  return out;
}

// Runs only when executed directly (never on import): see test/import-is-inert.test.mjs.
if (import.meta.url === pathToFileURL(process.argv[1] ?? '').href) await main();

async function main() {
  const [pyRepo, javaRepo, coordRepo] = process.argv.slice(2);
  if (!coordRepo) { console.error('usage: build-exclusions.mjs <python-vibe-guard> <java-vibe-guard> <vibe-guard>'); process.exit(2); }
  const local = { 'python-vibe-guard': pyRepo, 'java-vibe-guard': javaRepo, 'vibe-guard': coordRepo };

  for (const [repo, src] of Object.entries(SOURCES)) {
    const cwd = local[repo];
    const commit = git(['rev-parse', `${src.commit}^{commit}`], { cwd }).trim();
    const files = git(['ls-tree', '-r', '--name-only', commit], { cwd }).split('\n').filter(Boolean);
    for (const path of src.lists) {
      for (const n of namesInList(path, JSON.parse(git(['show', `${commit}:${path}`], { cwd })))) add(n, `${repo}@${commit.slice(0, 7)}:${path}`);
    }
    for (const path of files.filter((f) => src.markdown.some((re) => re.test(f)))) {
      for (const m of git(['show', `${commit}:${path}`], { cwd }).matchAll(URL_RE)) add(m[1], `${repo}@${commit.slice(0, 7)}:${path} (URL)`);
    }
  }
  for (const n of TRIAL) add(n, 'vibe-guard audit trial 2026-10-12 (development set)');
  // Audited "Found in the Wild" candidate, named without a URL (vibe-guard docs/FASE-3-b0-found-in-wild-openlegislation.md).
  add('nysenate/OpenLegislation', 'vibe-guard@eb88a8d:docs/FASE-3-b0-found-in-wild-openlegislation.md (named)');

  const entries = [...found.values()].sort((a, b) => a.name.toLowerCase().localeCompare(b.name.toLowerCase()))
    .map((e) => ({ name: e.name, sources: [...e.sources].sort() }));
  const sources = Object.fromEntries(Object.entries(SOURCES).map(([k, v]) => [k, { ...v, markdown: v.markdown.map(String) }]));
  writeJson(join(DIR, 'exclusions.json'), { builtAt: new Date().toISOString(), sources, count: entries.length, repositories: entries });
  console.log(`exclusions.json: ${entries.length} repositories`);
}
