// Unit tests of the pure parts of the Node scripts: queries and subpools, ordering, exclusions
// (c2 included), signals, stack checks, stopping rule, the FROZEN.json guard and the tool identity
// checks (annotated tags, wheel/tgz hashes), the pre-registration hash and its verbatim appendix.
// No network, no scan; the git checks run on throwaway repositories.
import test from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'child_process';
import { createHash } from 'crypto';
import { mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'fs';
import { tmpdir } from 'os';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';
import { isJava, JAVA_SUBPOOLS, JAVA_T1, JAVA_T2, metadataExclusion, orderUnion, POOLS, PYTHON_B_TOPICS, queries, studyRepository, toyKeyword } from '../scripts/select.mjs';
import { countFiles, families, javaSignals, pyFrameworks } from '../scripts/count-files.mjs';
import { poolCandidates, poolCritical, POOL_RULES, stackExclusion, stopDecision } from '../scripts/run.mjs';
import { artifactProblems, frozenProblems, loadFrozen, observeTag, sha256File, sha512Integrity, tagProblems, unfilled } from '../scripts/lib.mjs';
import { namesInList, namesInText, normalize, SOURCES } from '../scripts/build-exclusions.mjs';

const TC4 = join(dirname(fileURLToPath(import.meta.url)), '..');
const ROOT = join(TC4, '..');
const read = (...p) => readFileSync(join(...p), 'utf8');
const sh = (cwd, ...args) => {
  const r = spawnSync('git', args, { cwd, encoding: 'utf8', env: { ...process.env, GIT_AUTHOR_NAME: 't', GIT_AUTHOR_EMAIL: 't@t', GIT_COMMITTER_NAME: 't', GIT_COMMITTER_EMAIL: 't@t' } });
  assert.equal(r.status, 0, r.stderr);
  return r.stdout.trim();
};

test('pre-registration: sha256 matches PREREGISTRATION.sha256', () => {
  const [hash, name] = read(TC4, 'PREREGISTRATION.sha256').trim().split(/\s+/);
  assert.equal(name, 'PREREGISTRATION.md');
  assert.equal(createHash('sha256').update(readFileSync(join(TC4, 'PREREGISTRATION.md'))).digest('hex'), hash);
});

test('pre-registration: the verbatim blocks equal REVIEW-CRITERIA.md v1 at bc0a3c6, byte for byte', () => {
  const v1 = spawnSync('git', ['show', 'bc0a3c6:REVIEW-CRITERIA.md'], { cwd: ROOT, encoding: 'utf8' });
  assert.equal(v1.status, 0, v1.stderr);
  assert.equal(createHash('sha256').update(v1.stdout).digest('hex'), 'c1ff60e770e586f3afbc99d8121f72cfab6f77ef0c4a92a2883e057f34e1b77d');
  const between = (a, b) => { const i = v1.stdout.indexOf(a); return v1.stdout.slice(i, v1.stdout.indexOf(b, i)).replace(/\n+$/, ''); };
  const want = {
    '§2.4 exclusion c2': between('**Exclusion c2 — study repositories.**', 'Dry run on the descriptions'),
    '§1': between('## 1. The three conditions', '## 2. Reachability'),
    '§5': between('## 5. Rule criteria v1', '## 6. Re-labelled'),
  };
  const blocks = [...read(TC4, 'PREREGISTRATION.md').matchAll(/<!-- BEGIN VERBATIM REVIEW-CRITERIA\.md v1 \(bc0a3c6\) (.+?) -->\n([\s\S]*?)\n<!-- END VERBATIM -->/g)];
  assert.deepEqual(blocks.map((m) => m[1]).sort(), Object.keys(want).sort());
  for (const [, key, text] of blocks) assert.equal(text, want[key], key);
});

test('queries: 75 Java (subpools A-D) and 7 Python, exact strings, cutoff = selection date - 183 days', () => {
  const q = queries('2026-11-02T08:00:00Z');
  assert.equal(q.cutoff, '2026-05-03');
  const Q = (lang) => `language:${lang} fork:false archived:false is:public size:100..1000000 pushed:>=2026-05-03`;
  assert.deepEqual(JAVA_T1, ['spring-boot', 'spring-kafka', 'kafka', 'apache-kafka', 'spring-webflux', 'webflux', 'project-reactor', 'reactor', 'reactive', 'spring-cloud', 'microservices']);
  assert.deepEqual(JAVA_T2, ['spring', 'spring-boot-3', 'spring-cloud-stream', 'kafka-streams', 'kafka-consumer', 'kafka-producer', 'event-driven',
    'event-driven-architecture', 'event-sourcing', 'cqrs', 'r2dbc', 'reactive-programming', 'reactive-streams', 'rsocket']);
  assert.deepEqual(q['java-A'], JAVA_T1.map((t) => `topic:${t} ${Q('Java')} stars:>=50`));
  assert.deepEqual(q['java-B'], JAVA_T2.map((t) => `topic:${t} ${Q('Java')} stars:>=50`));
  assert.deepEqual(q['java-C'], [...JAVA_T1, ...JAVA_T2].map((t) => `topic:${t} ${Q('Java')} stars:20..49`));
  assert.deepEqual(q['java-D'], [...JAVA_T1, ...JAVA_T2].map((t) => `topic:${t} ${Q('Java')} stars:10..19`));
  assert.equal(Object.keys(JAVA_SUBPOOLS).reduce((n, p) => n + q[p].length, 0), 75);
  assert.deepEqual(q['python-A'], [`topic:fastapi ${Q('Python')} stars:>=100`]);
  assert.deepEqual(q['python-B'], PYTHON_B_TOPICS.map((t) => `topic:${t} ${Q('Python')} stars:>=50`));
  assert.deepEqual(POOLS, ['java-A', 'java-B', 'java-C', 'java-D', 'python-A', 'python-B']);
});

test('queries: every pre-registered query string appears in PREREGISTRATION.md (topics and star bands)', () => {
  const pre = read(TC4, 'PREREGISTRATION.md');
  for (const t of [...JAVA_T1, ...JAVA_T2]) assert.match(pre, new RegExp(`\\b${t.replace(/[-]/g, '\\-')}\\b`), t);
  for (const s of ['stars:>=50', 'stars:20..49', 'stars:10..19', 'stars:>=100']) assert.ok(pre.includes(s), s);
  assert.ok(pre.includes('Q_JAVA = language:Java fork:false archived:false is:public size:100..1000000 pushed:>=<D>'));
  assert.ok(pre.includes('Q_PY   = language:Python fork:false archived:false is:public size:100..1000000 pushed:>=<D>'));
});

const repo = (id, full_name, stars, extra = {}) => ({ id, full_name, stargazers_count: stars, name: full_name.split('/')[1], owner: { login: full_name.split('/')[0] }, description: '', ...extra });

test('orderUnion: one entry per id, stars descending, ties by full_name (case-insensitive), queries matched', () => {
  const out = orderUnion([[repo(1, 'b/x', 10), repo(2, 'A/y', 10)], [repo(1, 'b/x', 10), repo(3, 'c/z', 99)]]);
  assert.deepEqual(out.map((o) => o.repo.id), [3, 2, 1]);
  assert.deepEqual(out.find((o) => o.repo.id === 1).matched, [0, 1]);
});

test('metadata exclusions: 3a by id or name, 3b own, 3c toy, 3c2 study, 3d overlap across subpools', () => {
  const earlier = { 'java-A': new Set([5]), 'java-B': new Set([8]), 'python-A': new Set([6]) };
  const ctx = { usedIds: new Set([1]), usedNames: new Set(['old/name']), earlier };
  assert.equal(metadataExclusion(repo(1, 'a/b', 1), 'java-A', ctx), '3a used before');
  assert.equal(metadataExclusion(repo(2, 'Old/Name', 1), 'java-A', ctx), '3a used before');
  assert.equal(metadataExclusion(repo(3, 'Joaquinriosheredia/x', 1), 'java-A', ctx), '3b own repository');
  assert.equal(metadataExclusion(repo(4, 'a/springDemo', 1), 'java-A', ctx), '3c toy keyword "demo"');
  assert.equal(metadataExclusion(repo(9, 'a/spring-cloud-study', 1), 'java-C', ctx), '3c2 study repository: name token "study"');
  assert.equal(metadataExclusion(repo(5, 'a/c', 1), 'java-C', ctx), '3d in the java-A pool: kept there only');
  assert.equal(metadataExclusion(repo(8, 'a/c', 1), 'python-A', ctx), '3d in the java-B pool: kept there only');
  assert.equal(metadataExclusion(repo(6, 'a/d', 1), 'python-B', ctx), '3d in the python-A pool: kept there only');
  assert.equal(metadataExclusion(repo(7, 'a/e', 1), 'python-B', ctx), null);
  assert.equal(toyKeyword({ name: 'KafkaStarterKit', description: '' }), 'starter');
  assert.ok(isJava('java-D') && !isJava('python-A'));
});

test('c2 study repositories: name, description and topic clauses, and the rejected variants', () => {
  const c2 = (name, description = '', topics = []) => studyRepository({ full_name: `o/${name}`, description, topics });
  assert.equal(c2('study'), 'name token "study"');
  assert.equal(c2('flink-learning'), 'name token "learning"');
  assert.equal(c2('Python-Studies'), 'name token "studies"');
  assert.equal(c2('kafka_notes'), 'name token "notes"');
  assert.equal(c2('deep-learning'), null); // the token before is in the exception list
  assert.equal(c2('machine.learning'), null);
  assert.equal(c2('StudyPilot'), null); // no camelCase split of the name
  assert.equal(c2('OpenStudy'), null);
  assert.equal(c2('study-app'), null); // only the last token
  assert.equal(c2('x', 'My Spring study notes'), 'description "study notes"');
  assert.equal(c2('x', 'A demo for-learning purposes'), 'description "for learning"');
  assert.equal(c2('x', 'For LearningPurposes only'), 'description "for learning"'); // camelCase split in the description
  assert.equal(c2('x', 'Spring Cloud 学习笔记'), 'description "学习笔记"');
  assert.equal(c2('x', '一个练手项目'), 'description "练手"');
  assert.equal(c2('x', '仅供学习使用'), null); // rejected variant (a common disclaimer)
  assert.equal(c2('yu-ai-learn', 'learn AI'), null); // a bare "learn" is not a clause
  assert.equal(c2('x', 'notes on learning'), null);
  assert.equal(c2('x', '', ['Study-Notes']), 'topic "study-notes"');
  assert.equal(c2('x', '', ['notes', 'java']), 'topic "notes"');
  assert.equal(c2('x', '', ['learning']), null);
});

test('c2 dry run of REVIEW-CRITERIA v1 §2.4: on the test-corpus-2 and test-corpus-3 candidates it hits exactly the five study repositories', () => {
  const hits = new Set();
  for (const c of ['2', '3']) {
    const pools = JSON.parse(read(ROOT, `test-corpus-${c}`, 'candidates.json')).pools;
    for (const list of Object.values(pools)) for (const r of list) if (studyRepository(r)) hits.add(r.full_name);
  }
  assert.deepEqual([...hits].sort((a, b) => a.toLowerCase().localeCompare(b.toLowerCase())),
    ['bage2014/study', 'kilerhg/Python-Studies', 'moshowgame/spring-cloud-study', 'zeroaihub/Java-Agent-Study', 'zhisheng17/flink-learning']);
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
  assert.equal(stackExclusion('java', 'java-C', java), null);
  assert.match(stackExclusion('java', 'java-A', { ...java, families: [] }), /^3g no code signal/);
  assert.match(stackExclusion('java', 'java-A', { ...java, java: 19 }), /^3e stack/);
  assert.match(stackExclusion('java', 'java-D', { ...java, springBoot: false }), /^3e stack/);
  const py = { python: 20, pyFrameworks: ['aiohttp'] };
  assert.match(stackExclusion('python', 'python-A', py), /^3e stack: fastapi import not found/);
  assert.equal(stackExclusion('python', 'python-B', py), null);
  assert.equal(stackExclusion('python', 'python-A', { ...py, pyFrameworks: ['fastapi'] }), null);
  assert.match(stackExclusion('python', 'python-B', { ...py, python: 5 }), /^3e stack/);
});

test('pool candidates: Java subpools A, B, C, D in order; Python A then B', () => {
  const pools = Object.fromEntries(POOLS.map((p, i) => [p, [{ id: i, rank: 1 }]]));
  assert.deepEqual(poolCandidates({ pools }, 'java').map((c) => c.subpool), ['java-A', 'java-B', 'java-C', 'java-D']);
  assert.deepEqual(poolCandidates({ pools }, 'python').map((c) => c.subpool), ['python-A', 'python-B']);
});

test('stopping rule per pool: target, Java cap 500, exhaustion; never by verdicts', () => {
  assert.deepEqual(POOL_RULES.java, { language: 'java', firstBatch: 25, nextBatch: 25, cap: 500, target: 50 });
  assert.deepEqual(POOL_RULES.python, { language: 'python', firstBatch: 20, nextBatch: 10, cap: 150, target: 100 });
  assert.equal(stopDecision(POOL_RULES.java, { critical: 50, included: 25, addedThisBatch: 25, quota: 25 }).frozen, true);
  assert.equal(stopDecision(POOL_RULES.java, { critical: 49, included: 300, addedThisBatch: 25, quota: 25 }).frozen, false);
  assert.equal(stopDecision(POOL_RULES.java, { critical: 49, included: 475, addedThisBatch: 25, quota: 25 }).frozen, false);
  const capped = stopDecision(POOL_RULES.java, { critical: 49, included: 500, addedThisBatch: 25, quota: 25 });
  assert.match(capped.reason, /cap of 500 .* 49 java CRITICAL < 50: criterion 1 NOT MET for java/);
  assert.match(stopDecision(POOL_RULES.python, { critical: 80, included: 60, addedThisBatch: 3, quota: 10 }).reason, /candidates exhausted .*NOT MET for python/);
  const report = { findings: [{ severity: 'critical', language: 'java' }, { severity: 'critical', language: 'python' }, { severity: 'warning', language: 'java' }] };
  assert.equal(poolCritical(report, 'java'), 1);
});

const FILLED = {
  pyvibePro: { tag: 'v0.16.0', commit: 'a'.repeat(40), version: '0.16.0', wheel: 'python_vibe_guard-0.16.0-py3-none-any.whl', sha256: 'b'.repeat(64) },
  javaVibeGuardPro: { tag: 'v3.1.0', commit: 'c'.repeat(40), version: '3.1.0', tgz: 'java-vibe-guard-3.1.0.tgz', sha256: 'd'.repeat(64), integrity: 'sha512-AAAA==' },
  vibeGuardScan: { tag: 'v0.4.0', commit: 'e'.repeat(40), version: '0.4.0', versionLine: 'vibe-guard 0.4.0 (...)' },
};

test('FROZEN.json guard: refuses TO-FILL values; a filled one needs full SHAs, tags, hashes and an npm integrity', () => {
  assert.deepEqual(unfilled({ a: { b: 'TO-FILL: x' }, c: 'ok' }), ['a.b']);
  const frozen = JSON.parse(read(TC4, 'FROZEN.json'));
  const missing = unfilled(frozen);
  if (missing.length) {
    // Until Joaquín tags (PREREGISTRATION.md, "Tools under test") every identity is TO-FILL and nothing can run.
    assert.deepEqual(missing, ['pyvibePro.tag', 'pyvibePro.commit', 'pyvibePro.version', 'pyvibePro.wheel', 'pyvibePro.sha256',
      'javaVibeGuardPro.tag', 'javaVibeGuardPro.commit', 'javaVibeGuardPro.version', 'javaVibeGuardPro.tgz', 'javaVibeGuardPro.sha256', 'javaVibeGuardPro.integrity',
      'vibeGuardScan.tag', 'vibeGuardScan.commit', 'vibeGuardScan.version', 'vibeGuardScan.versionLine']);
    assert.throws(() => loadFrozen(), /FROZEN.json not filled: pyvibePro.tag/);
  } else {
    assert.deepEqual(frozenProblems(frozen), []);
    assert.equal(loadFrozen().vibeGuardScan.commit, frozen.vibeGuardScan.commit);
  }
  assert.deepEqual(frozenProblems(FILLED), []);
  const bad = structuredClone(FILLED);
  bad.vibeGuardScan.commit = 'abc1234';
  bad.pyvibePro.sha256 = 'x';
  bad.javaVibeGuardPro.integrity = 'sha1-zz';
  bad.javaVibeGuardPro.tgz = 'jvg.zip';
  assert.deepEqual(frozenProblems(bad), ['vibeGuardScan.commit must be a full 40-character SHA', 'pyvibePro.sha256 must be 64 hex characters',
    'javaVibeGuardPro.tgz must be a .tgz file name', 'javaVibeGuardPro.integrity must be an npm sha512 integrity']);
});

test('tags: annotated and at the frozen commit; the wrapper checkout at that commit with no tracked change', () => {
  const dir = mkdtempSync(join(tmpdir(), 'tc4-tag-'));
  try {
    sh(dir, 'init', '-q');
    writeFileSync(join(dir, 'f'), '1');
    sh(dir, 'add', 'f');
    sh(dir, 'commit', '-q', '-m', 'one');
    const c1 = sh(dir, 'rev-parse', 'HEAD');
    sh(dir, 'tag', '-a', 'v1', '-m', 'v1');
    sh(dir, 'tag', 'light');
    writeFileSync(join(dir, 'f'), '2');
    sh(dir, 'commit', '-q', '-am', 'two');
    const want = { tag: 'v1', commit: c1 };
    assert.deepEqual(observeTag(dir, 'v1'), { type: 'tag', commit: c1, head: sh(dir, 'rev-parse', 'HEAD'), clean: true });
    assert.deepEqual(tagProblems('x', want, observeTag(dir, 'v1')), []);
    assert.match(tagProblems('x', want, observeTag(dir, 'v1'), { atHead: true }).join(), /checkout is at/);
    sh(dir, 'checkout', '-q', 'v1');
    assert.deepEqual(tagProblems('x', want, observeTag(dir, 'v1'), { atHead: true }), []);
    writeFileSync(join(dir, 'f'), 'dirty');
    assert.deepEqual(tagProblems('x', want, observeTag(dir, 'v1'), { atHead: true }), ['x: checkout has uncommitted changes']);
    assert.deepEqual(tagProblems('x', { tag: 'light', commit: c1 }, observeTag(dir, 'light')), ['x: tag light is a commit, not an annotated tag']);
    assert.match(tagProblems('x', { tag: 'nope', commit: c1 }, observeTag(dir, 'nope')).join(), /tag nope is missing.*points to null/);
    assert.match(tagProblems('x', { tag: 'v1', commit: 'f'.repeat(40) }, observeTag(dir, 'v1')).join(), /points to/);
  } finally { rmSync(dir, { recursive: true, force: true }); }
});

test('artifacts: the wheel and the .tgz by name and hash; the wrapper lockfile and the installed version', () => {
  const dir = mkdtempSync(join(tmpdir(), 'tc4-art-'));
  try {
    const whl = join(dir, FILLED.pyvibePro.wheel);
    const tgz = join(dir, FILLED.javaVibeGuardPro.tgz);
    writeFileSync(whl, 'wheel');
    writeFileSync(tgz, 'tarball');
    assert.equal(sha256File(whl), createHash('sha256').update('wheel').digest('hex'));
    assert.equal(sha512Integrity(tgz), `sha512-${createHash('sha512').update('tarball').digest('base64')}`);
    const frozen = structuredClone(FILLED);
    frozen.pyvibePro.sha256 = sha256File(whl);
    frozen.javaVibeGuardPro.sha256 = sha256File(tgz);
    frozen.javaVibeGuardPro.integrity = sha512Integrity(tgz);
    const ok = {
      wheel: { name: FILLED.pyvibePro.wheel, sha256: sha256File(whl) },
      tgz: { name: FILLED.javaVibeGuardPro.tgz, sha256: sha256File(tgz), integrity: sha512Integrity(tgz) },
      lockIntegrity: sha512Integrity(tgz), installedVersion: '3.1.0',
    };
    assert.deepEqual(artifactProblems(frozen, ok), []);
    const bad = artifactProblems(frozen, { ...ok, wheel: { ...ok.wheel, sha256: '0'.repeat(64) }, lockIntegrity: 'sha512-other', installedVersion: '3.0.0' });
    assert.equal(bad.length, 3);
    assert.match(bad.join('\n'), /wheel sha256.*\n.*package-lock.json pins.*\n.*installed java-vibe-guard is 3.0.0/);
  } finally { rmSync(dir, { recursive: true, force: true }); }
});

test('exclusion sources: the seven repositories, pinned by full SHA; evaluation at the merged pre-registration', () => {
  assert.deepEqual(Object.keys(SOURCES), ['pyvibe-pro', 'java-vibe-guard-pro', 'python-vibe-guard', 'java-vibe-guard', 'vibe-guard', 'vibe-guard-scan', 'vibe-guard-evaluation']);
  for (const [k, v] of Object.entries(SOURCES)) assert.match(v.commit, /^[0-9a-f]{40}$/, k);
  assert.equal(SOURCES['pyvibe-pro'].commit, 'ec317f9c1c4fd0d269913079413c561b483e925d');
  assert.equal(SOURCES['java-vibe-guard-pro'].commit, '18e585cbed5a689ba3191beb689dccc5954bca98');
  const r = spawnSync('git', ['cat-file', '-e', `${SOURCES['vibe-guard-evaluation'].commit}:test-corpus-4/PREREGISTRATION.md`], { cwd: ROOT });
  assert.equal(r.status, 0, 'the pinned evaluation commit holds the pre-registration');
  assert.ok(SOURCES['vibe-guard-evaluation'].text.some((re) => re.test('calibration-v1-2026-10-28/README.md')));
  assert.ok(SOURCES['vibe-guard-evaluation'].text.some((re) => re.test('test-corpus-4/PREREGISTRATION.md')));
  assert.ok(!SOURCES['vibe-guard-evaluation'].text.some((re) => re.test('test-corpus-3/cards/J001.md')));
});

test('exclusions: names from lists and URLs; own repositories dropped; the committed list covers test-corpus-1, 2 and 3', () => {
  assert.deepEqual(namesInList('x.json', { repositories: [{ name: 'a/b' }, { name: 'not a repo' }], processed: [{ full_name: 'c/d' }], entries: [{ repo: 'e/f' }] }).sort(), ['a/b', 'c/d', 'e/f']);
  assert.deepEqual(namesInText('see https://github.com/foo/bar.git and github.com/x/y.'), ['foo/bar.git', 'x/y.']);
  assert.equal(normalize('foo/bar.git'), 'foo/bar');
  assert.equal(normalize('Joaquinriosheredia/java-vibe-guard'), null);
  const ex = JSON.parse(read(TC4, 'exclusions.json'));
  assert.equal(ex.count, ex.repositories.length);
  const names = new Set(ex.repositories.map((r) => r.name.toLowerCase()));
  const tc3ex = JSON.parse(read(ROOT, 'test-corpus-3', 'exclusions.json')).repositories;
  assert.ok(tc3ex.length === 1277 && tc3ex.every((r) => names.has(r.name.toLowerCase())));
  const tc3 = ['java', 'python'].flatMap((p) => JSON.parse(read(ROOT, 'test-corpus-3', `corpus-${p}.json`)).processed);
  assert.ok(tc3.length === 877 && tc3.every((p) => names.has(p.full_name.toLowerCase())));
  const tc2 = ['java', 'python'].flatMap((p) => JSON.parse(read(ROOT, 'test-corpus-2', `corpus-${p}.json`)).processed);
  assert.ok(tc2.length === 529 && tc2.every((p) => names.has(p.full_name.toLowerCase())));
  const tc1 = JSON.parse(read(ROOT, 'test-corpus-1', 'corpus.json')).processed;
  assert.ok(tc1.length === 204 && tc1.every((p) => names.has(p.full_name.toLowerCase())));
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
