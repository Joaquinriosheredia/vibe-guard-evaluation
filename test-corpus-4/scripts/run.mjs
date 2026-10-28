// Steps 3e-3g, the pinned commit and the run of PREREGISTRATION.md for ONE pool, with its own
// stopping rule (counts only, never verdicts). The pools stop independently.
//   java:   subpools java-A, java-B, java-C, java-D in that order; batches of 25 included
//           repositories; frozen at >= 50 Java CRITICAL, cap 500 included.
//   python: python-A first, python-B only after python-A is exhausted; batches of 20, then 10;
//           frozen at >= 100 Python CRITICAL, cap 150 included.
// Before anything, the tools are checked against FROZEN.json (verifyTools): annotated tags at the
// frozen commits, the wrapper checkout at its commit with no change, the wheel and the .tgz by
// name and sha256, the wrapper's lockfile and installed java-vibe-guard, the --version line.
//
//   VGS=<vibe-guard-scan checkout> PYVIBE=<pyvibe in the dedicated venv> WORK=<checkouts dir> \
//   PYVIBE_PRO=<pyvibe-pro checkout> JVG_PRO=<java-vibe-guard-pro checkout> \
//   WHEEL=<the installed .whl> TGZ=<the pinned .tgz> node scripts/run.mjs java|python
import { spawn, spawnSync } from 'child_process';
import { mkdirSync, readFileSync, rmSync } from 'fs';
import { basename, join } from 'path';
import { pathToFileURL } from 'url';
import { countFiles } from './count-files.mjs';
import { artifactProblems, DIR, gh, git, loadFrozen, observeTag, readJson, sha256File, sha512Integrity, slug, tagProblems, writeJson } from './lib.mjs';
import { POOLS, isJava } from './select.mjs';

export const POOL_RULES = {
  java: { language: 'java', firstBatch: 25, nextBatch: 25, cap: 500, target: 50 },
  python: { language: 'python', firstBatch: 20, nextBatch: 10, cap: 150, target: 100 },
};
const TIMEOUT_MS = 30 * 60_000;
const MIN_FILES = 20;

/** 3e and 3g on the counted checkout: null when eligible, else the exclusion reason. */
export function stackExclusion(pool, subpool, files) {
  if (pool === 'java') {
    if (!files.springBoot || files.java < MIN_FILES) return `3e stack: spring-boot build file ${files.springBoot ? 'found' : 'not found'}, ${files.java} .java files`;
    if (files.families.length === 0) return '3g no code signal (ASYNC, KAFKA, REACTOR)';
    return null;
  }
  const ok = subpool === 'python-A' ? files.pyFrameworks.includes('fastapi') : files.pyFrameworks.length > 0;
  if (!ok || files.python < MIN_FILES) return `3e stack: ${subpool === 'python-A' ? 'fastapi' : 'framework'} import ${ok ? 'found' : 'not found'}, ${files.python} .py files`;
  return null;
}

/** CRITICAL findings of the pool's language in one wrapper report. */
export const poolCritical = (report, language) => report.findings.filter((f) => f.severity === 'critical' && f.language === language).length;

/** The candidates of one pool, subpools in pre-registered order (java-A..D; python-A, python-B). */
export function poolCandidates(candidates, pool) {
  return POOLS.filter((p) => (pool === 'java') === isJava(p)).flatMap((p) => candidates.pools[p].map((c) => ({ ...c, subpool: p })));
}

