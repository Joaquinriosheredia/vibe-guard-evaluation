// Unit tests of the pure parts of the Node scripts: queries, ordering, exclusions, signals,
// stack checks, stopping rule and the FROZEN.json guard. No network, no scan.
import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'fs';
import { tmpdir } from 'os';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';
import { metadataExclusion, orderUnion, queries, toyKeyword, JAVA_TOPICS, PYTHON_B_TOPICS } from '../scripts/select.mjs';
import { countFiles, families, javaSignals, pyFrameworks } from '../scripts/count-files.mjs';
import { poolCritical, POOL_RULES, stackExclusion, stopDecision } from '../scripts/run.mjs';
import { loadFrozen, unfilled } from '../scripts/lib.mjs';
import { namesInList, namesInText, normalize } from '../scripts/build-exclusions.mjs';

const TC2 = join(dirname(fileURLToPath(import.meta.url)), '..');

test('queries: exact strings, cutoff = selection date - 183 days', () => {
  const q = queries('2026-10-20T08:00:00Z');
  assert.equal(q.cutoff, '2026-04-20');
  const tail = (s) => `fork:false archived:false is:public stars:>=${s} size:100..1000000 pushed:>=2026-04-20`;
  assert.deepEqual(q['python-A'], [`topic:fastapi language:Python ${tail(100)}`]);
  assert.deepEqual(q.java, JAVA_TOPICS.map((t) => `topic:${t} language:Java ${tail(50)}`));
  assert.deepEqual(q['python-B'], PYTHON_B_TOPICS.map((t) => `topic:${t} language:Python ${tail(50)}`));
  assert.equal(q.java.length, 11);
  assert.deepEqual(PYTHON_B_TOPICS, ['fastapi', 'aiohttp', 'starlette', 'litestar', 'sanic', 'quart']);
});

const repo = (id, full_name, stars, extra = {}) => ({ id, full_name, stargazers_count: stars, name: full_name.split('/')[1], owner: { login: full_name.split('/')[0] }, description: '', ...extra });

test('orderUnion: one entry per id, stars descending, ties by full_name (case-insensitive), queries matched', () => {
  const out = orderUnion([[repo(1, 'b/x', 10), repo(2, 'A/y', 10)], [repo(1, 'b/x', 10), repo(3, 'c/z', 99)]]);
  assert.deepEqual(out.map((o) => o.repo.id), [3, 2, 1]);
  assert.deepEqual(out.find((o) => o.repo.id === 1).matched, [0, 1]);
});

test('metadata exclusions: 3a by id or name, 3b own, 3c toy, 3d overlap', () => {
  const ctx = { usedIds: new Set([1]), usedNames: new Set(['old/name']), javaIds: new Set([5]), pythonAIds: new Set([6]) };
  assert.equal(metadataExclusion(repo(1, 'a/b', 1), 'java', ctx), '3a used before');
  assert.equal(metadataExclusion(repo(2, 'Old/Name', 1), 'java', ctx), '3a used before');
  assert.equal(metadataExclusion(repo(3, 'Joaquinriosheredia/x', 1), 'java', ctx), '3b own repository');
  assert.equal(metadataExclusion(repo(4, 'a/springDemo', 1), 'java', ctx), '3c toy keyword "demo"');
  assert.equal(metadataExclusion(repo(5, 'a/c', 1), 'python-A', ctx), '3d in the java pool: kept there only');
  assert.equal(metadataExclusion(repo(6, 'a/d', 1), 'python-B', ctx), '3d in the python-A pool: kept there only');
  assert.equal(metadataExclusion(repo(7, 'a/e', 1), 'python-B', ctx), null);
  assert.equal(toyKeyword({ name: 'KafkaStarterKit', description: '' }), 'starter');
});

