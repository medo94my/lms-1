#!/usr/bin/env bash
# PostToolUse hook — after Claude edits a frontend source file, run the Vitest
# specs related to it. This codebase keeps regressing on editor lifecycle /
# teardown paths (see frontend/src/tests/*Teardown.test.ts), so fast feedback on
# the change that just landed catches those before a commit.
#
# Feedback contract: if related tests FAIL, exit 2 and print the failure tail on
# stderr so the model sees it and can self-correct (the edit itself is NOT undone
# — PostToolUse runs after the write). If tests pass, there's no related spec, or
# Vitest isn't installed, it silently exits 0. Never blocks on a clean tree.
set -uo pipefail

input=$(cat)
file=$(printf '%s' "$input" | jq -r '.tool_input.file_path // empty' 2>/dev/null)
[ -z "$file" ] && exit 0
[ -f "$file" ] || exit 0

# Only react to frontend source/test edits.
case "$file" in
	*/frontend/src/*.ts|*/frontend/src/*.js|*/frontend/src/*.vue) ;;
	*) exit 0 ;;
esac

root="${CLAUDE_PROJECT_DIR:-.}"
vitest="$root/frontend/node_modules/.bin/vitest"
[ -x "$vitest" ] || exit 0

# `vitest related` maps the changed file to the specs that import it (directly or
# transitively) and runs only those. --run = no watch; bail early on first fail.
out=$(cd "$root/frontend" && "$vitest" related "$file" --run --reporter=dot --bail=1 2>&1)
code=$?

if [ "$code" -ne 0 ]; then
	echo "Related Vitest specs FAILED after editing $file:" >&2
	printf '%s\n' "$out" | tail -n 40 >&2
	echo "Fix the regression or update the spec before continuing." >&2
	exit 2
fi

exit 0
