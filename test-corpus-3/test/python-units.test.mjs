// Runs the Python unit tests (test_units.py: evaluate, sample, cards) under `node --test`.
import test from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'child_process';
import { dirname } from 'path';
import { fileURLToPath } from 'url';

const HERE = dirname(fileURLToPath(import.meta.url));

test('python3 -m unittest test_units.py', () => {
  const r = spawnSync('python3', ['-I', '-m', 'unittest', 'discover', '-s', HERE, '-t', HERE, '-p', 'test_*.py'], { encoding: 'utf8', cwd: HERE, timeout: 120_000 });
  assert.equal(r.status, 0, `${r.stdout}\n${r.stderr}`);
});
