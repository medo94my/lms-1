# LMS (Basiret Vakfı rebrand) — project guide

Frappe **LMS** app (Python, flit) with a **Vue 3 + Vite + TypeScript** frontend
(`frappe-ui`). Active branch `basiret-redesign` rebrands the UI for
**Basiret Vakfı / وقف بصيرة** — Arabic-first, RTL, deep-green + gold. See
`design-docs/` (`DESIGN.md`, `COLORS_TOKENS.md`, `PRODUCT.md`) and
`frontend/src/styles/basiret-theme.css`.

## Deployment topology (non-obvious — read before debugging the live site)

The live site runs as a **Docker Compose stack**, not a host bench.
`/home/frappe/...` paths exist only INSIDE containers — inspect via `docker exec`.

- **lms-preview.craftspace.space** → Cloudflare tunnel (`infra/cloudflared/config.yml`)
  → Traefik (`reverse-proxy-traefik-1`) → **`frappe-lms-preview-1`**: a `node:24`
  **Vite dev server** (:5173), `apps/frappe/compose.preview.yml`.
- `frappe-lms-preview-1` **bind-mounts `/home/medo94my/apps/lms-src` → `/app`** →
  `.vue`/`.ts` edits hot-reload. **`vite.preview.config.mjs` changes need a restart**
  (use `/preview-deploy`).
- Real Frappe **site name = `frappe.craftspace.space`**. The Vite proxy forces that
  as the `Host` header so site resolution works (backend `http://backend:8000`,
  socketio `http://websocket:9000`).
- **Production backend** (`frappe-backend-1`, `ghcr.io/frappe/lms:stable`) runs lms on
  **`develop`** — backend bugs reproduce on prod too; the preview changes only the
  frontend.

## Working in this repo

- **Debugging the live site:** use the `frappe-lms-debugger` agent — it knows the
  container layout, how to pull real tracebacks
  (`docker exec frappe-backend-1 bench --site frappe.craftspace.space console`), and
  the Vite proxy model. Don't diagnose browser console errors from the symptom alone.
- **Frontend review:** use the `vue-frontend-reviewer` agent after editing
  `frontend/src` — it targets the resource-lifecycle/timing bugs common here.
- **Restart preview:** `/preview-deploy`.

## Conventions & gotchas

- **`frappe-ui` `createResource`:** never `auto: true` when params come from async
  props — frappe-ui drops `undefined` params and the backend 500s with
  `TypeError: ... missing 1 required positional argument`. Use `auto: false` + a
  `watch` that `reload()`s once the param exists. Make `cache` keys reactive.
- **i18n / RTL:** wrap user-facing strings in `__()`; prefer logical spacing over
  hardcoded left/right so RTL holds.
- **Lint/format:** Ruff (pre-commit) for Python, Prettier/ESLint for the frontend.
  A PostToolUse hook auto-formats on edit when the tools are available.
- **Tests:** Vitest unit tests in `frontend/src/tests`, Cypress e2e in `cypress/`.
- **Protected files:** `common_site_config.json`, `site_config.json`, `*.env`, and
  `infra/**` are blocked from automated edits by a PreToolUse hook — edit manually.

## General engineering guidelines

> Imported from [`andrej-karpathy-skills`](https://github.com/forrestchang/andrej-karpathy-skills).
> Behavioral guidelines to reduce common LLM coding mistakes. They **complement** the
> project-specific instructions above — where they conflict, the project rules win.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

### Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

### Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

### Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

### Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.
