// Shared helpers: GitHub REST calls (token from `gh auth token`), JSON files, git, and the
// frozen tool identities (FROZEN.json: annotated tags, commits, wheel/tgz hashes). Importing this
// module does nothing.
import { execFileSync, spawnSync } from 'child_process';
import { createHash } from 'crypto';
import { existsSync, readFileSync, writeFileSync } from 'fs';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';

export const DIR = join(dirname(fileURLToPath(import.meta.url)), '..');

let token;
function auth() {
  token ??= process.env.GITHUB_TOKEN || execFileSync('gh', ['auth', 'token'], { encoding: 'utf8' }).trim();
  return token;
}

export const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

/** GET https://api.github.com<path>. Returns { status, body }. Retries on rate limits and 5xx. */
export async function gh(path) {
  for (let attempt = 0; ; attempt++) {
    const res = await fetch(`https://api.github.com${path}`, {
      headers: { Authorization: `Bearer ${auth()}`, Accept: 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28' },
    });
    const remaining = Number(res.headers.get('x-ratelimit-remaining'));
    if ((res.status === 403 || res.status === 429) && attempt < 8) {
      const reset = Number(res.headers.get('x-ratelimit-reset')) * 1000;
      const wait = Number.isFinite(reset) && remaining === 0 ? Math.max(reset - Date.now(), 1000) + 1000 : 30_000 * (attempt + 1);
      await sleep(wait);
      continue;
    }
    if (res.status >= 500 && attempt < 5) { await sleep(5000 * (attempt + 1)); continue; }
    const text = await res.text();
    return { status: res.status, body: text ? JSON.parse(text) : null };
  }
}

export const readJson = (p, fallback) => (existsSync(p) ? JSON.parse(readFileSync(p, 'utf8')) : fallback);
export const writeJson = (p, v) => writeFileSync(p, `${JSON.stringify(v, null, 2)}\n`);

export function git(args, opts = {}) {
  const r = spawnSync('git', args, { encoding: 'utf8', maxBuffer: 1 << 28, ...opts });
  if (r.status !== 0) throw new Error(`git ${args.join(' ')}: ${r.stderr.trim()}`);
  return r.stdout;
}

export const slug = (fullName) => fullName.replace('/', '__');

/** Every string value of FROZEN.json that still starts with TO-FILL (empty when frozen). */
export function unfilled(frozen) {
  const out = [];
  const visit = (x, path) => {
    if (typeof x === 'string') { if (x.startsWith('TO-FILL')) out.push(path); }
    else if (x && typeof x === 'object') for (const [k, v] of Object.entries(x)) visit(v, path ? `${path}.${k}` : k);
  };
  visit(frozen, '');
  return out;
}

const SHA1 = /^[0-9a-f]{40}$/;
const SHA256 = /^[0-9a-f]{64}$/;

/** Format problems of a filled FROZEN.json (PREREGISTRATION.md, "Tools under test"). */
export function frozenProblems(frozen) {
  const out = [];
  for (const k of ['pyvibePro', 'javaVibeGuardPro', 'vibeGuardScan']) {
    if (!SHA1.test(frozen[k]?.commit ?? '')) out.push(`${k}.commit must be a full 40-character SHA`);
    if (!(frozen[k]?.tag ?? '').trim()) out.push(`${k}.tag missing`);
  }
  if (!SHA256.test(frozen.pyvibePro?.sha256 ?? '')) out.push('pyvibePro.sha256 must be 64 hex characters');
  if (!/\.whl$/.test(frozen.pyvibePro?.wheel ?? '')) out.push('pyvibePro.wheel must be a .whl file name');
  if (!SHA256.test(frozen.javaVibeGuardPro?.sha256 ?? '')) out.push('javaVibeGuardPro.sha256 must be 64 hex characters');
  if (!/\.tgz$/.test(frozen.javaVibeGuardPro?.tgz ?? '')) out.push('javaVibeGuardPro.tgz must be a .tgz file name');
  if (!/^sha512-[A-Za-z0-9+/]+=*$/.test(frozen.javaVibeGuardPro?.integrity ?? '')) out.push('javaVibeGuardPro.integrity must be an npm sha512 integrity');
  return out;
}

/** FROZEN.json, refusing placeholders and malformed identities. */
export function loadFrozen() {
  const frozen = JSON.parse(readFileSync(join(DIR, 'FROZEN.json'), 'utf8'));
  const missing = unfilled(frozen);
  if (missing.length) throw new Error(`FROZEN.json not filled: ${missing.join(', ')} (PREREGISTRATION.md, "Tools under test")`);
  const bad = frozenProblems(frozen);
  if (bad.length) throw new Error(`FROZEN.json: ${bad.join('; ')}`);
  return frozen;
}

export const sha256File = (p) => createHash('sha256').update(readFileSync(p)).digest('hex');
export const sha512Integrity = (p) => `sha512-${createHash('sha512').update(readFileSync(p)).digest('base64')}`;

/** What one checkout says about a tag: { type, commit, head, clean } (git only, no network). */
export function observeTag(cwd, tag) {
  const type = spawnSync('git', ['cat-file', '-t', `refs/tags/${tag}`], { cwd, encoding: 'utf8' }).stdout.trim() || null;
  const commit = spawnSync('git', ['rev-parse', '--verify', '--quiet', `refs/tags/${tag}^{commit}`], { cwd, encoding: 'utf8' }).stdout.trim() || null;
  const head = git(['rev-parse', 'HEAD'], { cwd }).trim();
  const clean = git(['status', '--porcelain', '--untracked-files=no'], { cwd }).trim() === '';
  return { type, commit, head, clean };
}

/**
 * Identity problems of one tool: the tag must be annotated and resolve to the frozen commit; when
 * `atHead` the checkout must be at that commit with no tracked change (the wrapper that runs).
 */
export function tagProblems(name, want, seen, { atHead = false } = {}) {
  const out = [];
  if (seen.type !== 'tag') out.push(`${name}: tag ${want.tag} is ${seen.type ? `a ${seen.type}, not an annotated tag` : 'missing'}`);
  if (seen.commit !== want.commit) out.push(`${name}: tag ${want.tag} points to ${seen.commit}, FROZEN.json says ${want.commit}`);
  if (atHead && seen.head !== want.commit) out.push(`${name}: checkout is at ${seen.head}, FROZEN.json says ${want.commit}`);
  if (atHead && !seen.clean) out.push(`${name}: checkout has uncommitted changes`);
  return out;
}

/** Artifact problems: the wheel and the .tgz used must be the frozen ones, by name and hash. */
export function artifactProblems(frozen, { wheel, tgz, lockIntegrity, installedVersion }) {
  const out = [];
  if (wheel.name !== frozen.pyvibePro.wheel) out.push(`wheel is ${wheel.name}, FROZEN.json says ${frozen.pyvibePro.wheel}`);
  if (wheel.sha256 !== frozen.pyvibePro.sha256) out.push(`wheel sha256 ${wheel.sha256} != ${frozen.pyvibePro.sha256}`);
  if (tgz.name !== frozen.javaVibeGuardPro.tgz) out.push(`tgz is ${tgz.name}, FROZEN.json says ${frozen.javaVibeGuardPro.tgz}`);
  if (tgz.sha256 !== frozen.javaVibeGuardPro.sha256) out.push(`tgz sha256 ${tgz.sha256} != ${frozen.javaVibeGuardPro.sha256}`);
  if (tgz.integrity !== frozen.javaVibeGuardPro.integrity) out.push(`tgz integrity ${tgz.integrity} != ${frozen.javaVibeGuardPro.integrity}`);
  if (lockIntegrity !== frozen.javaVibeGuardPro.integrity) out.push(`the wrapper's package-lock.json pins java-vibe-guard by ${lockIntegrity}, not ${frozen.javaVibeGuardPro.integrity}`);
  if (installedVersion !== frozen.javaVibeGuardPro.version) out.push(`installed java-vibe-guard is ${installedVersion}, FROZEN.json says ${frozen.javaVibeGuardPro.version}`);
  return out;
}