test('Java signals (3g): literal annotations and imports; ASYNC needs @EnableAsync and @Async', () => {
  assert.deepEqual(javaSignals('@EnableAsync\nclass A {}'), { enableAsync: true, async: false, kafka: false, reactor: false });
  assert.equal(javaSignals('@AsyncResult x').async, false);
  assert.equal(javaSignals('  @Async("pool") void f(){}').async, true);
  assert.equal(javaSignals('import org.springframework.kafka.core.KafkaTemplate;').kafka, true);
  assert.equal(javaSignals('@KafkaListener(topics="t")').kafka, true);
  assert.equal(javaSignals('import org.apache.kafka.clients.producer.Producer;').kafka, true);
  assert.equal(javaSignals('import org.apache.kafka.clients.consumer.KafkaConsumer;').kafka, false);
  assert.equal(javaSignals('import reactor.core.publisher.Mono;').reactor, true);
  assert.equal(javaSignals('import reactor.core.publisher.*;').reactor, true);
  assert.equal(javaSignals('import reactor.core.scheduler.Schedulers;').reactor, false);
  assert.deepEqual(families({ enableAsync: true, async: false, kafka: true, reactor: false }), ['KAFKA']);
  assert.deepEqual(families({ enableAsync: true, async: true, kafka: false, reactor: true }), ['ASYNC', 'REACTOR']);
});

test('Python framework imports (3e)', () => {
  assert.deepEqual(pyFrameworks('from fastapi import FastAPI\nimport aiohttp.web\n  from quart import Quart\nfrom fastapi_utils import x'), ['aiohttp', 'fastapi', 'quart']);
  assert.deepEqual(pyFrameworks('# from fastapi import x is in a comment? no: it starts with #'), []);
});

test('stack checks (3e, 3g)', () => {
  const java = { springBoot: true, java: 20, families: ['KAFKA'] };
  assert.equal(stackExclusion('java', 'java', java), null);
  assert.match(stackExclusion('java', 'java', { ...java, families: [] }), /^3g no code signal/);
  assert.match(stackExclusion('java', 'java', { ...java, java: 19 }), /^3e stack/);
  assert.match(stackExclusion('java', 'java', { ...java, springBoot: false }), /^3e stack/);
  const py = { python: 20, pyFrameworks: ['aiohttp'] };
  assert.match(stackExclusion('python', 'python-A', py), /^3e stack: fastapi import not found/);
  assert.equal(stackExclusion('python', 'python-B', py), null);
  assert.equal(stackExclusion('python', 'python-A', { ...py, pyFrameworks: ['fastapi'] }), null);
  assert.match(stackExclusion('python', 'python-B', { ...py, python: 5 }), /^3e stack/);
});

test('stopping rule per pool: target, cap, exhaustion; never by verdicts', () => {
  assert.deepEqual(POOL_RULES.java, { language: 'java', firstBatch: 25, nextBatch: 25, cap: 300, target: 50 });
  assert.deepEqual(POOL_RULES.python, { language: 'python', firstBatch: 20, nextBatch: 10, cap: 150, target: 100 });
  assert.equal(stopDecision(POOL_RULES.java, { critical: 50, included: 25, addedThisBatch: 25, quota: 25 }).frozen, true);
  assert.equal(stopDecision(POOL_RULES.java, { critical: 49, included: 275, addedThisBatch: 25, quota: 25 }).frozen, false);
  const capped = stopDecision(POOL_RULES.java, { critical: 49, included: 300, addedThisBatch: 25, quota: 25 });
  assert.match(capped.reason, /cap of 300 .* 49 java CRITICAL < 50: criterion 1 NOT MET for java/);
  assert.match(stopDecision(POOL_RULES.python, { critical: 80, included: 60, addedThisBatch: 3, quota: 10 }).reason, /candidates exhausted .*NOT MET for python/);
  const report = { findings: [{ severity: 'critical', language: 'java' }, { severity: 'critical', language: 'python' }, { severity: 'warning', language: 'java' }] };
  assert.equal(poolCritical(report, 'java'), 1);
});

