// Steps 3e, 3f, 4-5 and the run of the pre-registration, with the stopping rule:
// batches of 20 + 20, then 10 + 10, from the frozen candidates.json, until the scanned
// corpus has >= 50 CRITICAL findings (counted, never reviewed) or a pool reaches 150.
//
//   VGS=<vibe-guard-scan checkout> PYVIBE=<pyvibe> WORK=<checkouts dir> node scripts/run.mjs
import { spawn } from 'child_process';
import { existsSync, mkdirSync, readFileSync, rmSync } from 'fs';
import { join } from 'path';
import { pathToFileURL } from 'url';
import { countFiles } from './count-files.mjs';
import { DIR, gh, git, readJson, slug, writeJson } from './lib.mjs';

const { VGS, PYVIBE, WORK } = process.env;

const FIRST_BATCH = 20;
const NEXT_BATCH = 10;
const CAP = 150;
const TARGET_CRITICAL = 50;
const TIMEOUT_MS = 30 * 60_000;
const MIN_FILES = 20;

// Runs only when executed directly (never on import): see test/import-is-inert.test.mjs.
if (import.meta.url === pathToFileURL(process.argv[1] ?? '').href) await main();

async function main() {
  if (!VGS || !PYVIBE || !WORK) throw new Error('VGS, PYVIBE and WORK are required');
  const candidates = readJson(join(DIR, 'candidates.json'));
  const corpusPath = join(DIR, 'corpus.json');
  const corpus = readJson(corpusPath, { batches: [], processed: [], frozen: false });
  const resultsDir = join(DIR, 'results');
  mkdirSync(resultsDir, { recursive: true });
  mkdirSync(WORK, { recursive: true });

  const save = () => writeJson(corpusPath, corpus);
  const included = (pool) => corpus.processed.filter((p) => p.pool === pool && p.status === 'included');

  function scan(checkout, out) {
    return new Promise((resolve) => {
      const started = Date.now();
      const child = spawn(process.execPath, [join(VGS, 'bin', 'vibe-guard.js'), 'scan', checkout, '--format', 'json', '--output', out], {
        env: { ...process.env, VIBE_GUARD_PYVIBE: PYVIBE, NO_COLOR: '1' }, stdio: ['ignore', 'ignore', 'pipe'], detached: true,
      });
      let stderr = '';
      child.stderr.on('data', (d) => { stderr = (stderr + d).slice(-4000); });
      const timer = setTimeout(() => { try { process.kill(-child.pid, 'SIGKILL'); } catch { /* gone */ } }, TIMEOUT_MS);
      child.on('close', (code, signal) => {
        clearTimeout(timer);
        resolve({ code, signal, ms: Date.now() - started, timedOut: Date.now() - started >= TIMEOUT_MS, stderr: stderr.trim() });
      });
    });
  }

  async function processCandidate(pool, c, batch) {
    const rec = { pool, batch, rank: c.rank, full_name: c.full_name, id: c.id, stars: c.stars, processedAt: new Date().toISOString() };
    // 5. Pinned commit: the default branch's SHA at selection time.
    const { status, body } = await gh(`/repos/${c.full_name}/commits/${encodeURIComponent(c.default_branch)}`);
    if (status !== 200) return { ...rec, status: 'excluded', reason: `3f cannot be fetched: commit lookup HTTP ${status}` };
    rec.commit = body.sha;
    const checkout = join(WORK, slug(c.full_name));
    try {
      rmSync(checkout, { recursive: true, force: true });
      mkdirSync(checkout, { recursive: true });
      git(['init', '-q'], { cwd: checkout });
      git(['fetch', '-q', '--depth', '1', `https://github.com/${c.full_name}.git`, rec.commit], { cwd: checkout, timeout: 15 * 60_000 });
      git(['-c', 'advice.detachedHead=false', 'checkout', '-q', 'FETCH_HEAD'], { cwd: checkout });
      const head = git(['rev-parse', 'HEAD'], { cwd: checkout }).trim();
      if (head !== rec.commit) throw new Error(`HEAD ${head} is not the pinned ${rec.commit}`);
    } catch (e) {
      return { ...rec, status: 'excluded', reason: `3f cannot be fetched: ${e.message.split('\n')[0].slice(0, 300)}` };
    }
    // 3e. Stack present at the pinned commit (counted with the scan's own exclusions).
    const files = await countFiles(checkout);
    rec.files = { java: files.java, python: files.python };
    if (pool === 'java' && (!files.springBoot || files.java < MIN_FILES)) {
      return { ...rec, status: 'excluded', reason: `3e stack: spring-boot build file ${files.springBoot ? 'found' : 'not found'}, ${files.java} .java files` };
    }
    if (pool === 'python' && (!files.fastapi || files.python < MIN_FILES)) {
      return { ...rec, status: 'excluded', reason: `3e stack: fastapi import ${files.fastapi ? 'found' : 'not found'}, ${files.python} .py files` };
    }
    // Run, exactly as a user would.
    const out = join(resultsDir, `${slug(c.full_name)}.json`);
    rmSync(out, { force: true });
    const r = await scan(checkout, out);
    rec.scan = { exitCode: r.code, signal: r.signal, durationMs: r.ms };
    if (r.timedOut) return { ...rec, status: 'excluded', reason: '3f TIMEOUT (30 min)', stderr: r.stderr };
    if (r.code !== 0 && r.code !== 1) {
      rmSync(out, { force: true });
      return { ...rec, status: 'excluded', reason: `3f scan exit ${r.code}`, stderr: r.stderr };
    }
    const report = JSON.parse(readFileSync(out, 'utf8'));
    // The counts must use the same excluded folders as the scan.
    rec.excludesMatch = JSON.stringify(report.excludes.applied) === JSON.stringify(files.applied);
    rec.critical = report.summary.critical;
    return { ...rec, status: 'included' };
  }

  const totalCritical = () => corpus.processed.filter((p) => p.status === 'included').reduce((n, p) => n + p.critical, 0);

  while (!corpus.frozen) {
    const batch = corpus.batches.length + 1;
    const quota = batch === 1 ? FIRST_BATCH : NEXT_BATCH;
    const added = {};
    for (const pool of ['java', 'python']) {
      added[pool] = 0;
      const done = new Set(corpus.processed.filter((p) => p.pool === pool).map((p) => p.id));
      for (const c of candidates.pools[pool]) {
        if (added[pool] >= quota || included(pool).length >= CAP) break;
        if (done.has(c.id)) continue;
        if (c.exclusion) {
          corpus.processed.push({ pool, batch, rank: c.rank, full_name: c.full_name, id: c.id, status: 'excluded', reason: c.exclusion });
          save();
          continue;
        }
        const rec = await processCandidate(pool, c, batch);
        corpus.processed.push(rec);
        save();
        if (rec.status === 'included') added[pool]++;
        console.log(`[batch ${batch}] ${pool} #${c.rank} ${c.full_name}: ${rec.status}${rec.reason ? ` (${rec.reason})` : ''}${rec.status === 'included' ? `, ${rec.critical} critical` : ''}`);
      }
    }
    const critical = totalCritical();
    corpus.batches.push({ batch, at: new Date().toISOString(), added, includedJava: included('java').length, includedPython: included('python').length, criticalSoFar: critical });
    const exhausted = (pool) => included(pool).length >= CAP || added[pool] < quota;
    if (critical >= TARGET_CRITICAL) {
      corpus.frozen = true;
      corpus.frozenReason = `${critical} CRITICAL >= ${TARGET_CRITICAL}`;
    } else if (exhausted('java') && exhausted('python')) {
      corpus.frozen = true;
      corpus.frozenReason = `cap or candidates exhausted with ${critical} CRITICAL < ${TARGET_CRITICAL}: criterion 1 not met`;
    }
    save();
    console.log(`batch ${batch}: java ${included('java').length}, python ${included('python').length}, CRITICAL so far ${critical}`);
  }
  console.log(`corpus frozen: ${corpus.frozenReason}`);
  if (!existsSync(join(DIR, 'env.txt'))) console.log('remember to write env.txt');
}
