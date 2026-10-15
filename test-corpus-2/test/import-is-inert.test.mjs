// Importing any evaluation script must not touch the network, start a process or write a file
// (test-corpus-1 DEVIATIONS.md §1: importing select.mjs once ran the search). Every script is
// imported in its own process with those calls intercepted; positive controls prove the
// interception works. Run: node --test test-corpus-2/test/
import test from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'child_process';
import { readdirSync } from 'fs';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';

const HERE = dirname(fileURLToPath(import.meta.url));
const SCRIPTS = join(HERE, '..', 'scripts');
const env = { PATH: process.env.PATH, HOME: process.env.HOME }; // no VGS, PYVIBE, WORK or token

function probe(file) {
  const [cmd, args] = file.endsWith('.py')
    ? ['python3', ['-I', join(HERE, 'inert_harness.py'), file]]
    : [process.execPath, [join(HERE, 'inert-harness.mjs'), file]];
  const r = spawnSync(cmd, args, { encoding: 'utf8', env, cwd: HERE, timeout: 60_000 });
  assert.equal(r.status, 0, r.stderr);
  return JSON.parse(r.stdout.trim().split('\n').pop());
}

const scripts = readdirSync(SCRIPTS).filter((f) => f.endsWith('.mjs') || f.endsWith('.py'));

test('there are scripts to check (build-exclusions, cards, count-files, evaluate, lib, review_sheet, run, sample, select)', () => {
  assert.deepEqual(scripts.sort(), ['build-exclusions.mjs', 'cards.py', 'count-files.mjs', 'evaluate.py', 'lib.mjs', 'review_sheet.py', 'run.mjs', 'sample.py', 'select.mjs']);
});

for (const f of scripts) {
  test(`importing scripts/${f} makes no network call, starts no process and writes no file`, () => {
    const { calls, error } = probe(join(SCRIPTS, f));
    assert.deepEqual(calls, []);
    assert.equal(error, null);
  });
}

for (const [f, kind] of [['bad-network.mjs', 'network'], ['bad-write.mjs', 'write'], ['bad_network.py', 'network'], ['bad_write.py', 'write']]) {
  test(`positive control: ${f} is caught (${kind})`, () => {
    const { calls } = probe(join(HERE, 'fixtures', f));
    assert.ok(calls.some((c) => c.startsWith(`${kind}:`)), JSON.stringify(calls));
  });
}