test('FROZEN.json guard: refuses TO-FILL values, otherwise needs a full SHA and the frozen versions', () => {
  assert.deepEqual(unfilled({ a: { b: 'TO-FILL: x' }, c: 'ok' }), ['a.b']);
  const frozen = JSON.parse(readFileSync(join(TC2, 'FROZEN.json'), 'utf8'));
  assert.equal(frozen.pyvibe.sha256, '7847e9577bca8eb74e77d4079ecf437232ef5c9d187e3c75cf3ce67084caf254');
  assert.equal(frozen.javaVibeGuard.integrity, 'sha512-YawOnqjT9X48nqWwjwbl31xecv6jDoqQAUQD0Ohpy4aI1iiReO/QYXm+KKQJeyi0yGvhKuiAhwAuh6b3UubEyQ==');
  assert.equal(frozen.vibeGuardScan.versionLine, 'vibe-guard 0.2.0 (java-vibe-guard 2.4.0; pyvibe 0.14.0)');
  if (unfilled(frozen).length) assert.throws(() => loadFrozen(), /FROZEN.json not filled: vibeGuardScan.commit/);
  else assert.match(loadFrozen().vibeGuardScan.commit, /^[0-9a-f]{40}$/);
});

test('exclusions: names from lists and URLs; own repositories dropped; the committed list covers test-corpus-1', () => {
  assert.deepEqual(namesInList('x.json', { repositories: [{ name: 'a/b' }, { name: 'not a repo' }], processed: [{ full_name: 'c/d' }], entries: [{ repo: 'e/f' }] }).sort(), ['a/b', 'c/d', 'e/f']);
  assert.deepEqual(namesInText('see https://github.com/foo/bar.git and github.com/x/y.'), ['foo/bar.git', 'x/y.']);
  assert.equal(normalize('foo/bar.git'), 'foo/bar');
  assert.equal(normalize('Joaquinriosheredia/java-vibe-guard'), null);
  const ex = JSON.parse(readFileSync(join(TC2, 'exclusions.json'), 'utf8'));
  assert.equal(ex.count, ex.repositories.length);
  const names = new Set(ex.repositories.map((r) => r.name.toLowerCase()));
  const tc1 = JSON.parse(readFileSync(join(TC2, '..', 'test-corpus-1', 'corpus.json'), 'utf8')).processed;
  assert.ok(tc1.length === 204 && tc1.every((p) => names.has(p.full_name.toLowerCase())));
  const tc1ex = JSON.parse(readFileSync(join(TC2, '..', 'test-corpus-1', 'exclusions.json'), 'utf8')).repositories;
  assert.ok(tc1ex.every((r) => names.has(r.name.toLowerCase())));
  for (const n of ['halo-dev/halo', 'yunaiv/ruoyi-vue-pro', 'open-webui/open-webui', 'nysenate/openlegislation']) assert.ok(names.has(n), n);
});

test('countFiles: counts, frameworks and signals outside the wrapper\'s exclusions (stub detect.js)', async () => {
  const vgs = mkdtempSync(join(tmpdir(), 'vgs-'));
  mkdirSync(join(vgs, 'src'));
  writeFileSync(join(vgs, 'src', 'detect.js'), `export const SCAN_DEFAULT_EXCLUDES = ['tests'];
export const JAVA_DEFAULT_EXCLUDES = ['target']; export const PYVIBE_DEFAULT_EXCLUDES = ['.venv'];
export function resolveDefaultExcludes(root) { return [{ path: 'tests', pattern: 'tests', files: 1 }]; }\n`);
  const root = mkdtempSync(join(tmpdir(), 'repo-'));
  for (const d of ['src', 'tests', 'target']) mkdirSync(join(root, d));
  writeFileSync(join(root, 'pom.xml'), '<artifactId>spring-boot-starter</artifactId>');
  writeFileSync(join(root, 'src', 'A.java'), '@EnableAsync class A { @Async void f(){} }');
  writeFileSync(join(root, 'tests', 'B.java'), 'import reactor.core.publisher.Mono;');
  writeFileSync(join(root, 'target', 'C.java'), '@KafkaListener');
  writeFileSync(join(root, 'src', 'app.py'), 'from fastapi import FastAPI');
  process.env.VGS = vgs;
  const out = await countFiles(root);
  delete process.env.VGS;
  assert.equal(out.java, 1);
  assert.equal(out.python, 1);
  assert.equal(out.springBoot, true);
  assert.deepEqual(out.pyFrameworks, ['fastapi']);
  assert.deepEqual(out.families, ['ASYNC']);
  rmSync(vgs, { recursive: true, force: true });
  rmSync(root, { recursive: true, force: true });
});
