#!/usr/bin/env bash
# PreToolUse hook — block Claude from editing infrastructure / secret files.
# These hold deployment + credential state you don't want an agent rewriting
# as a side effect of a task. Exit 2 blocks the tool call and shows the reason
# to the model; exit 0 allows it.
set -uo pipefail

input=$(cat)
file=$(printf '%s' "$input" | jq -r '.tool_input.file_path // empty' 2>/dev/null)
[ -z "$file" ] && exit 0

case "$file" in
	*common_site_config.json|*/site_config.json|*.env|*.env.*|\
	*/infra/cloudflared/*|*/infra/reverse-proxy/*|*/infra/authelia/*|*credentials*)
		echo "BLOCKED: '$file' is infrastructure/secret config and is protected from automated edits. If this change is truly intended, edit the file manually." >&2
		exit 2
		;;
esac

exit 0