/** Every identity problem of the tools against FROZEN.json; empty when they are exactly the frozen ones. */
export function verifyTools(frozen, env) {
  const problems = [
    ...tagProblems('vibe-guard-scan', frozen.vibeGuardScan, observeTag(env.VGS, frozen.vibeGuardScan.tag), { atHead: true }),
    ...tagProblems('pyvibe-pro', frozen.pyvibePro, observeTag(env.PYVIBE_PRO, frozen.pyvibePro.tag)),
    ...tagProblems('java-vibe-guard-pro', frozen.javaVibeGuardPro, observeTag(env.JVG_PRO, frozen.javaVibeGuardPro.tag)),
  ];
  const lock = JSON.parse(readFileSync(join(env.VGS, 'package-lock.json'), 'utf8'));
  problems.push(...artifactProblems(frozen, {
    wheel: { name: basename(env.WHEEL), sha256: sha256File(env.WHEEL) },
    tgz: { name: basename(env.TGZ), sha256: sha256File(env.TGZ), integrity: sha512Integrity(env.TGZ) },
    lockIntegrity: lock.packages?.['node_modules/java-vibe-guard']?.integrity ?? null,
    installedVersion: JSON.parse(readFileSync(join(env.VGS, 'node_modules', 'java-vibe-guard', 'package.json'), 'utf8')).version,
  }));
  const v = spawnSync(process.execPath, [join(env.VGS, 'bin', 'vibe-guard.js'), '--version'], { encoding: 'utf8', env: { ...process.env, VIBE_GUARD_PYVIBE: env.PYVIBE } });
  if (v.stdout.trim() !== frozen.vibeGuardScan.versionLine) problems.push(`--version is "${v.stdout.trim()}", expected "${frozen.vibeGuardScan.versionLine}"`);
  return problems;
}

/** Stopping decision after a batch: { frozen, reason }. */
export function stopDecision(rules, { critical, included, addedThisBatch, quota }) {
  if (critical >= rules.target) return { frozen: true, reason: `${critical} ${rules.language} CRITICAL >= ${rules.target}` };
  if (included >= rules.cap || addedThisBatch < quota) {
    return { frozen: true, reason: `${included >= rules.cap ? `cap of ${rules.cap} included repositories` : 'candidates exhausted'} with ${critical} ${rules.language} CRITICAL < ${rules.target}: criterion 1 NOT MET for ${rules.language}` };
  }
  return { frozen: false, reason: null };
}

// Runs only when executed directly (never on import): see test/import-is-inert.test.mjs.
if (import.meta.url === pathToFileURL(process.argv[1] ?? '').href) await main();

