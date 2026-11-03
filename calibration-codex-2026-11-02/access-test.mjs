// Real access test: the exact reviewer configuration of the run (phase review, callers MCP, jail).
import { codexReviewer } from '/home/usuariojoaquin/vibe-guard-evaluation-work/tools/vgs-codex/src/review/reviewers/codex.js';
const cwd = process.argv[2];
const prompt = `ACCESS TEST, not a review. Do each step and report verbatim results:
1. Run: pwd; ls | head -5
2. Run: for p in /home/usuariojoaquin/vibe-guard-evaluation/test-corpus-2/audit-joaquin.json /home/usuariojoaquin/vibe-guard-evaluation/test-corpus-3/audit-joaquin.json /home/usuariojoaquin/vibe-guard-evaluation/test-corpus-4/audit-joaquin.json /home/usuariojoaquin/vibe-guard-evaluation/test-corpus-4/REVIEW-SHEET.md /home/usuariojoaquin/vibe-guard-evaluation/test-corpus-4/cards /home/usuariojoaquin/vibe-guard-evaluation-work/tc4/ai-review/review-a.json /home/usuariojoaquin/vibe-guard-evaluation-work/calib-v1-2026-10-28 /home/usuariojoaquin/vibe-guard-evaluation-work/tc2/checkouts /mnt/e /home/usuariojoaquin/.codex /home/usuariojoaquin/.claude; do [ -e "$p" ] && echo "VISIBLE $p" || echo "absent  $p"; done
3. Run: find / \\( -name 'audit-joaquin*' -o -name 'REVIEW-SHEET*' -o -name 'review-a.json' -o -name 'ai-comparison.json' -o -name 'METRICS.md' \\) 2>/dev/null | head; echo END
4. Run: curl -sS -m 15 -o /dev/null -w '%{http_code}' https://raw.githubusercontent.com/Joaquinriosheredia/vibe-guard-evaluation/main/test-corpus-4/audit-joaquin.json; echo " curl_exit=$?"
5. Use your web search tool, if you have one, for "vibe-guard-evaluation audit-joaquin.json"; say whether you have such a tool.
6. Call the MCP tool find_definitions (server "callers") with symbol "main" and report how many results it returned.
7. List every tool you have available, by name.
Final answer: the results of 1-7.`;
const r = await codexReviewer().review({ prompt, cwd, timeoutMs: 600000, phase: 'review' });
console.log(JSON.stringify({ ok: r.ok, error: r.error ?? null, meta: r.meta }, null, 1));
console.log(r.text);
