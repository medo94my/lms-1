#!/usr/bin/env bash
# PostToolUse hook — format files right after Claude edits them, so edits land
# CI-clean (Ruff for Python, Prettier for the Vue frontend).
#
# Non-blocking by contract: ALWAYS exits 0. If a formatter isn't installed it
# silently no-ops rather than failing the edit. Reads the tool-call JSON on
# stdin and pulls the edited file path from it.
set -uo pipefail

input=$(cat)
file=$(printf '%s' "$input" | jq -r '.tool_input.file_path // empty' 2>/dev/null)
[ -z "$file" ] && exit 0
[ -f "$file" ] || exit 0

case "$file" in
	*.py)
		# Ruff isn't on the host PATH by default (it's pinned in pre-commit).
		# Use it if present, else fall back to `python3 -m ruff`, else skip.
		if command -v ruff >/dev/null 2>&1; then
			ruff check --select I --fix "$file" >/dev/null 2>&1
			ruff format "$file" >/dev/null 2>&1
		elif python3 -m ruff --version >/dev/null 2>&1; then
			python3 -m ruff check --select I --fix "$file" >/dev/null 2>&1
			python3 -m ruff format "$file" >/dev/null 2>&1
		fi
		;;
	*/frontend/*.vue|*/frontend/*.ts|*/frontend/*.js|*/frontend/*.mjs|*/frontend/*.css|*/frontend/*.scss|*/frontend/*.json)
		pretty="${CLAUDE_PROJECT_DIR:-.}/frontend/node_modules/.bin/prettier"
		if [ -x "$pretty" ]; then
			( cd "${CLAUDE_PROJECT_DIR:-.}/frontend" && "$pretty" --write "$file" >/dev/null 2>&1 )
		fi
		;;
esac

exit 0