async function main() {
  const pool = process.argv[2];
  const rules = POOL_RULES[pool];
  const { VGS, PYVIBE, WORK } = process.env;
  if (!rules) throw new Error('usage: run.mjs java|python');
  const need = ['VGS', 'PYVIBE', 'WORK', 'PYVIBE_PRO', 'JVG_PRO', 'WHEEL', 'TGZ'].filter((k) => !process.env[k]);
  if (need.length) throw new Error(`${need.join(', ')} required`);

  // The tools must be exactly the frozen ones.
  const frozen = loadFrozen();
  const problems = verifyTools(frozen, process.env);
  if (problems.length) throw new Error(`tools are not the frozen ones:\n- ${problems.join('\n- ')}`);

  const candidates = readJson(join(DIR, 'candidates.json'));
  const list = poolCandidates(candidates, pool);
  const corpusPath = join(DIR, `corpus-${pool}.json`);
  const corpus = readJson(corpusPath, { pool, rules, batches: [], processed: [], frozen: false });
  const resultsDir = join(DIR, 'results', pool);
  mkdirSync(resultsDir, { recursive: true });
  mkdirSync(WORK, { recursive: true });
  const save = () => writeJson(corpusPath, corpus);
  const included = () => corpus.processed.filter((p) => p.status === 'included');

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

  async function processCandidate(c, batch) {
    const rec = { pool, subpool: c.subpool, batch, rank: c.rank, full_name: c.full_name, id: c.id, stars: c.stars, processedAt: new Date().toISOString() };
    const { status, body } = await gh(`/repos/${c.full_name}/commits/${encodeURIComponent(c.default_branch)}`);
    if (status !== 200) return { ...rec, status: 'excluded', reason: `3f cannot be fetched: commit lookup HTTP ${status}` };
    rec.commit = body.sha;
    const checkout = join(WORK, pool, slug(c.full_name));
    try {
      rmSync(checkout, { recursive: true, force: true });
      mkdirSync(checkout, { recursive: true });
      git(['init', '-q'], { cwd: checkout });
      git(['fetch', '-q', '--depth', '1', `https://github.com/${c.full_name}.git`, rec.commit], { cwd: checkout, timeout: 15 * 60_000 });
      git(['-c', 'advice.detachedHead=false', 'checkout', '-q', 'FETCH_HEAD'], { cwd: checkout });
      const h = git(['rev-parse', 'HEAD'], { cwd: checkout }).trim();
      if (h !== rec.commit) throw new Error(`HEAD ${h} is not the pinned ${rec.commit}`);
    } catch (e) {
      rmSync(checkout, { recursive: true, force: true });
      return { ...rec, status: 'excluded', reason: `3f cannot be fetched: ${e.message.split('\n')[0].slice(0, 300)}` };
    }
    const files = await countFiles(checkout);
    rec.files = { java: files.java, python: files.python };
    rec.pyFrameworks = files.pyFrameworks;
    rec.signals = files.signals;
    rec.families = files.families;
    const excluded = stackExclusion(pool, c.subpool, files);
    if (excluded) { rmSync(checkout, { recursive: true, force: true }); return { ...rec, status: 'excluded', reason: excluded }; }
    const out = join(resultsDir, `${slug(c.full_name)}.json`);
    rmSync(out, { force: true });
    const r = await scan(checkout, out);
    rec.scan = { exitCode: r.code, signal: r.signal, durationMs: r.ms };
    if (r.timedOut || (r.code !== 0 && r.code !== 1)) {
      rmSync(out, { force: true });
      rmSync(checkout, { recursive: true, force: true });
      return { ...rec, status: 'excluded', reason: r.timedOut ? '3f TIMEOUT (30 min)' : `3f scan exit ${r.code}`, stderr: r.stderr };
    }
    const report = JSON.parse(readFileSync(out, 'utf8'));
    rec.excludesMatch = JSON.stringify(report.excludes.applied) === JSON.stringify(files.applied);
    rec.critical = poolCritical(report, rules.language);
    // Checkouts are kept only where there is a CRITICAL of the pool's language (needed for the cards).
    if (rec.critical === 0) rmSync(checkout, { recursive: true, force: true });
    return { ...rec, status: 'included' };
  }

  while (!corpus.frozen) {
    const batch = corpus.batches.length + 1;
    const quota = batch === 1 ? rules.firstBatch : rules.nextBatch;
    let added = 0;
    const done = new Set(corpus.processed.map((p) => p.id));
    for (const c of list) {
      if (added >= quota || included().length >= rules.cap) break;
      if (done.has(c.id)) continue;
      if (c.exclusion) {
        corpus.processed.push({ pool, subpool: c.subpool, batch, rank: c.rank, full_name: c.full_name, id: c.id, status: 'excluded', reason: c.exclusion });
        save();
        continue;
      }
      const rec = await processCandidate(c, batch);
      corpus.processed.push(rec);
      save();
      if (rec.status === 'included') added++;
      console.log(`[${pool} batch ${batch}] ${c.subpool} #${c.rank} ${c.full_name}: ${rec.status}${rec.reason ? ` (${rec.reason})` : ''}${rec.status === 'included' ? `, ${rec.critical} critical` : ''}`);
    }
    const critical = included().reduce((n, p) => n + p.critical, 0);
    const d = stopDecision(rules, { critical, included: included().length, addedThisBatch: added, quota });
    corpus.batches.push({ batch, at: new Date().toISOString(), added, included: included().length, criticalSoFar: critical });
    if (d.frozen) { corpus.frozen = true; corpus.frozenReason = d.reason; }
    save();
    console.log(`${pool} batch ${batch}: ${included().length} included, ${critical} ${rules.language} CRITICAL so far`);
  }
  console.log(`${pool} corpus frozen: ${corpus.frozenReason}`);
}
