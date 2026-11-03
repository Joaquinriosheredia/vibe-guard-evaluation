#!/usr/bin/env bash
# Reanuda run.sh tras cada parada por límite de uso: espera a la hora "try again at" + 5 min
# (reloj real), máximo 6 reanudaciones. Cada parada queda en RUN.md.
W=/home/usuariojoaquin/vibe-guard-evaluation-work/calib-codex-2026-11-02
n=${1:-3}
for i in 1 2 3 4 5 6; do
  msg=$(grep -h "try again at" $W/run-tc*.log | tail -1 | sed -E 's/.*try again at (.*)\.$/\1/')
  when=$(echo "$msg" | sed -E 's/([0-9]+)(st|nd|rd|th),/\1/')
  t=$(date -d "$when" +%s 2>/dev/null) || { echo "- cannot parse reset time: $msg" >> $W/RUN.md; exit 2; }
  t=$((t + 300))
  echo "- $(date -Iseconds) resume $n scheduled for $(date -d @$t -Iseconds) (Codex: try again at $msg)" >> $W/RUN.md
  while [ $(date +%s) -lt $t ]; do sleep 30; done
  echo "- $(date -Iseconds) resume $n" >> $W/RUN.md
  $W/run.sh; rc=$?
  [ $rc -ne 3 ] && exit $rc
  n=$((n + 1))
done
exit 3
