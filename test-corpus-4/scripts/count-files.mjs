// File counts, stack checks (3e) and code signals (3g) of a checkout, with the frozen
// vibe-guard-scan's own exclusion logic (imported from its src/detect.js), so they match what
// the scan excludes.
//
//   VGS=<vibe-guard-scan checkout> node scripts/count-files.mjs <checkout>
import { existsSync, readdirSync, readFileSync } from 'fs';
import { join } from 'path';
import { pathToFileURL } from 'url';

let detect; // the frozen wrapper's src/detect.js, loaded on first use (never on import)
async function loadDetect() {
  const VGS = process.env.VGS;
  if (!VGS || !existsSync(join(VGS, 'src', 'detect.js'))) throw new Error('VGS must point to the vibe-guard-scan checkout');
  detect ??= await import(pathToFileURL(join(VGS, 'src', 'detect.js')).href);
  return detect;
}

const SPRING_BOOT_BUILD = new Set(['pom.xml', 'build.gradle', 'build.gradle.kts']);
export const PY_FRAMEWORKS = ['fastapi', 'aiohttp', 'starlette', 'litestar', 'sanic', 'quart'];
const PY_IMPORT_RE = new RegExp(`^\\s*(?:from|import)\\s+(${PY_FRAMEWORKS.join('|')})\\b`, 'gm');

// 3g: literal signals, matched anywhere in the file text (comments included).
export const JAVA_SIGNAL_RES = {
  enableAsync: /@EnableAsync\b/,
  async: /@Async\b/,
  kafka: /^\s*import\s+org\.springframework\.kafka\.core\.KafkaTemplate\s*;|@KafkaListener\b|^\s*import\s+org\.apache\.kafka\.clients\.producer\.(?:KafkaProducer|Producer)\s*;/m,
  reactor: /^\s*import\s+reactor\.core\.publisher\.(?:Mono|Flux|\*)\s*;/m,
};

/** Signals present in one .java file's text. */
export function javaSignals(text) {
  return Object.fromEntries(Object.entries(JAVA_SIGNAL_RES).map(([k, re]) => [k, re.test(text)]));
}

/** Signal families of a repository from its merged signals: ASYNC needs both annotations, possibly in different files. */
export function families(signals) {
  const out = [];
  if (signals.enableAsync && signals.async) out.push('ASYNC');
  if (signals.kafka) out.push('KAFKA');
  if (signals.reactor) out.push('REACTOR');
  return out;
}

/** Python frameworks imported at the start of a line in one .py file's text. */
export function pyFrameworks(text) {
  return [...new Set([...text.matchAll(PY_IMPORT_RE)].map((m) => m[1]))].sort();
}

/**
 * @returns {{ java: number, python: number, springBoot: boolean, pyFrameworks: string[],
 *   signals: Record<string, boolean>, families: string[], applied: {path:string, pattern:string, files:number}[] }}
 */
export async function countFiles(root) {
  await loadDetect();
  const applied = detect.resolveDefaultExcludes(root, detect.SCAN_DEFAULT_EXCLUDES, []);
  const excluded = new Set(applied.map((a) => join(root, a.path)));
  const skip = new Set([...detect.JAVA_DEFAULT_EXCLUDES, ...detect.PYVIBE_DEFAULT_EXCLUDES]);
  const out = { java: 0, python: 0, springBoot: false, pyFrameworks: new Set(), signals: Object.fromEntries(Object.keys(JAVA_SIGNAL_RES).map((k) => [k, false])), applied };
  const read = (p) => { try { return readFileSync(p, 'utf8'); } catch { return ''; } };
  const stack = [root];
  while (stack.length > 0) {
    const dir = stack.pop();
    let entries;
    try { entries = readdirSync(dir, { withFileTypes: true }); } catch { continue; }
    for (const e of entries) {
      const p = join(dir, e.name);
      if (e.isDirectory()) {
        if (!skip.has(e.name) && !excluded.has(p)) stack.push(p);
      } else if (e.isFile()) {
        if (e.name.endsWith('.java')) {
          out.java++;
          const s = javaSignals(read(p));
          for (const k of Object.keys(s)) out.signals[k] ||= s[k];
        } else if (e.name.endsWith('.py')) {
          out.python++;
          for (const f of pyFrameworks(read(p))) out.pyFrameworks.add(f);
        } else if (!out.springBoot && SPRING_BOOT_BUILD.has(e.name)) {
          out.springBoot = read(p).includes('spring-boot');
        }
      }
    }
  }
  return { ...out, pyFrameworks: [...out.pyFrameworks].sort(), families: families(out.signals) };
}

if (import.meta.url === pathToFileURL(process.argv[1] ?? '').href) {
  console.log(JSON.stringify(await countFiles(process.argv[2]), null, 2));
}
