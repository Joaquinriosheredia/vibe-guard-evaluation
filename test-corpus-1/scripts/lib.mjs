// Shared helpers: GitHub REST calls (token from `gh auth token`), JSON files, git.
import { execFileSync, spawnSync } from 'child_process';
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
