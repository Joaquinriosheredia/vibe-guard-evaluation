import { codexReviewer } from '/home/usuariojoaquin/vibe-guard-evaluation-work/tools/vgs-codex/src/review/reviewers/codex.js';
const r = await codexReviewer().review({ prompt: 'ACCESS TEST, not a review. Call the MCP tool find_definitions (server "callers") with symbol "main". Report whether the call succeeded and how many results it returned, and the first result verbatim.', cwd: process.argv[2], timeoutMs: 600000, phase: 'review' });
console.log(JSON.stringify({ ok: r.ok, error: r.error ?? null }, null, 1)); console.log(r.text);
