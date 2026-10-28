// Imports one module with network, child processes and file writes intercepted, and prints
// every intercepted call as JSON. Used by import-is-inert.test.mjs, one process per module.
import cp from 'child_process';
import fs from 'fs';
import http from 'http';
import https from 'https';
import net from 'net';
import { syncBuiltinESMExports } from 'module';
import { pathToFileURL } from 'url';

const calls = [];
const trap = (obj, names, kind) => {
  for (const n of names) {
    if (typeof obj[n] !== 'function') continue;
    obj[n] = (...args) => { calls.push(`${kind}:${n}(${String(args[0]).slice(0, 80)})`); throw new Error(`blocked ${kind}:${n}`); };
  }
};
trap(cp, ['spawn', 'spawnSync', 'exec', 'execSync', 'execFile', 'execFileSync', 'fork'], 'process');
trap(http, ['request', 'get'], 'network');
trap(https, ['request', 'get'], 'network');
trap(net, ['connect', 'createConnection'], 'network');
trap(fs, ['writeFileSync', 'writeFile', 'appendFileSync', 'appendFile', 'mkdirSync', 'mkdir', 'rmSync', 'rm', 'unlinkSync', 'unlink',
  'renameSync', 'rename', 'copyFileSync', 'copyFile', 'createWriteStream', 'rmdirSync', 'symlinkSync', 'truncateSync'], 'write');
trap(fs.promises, ['writeFile', 'appendFile', 'mkdir', 'rm', 'unlink', 'rename', 'copyFile'], 'write');
// open/openSync: only write modes count (the module loader opens files to read them).
const writeMode = (flags) => typeof flags === 'number' ? (flags & (fs.constants.O_WRONLY | fs.constants.O_RDWR)) !== 0 : /[wa+]/.test(flags ?? 'r');
for (const [obj, n] of [[fs, 'openSync'], [fs, 'open'], [fs.promises, 'open']]) {
  const real = obj[n];
  obj[n] = (path, flags, ...rest) => {
    if (writeMode(flags)) { calls.push(`write:${n}(${String(path).slice(0, 80)}, ${flags})`); throw new Error(`blocked write:${n}`); }
    return real.call(obj, path, flags, ...rest);
  };
}
globalThis.fetch = (...args) => { calls.push(`network:fetch(${String(args[0]).slice(0, 80)})`); throw new Error('blocked fetch'); };
syncBuiltinESMExports();

let error = null;
try { await import(pathToFileURL(process.argv[2]).href); } catch (e) { error = String(e.message ?? e).slice(0, 300); }
await new Promise((r) => setTimeout(r, 200)); // let any un-awaited promise fire
console.log(JSON.stringify({ calls, error }));
