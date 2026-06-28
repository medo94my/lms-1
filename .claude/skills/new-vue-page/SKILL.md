---
name: new-vue-page
description: >-
  Scaffold a new routed page in the LMS frontend — creates the .vue under
  frontend/src/pages, registers a lazy route in router.js, and wires
  createResource with the auto:false + watch().reload() pattern this codebase
  requires. Use when adding a new screen/route. Run as /new-vue-page <Name>.
disable-model-invocation: true
---

# new-vue-page

Scaffold a new page for the Vue 3 + `frappe-ui` frontend at
`/home/medo94my/apps/lms-src/frontend/src`, wired the way this app expects.

Take the page **name** (and any route path / dynamic params) from the user's
`/new-vue-page` arguments. If a path or params weren't given, ask once, then
proceed.

## Steps

1. **Create the component** at `frontend/src/pages/<Name>.vue` (or under a
   subfolder like `pages/Courses/` if it belongs to an existing group — match the
   neighbours). Use `<script setup>` Composition API and these conventions:
   - Wrap every user-facing string in `__()`.
   - Use **logical** Tailwind spacing (`ms-*`/`me-*`/`ps-*`/`pe-*`, `text-start`)
     so the page holds up in RTL — this is the Basiret Arabic-first rebrand.
   - Pull colors from the Basiret theme tokens, not hardcoded hex.
2. **Wire data with the mandatory async-safe pattern.** For any `createResource`
   whose params come from route params or async props, **never** use `auto: true`
   (frappe-ui drops `undefined` params and the backend 500s with
   `TypeError: ... missing 1 required positional argument`). Instead:
   ```js
   const resource = createResource({
     url: 'lms.lms.api.some_method',
     auto: false,
     cache: () => ['some-key', props.someParam], // reactive key, not a snapshot
   })
   watch(
     () => props.someParam,
     (val) => { if (val) resource.reload({ some_param: val }) },
     { immediate: true },
   )
   ```
3. **Register the route** in `frontend/src/router.js` as a lazy import, matching
   the existing entries' formatting (tabs, trailing comma). Set `props: true` when
   the route has dynamic segments:
   ```js
   {
     path: '/<your-path>/:someParam',
     name: '<Name>',
     component: () => import('@/pages/<Name>.vue'),
     props: true,
   },
   ```
4. **Verify**: confirm the route name is unique, the import path resolves, and the
   page renders (point the user at `lms-preview.craftspace.space/<path>` — HMR
   picks up new `.vue` files via the bind-mount; no restart needed).

## Notes

- Model new pages on a close existing one (e.g. `pages/Courses/CourseDetail.vue`
  for a param-driven detail page) so props/resource patterns stay consistent.
- After scaffolding, suggest running the `vue-frontend-reviewer` and
  `rtl-i18n-reviewer` agents over the new file.
