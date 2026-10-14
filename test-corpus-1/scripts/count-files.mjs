// File counts and stack signals of a checkout, with the frozen vibe-guard-scan's own
// exclusion logic (imported from its src/detect.js), so they match what the scan excludes.
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
const FASTAPI_IMPORT_RE = /^\s*(?:from\s+fastapi\b|import\s+fastapi\b)/m;

/**
 * @returns {{ java: number, python: number, springBoot: boolean, fastapi: boolean,
 *   applied: {path:string, pattern:string, files:number}[] }}
 */
export async function countFiles(root) {
  await loadDetect();
  const applied = detect.resolveDefaultExcludes(root, detect.SCAN_DEFAULT_EXCLUDES, []);
  const excluded = new Set(applied.map((a) => join(root, a.path)));
  const skip = new Set([...detect.JAVA_DEFAULT_EXCLUDES, ...detect.PYVIBE_DEFAULT_EXCLUDES]);
  const out = { java: 0, python: 0, springBoot: false, fastapi: false, applied };
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
        if (e.name.endsWith('.java')) out.java++;
        else if (e.name.endsWith('.py')) {
          out.python++;
          if (!out.fastapi) { try { out.fastapi = FASTAPI_IMPORT_RE.test(readFileSync(p, 'utf8')); } catch { /* unreadable */ } }
        } else if (!out.springBoot && SPRING_BOOT_BUILD.has(e.name)) {
          try { out.springBoot = readFileSync(p, 'utf8').includes('spring-boot'); } catch { /* unreadable */ }
        }
      }
    }
  }
  return out;
}

if (import.meta.url === pathToFileURL(process.argv[1] ?? '').href) {
  console.log(JSON.stringify(await countFiles(process.argv[2]), null, 2));
}
