---
name: preview-deploy
description: >-
  Restart the lms-preview Vite container and confirm it comes back healthy.
  Use after changing vite.preview.config.mjs or anything that needs a real
  restart (HMR is not enough). Run as /preview-deploy.
disable-model-invocation: true
---

# preview-deploy

Restart the **`frappe-lms-preview-1`** container (the Vite dev server behind
`lms-preview.craftspace.space`) and verify it's healthy.

> Source edits hot-reload via the bind-mount, so you do NOT need this for normal
> `.vue`/`.ts` changes. You DO need it after editing `vite.preview.config.mjs`,
> changing env, or when HMR is stuck.

## Steps

1. Restart the container:
   ```bash
   cd /home/medo94my/apps/frappe
   docker compose -f compose.yml -f compose.preview.yml restart lms-preview
   ```
2. Wait for Vite to be ready, then show the tail of the logs:
   ```bash
   for i in $(seq 1 20); do
     docker logs --tail 30 frappe-lms-preview-1 2>&1 | grep -q "VITE.*ready\|Local:" && break
     sleep 1
   done
   docker logs --tail 25 frappe-lms-preview-1 2>&1
   ```
3. Smoke-test that the proxy is up (should print `200`):
   ```bash
   docker exec frappe-lms-preview-1 sh -c \
     "curl -s -o /dev/null -w '%{http_code}\n' 'http://localhost:5173/socket.io/?EIO=4&transport=polling'"
   ```
4. Report: container status, the ready line, and the smoke-test code. Tell the
   user to hard-refresh `lms-preview.craftspace.space` (Cmd/Ctrl+Shift+R, since
   Cloudflare caching is bypassed via `no-store`).

## Notes

- Real site name for this deployment: `frappe.craftspace.space`.
- If the container won't start, check `docker logs frappe-lms-preview-1` for a
  Vite config parse error first.
