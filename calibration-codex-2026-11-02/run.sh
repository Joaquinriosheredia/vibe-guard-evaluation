#!/usr/bin/env bash
# Calibración Codex 2026-11-02: proposer only (chain-v1), TC3, TC2, TC4. Rerun to resume:
# vibe-guard review skips the IDs already in <out>. Exit 3 (usage limit) stops the script.
set -uo pipefail
W=/home/usuariojoaquin/vibe-guard-evaluation-work/calib-codex-2026-11-02
E=/home/usuariojoaquin/vibe-guard-evaluation
VG=/home/usuariojoaquin/vibe-guard-evaluation-work/tools/vgs-codex/bin/vibe-guard.js
export VIBE_GUARD_CODEX=$W/codex-jail.sh
export JAIL_CODEX_AUTH=$HOME/.codex/auth.json
export JAIL_CODEX_EXEC_ARGS=$'-c\nmodel_reasoning_effort="medium"'
for c in 3 2 4; do
  echo "- $(date -Iseconds) TC$c start" >> $W/RUN.md
  node $VG review $E/test-corpus-$c/cards \
    --instructions $E/REVIEW-AI-INSTRUCTIONS.md \
    --examples $E/calibration-v1-2026-10-28/examples-tc2.md \
    --checkouts /home/usuariojoaquin/vibe-guard-evaluation-work/tc$c/checkouts \
    --out $W/out-tc$c --ids-file $W/ids-tc$c.txt \
    --protocol chain-v1 --reviewer-a codex --model-a gpt-6.1-sol --reviewer-b none \
    --concurrency 3 >> $W/run-tc$c.log 2>&1
  rc=$?
  echo "- $(date -Iseconds) TC$c exit $rc" >> $W/RUN.md
  if [ $rc -eq 3 ]; then echo "- USAGE LIMIT STOP during TC$c" >> $W/RUN.md; exit 3; fi
  if [ $rc -ne 0 ] && [ $rc -ne 1 ]; then echo "- unexpected exit during TC$c" >> $W/RUN.md; exit $rc; fi
done
echo "- $(date -Iseconds) all done" >> $W/RUN.md
