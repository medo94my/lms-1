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
