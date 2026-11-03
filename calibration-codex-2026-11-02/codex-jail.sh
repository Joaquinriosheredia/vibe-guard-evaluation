#!/usr/bin/env bash
# codex-jail.sh — runs the Codex CLI inside a bubblewrap mount namespace that contains ONLY:
# the system (/usr, /etc, resolv.conf), the Codex install, a fresh per-call CODEX_HOME (just a
# copy of auth.json), and the directories the reviewer names in VIBE_GUARD_CODEX_RO (read-only:
# checkout, task file, callers MCP server) and VIBE_GUARD_CODEX_RW (the last-message file's dir),
# one path per line. Nothing else exists inside: not $HOME, not /mnt, not the evaluation repo
# (audit-joaquin.json, REVIEW-SHEET.md), not the Claude review outputs, not other checkouts.
#
# Used as VIBE_GUARD_CODEX=<this script> by vibe-guard review --reviewer-a codex.
# JAIL_CODEX_AUTH: the auth.json to copy in (and back, if Codex refreshed it).
# JAIL_CODEX_EXEC_ARGS: extra options inserted right after `exec` (one per line), e.g. the
# reasoning effort, which vibe-guard review has no flag for.
set -euo pipefail

CODEX_PKG="${JAIL_CODEX_PKG:-$HOME/.npm-global/lib/node_modules/@openai/codex}"
AUTH="${JAIL_CODEX_AUTH:?JAIL_CODEX_AUTH must point to an auth.json}"

home="$(mktemp -d /tmp/codex-jail-home.XXXXXX)"
trap 'rm -rf "$home"' EXIT
cp "$AUTH" "$home/auth.json"
chmod 600 "$home/auth.json"

args=(
  --unshare-all --share-net --die-with-parent --new-session
  --ro-bind /usr /usr
  --symlink usr/bin /bin --symlink usr/lib /lib --symlink usr/lib64 /lib64 --symlink usr/sbin /sbin
  --ro-bind /etc /etc
  --proc /proc --dev /dev --tmpfs /tmp
  --ro-bind "$CODEX_PKG" "$CODEX_PKG"
  --bind "$home" "$home"
  --setenv HOME "$home" --setenv CODEX_HOME "$home" --setenv TMPDIR /tmp
)
[ -e /mnt/wsl/resolv.conf ] && args+=(--ro-bind /mnt/wsl/resolv.conf /mnt/wsl/resolv.conf)
while IFS= read -r d; do [ -n "$d" ] && args+=(--ro-bind "$d" "$d"); done <<< "${VIBE_GUARD_CODEX_RO:-}"
while IFS= read -r d; do [ -n "$d" ] && args+=(--bind "$d" "$d"); done <<< "${VIBE_GUARD_CODEX_RW:-}"
args+=(--chdir "$PWD")

cmd=("$@")
if [ "${cmd[0]:-}" = exec ] && [ -n "${JAIL_CODEX_EXEC_ARGS:-}" ]; then
  extra=(); while IFS= read -r a; do [ -n "$a" ] && extra+=("$a"); done <<< "$JAIL_CODEX_EXEC_ARGS"
  cmd=(exec "${extra[@]}" "${cmd[@]:1}")
fi

set +e
bwrap "${args[@]}" -- /usr/bin/node "$CODEX_PKG/bin/codex.js" "${cmd[@]}"
rc=$?
set -e

# A refreshed token is written back so the next call (and the user's own login) keeps working.
if ! cmp -s "$home/auth.json" "$AUTH"; then
  ( flock 9; cp "$home/auth.json" "$AUTH.tmp" && mv "$AUTH.tmp" "$AUTH" ) 9>"$AUTH.lock"
fi
exit $rc
