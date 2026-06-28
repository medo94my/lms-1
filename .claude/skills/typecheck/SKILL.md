---
name: typecheck
description: >-
  Type-check the Vue/TS frontend with vue-tsc --noEmit and report (optionally
  fix) the errors. The Vite dev server does NOT fail on type errors, so they
  hide until build/runtime — run this before committing TS changes. Run as
  /typecheck.
disable-model-invocation: true
---

# typecheck

Run a whole-project TypeScript check over
`/home/medo94my/apps/lms-src/frontend` and surface the errors. This is a manual
skill (not an edit hook) because `vue-tsc` checks the entire project graph — too
slow to run on every keystroke, but exactly right as a pre-commit gate.

## Steps

1. **Check the tool is available** (it is not in `devDependencies` by default):
   ```bash
   cd /home/medo94my/apps/lms-src/frontend && ls node_modules/.bin/vue-tsc
   ```
   If missing, tell the user it needs installing and stop unless they approve:
   ```bash
   cd /home/medo94my/apps/lms-src/frontend && npm i -D vue-tsc
   ```
   (Adds `vue-tsc` + touches `package.json`/lockfile — that's a repo change, so
   ask first.)
2. **Run the check** (no emit — type errors only):
   ```bash
   cd /home/medo94my/apps/lms-src/frontend && node_modules/.bin/vue-tsc --noEmit
   ```
3. **Report** the errors grouped by file, each as `file:line` + the message +
   the likely fix. Pay special attention to:
   - `createResource` generics / `Resource` typing (a known rough edge here),
   - props typed too loosely so async-`undefined` access slips through,
   - missing `.value` on refs.
4. **Fix only if asked.** If the user said `/typecheck --fix` (or asks), apply the
   minimal type fixes and re-run until clean. Otherwise just report.

## Notes

- Consider adding a `"typecheck": "vue-tsc --noEmit"` script to
  `frontend/package.json` so CI and contributors can run the same gate.
- A clean run means no type errors — say so plainly; don't invent findings.
