---
name: gen-vitest
description: >-
  Scaffold a Vitest + @vue/test-utils spec for a frontend component, mirroring
  the existing tests in frontend/src/tests and focusing on the mount/teardown
  lifecycle paths that keep regressing here. Use when a component lacks coverage
  or a teardown bug needs a guard test. Run as /gen-vitest <path-to-component>.
disable-model-invocation: true
---

# gen-vitest

Generate a unit spec for a Vue component under
`/home/medo94my/apps/lms-src/frontend`, matching this repo's test style.

Take the **target component** from the `/gen-vitest` arguments (a path under
`frontend/src/...`). If none given, ask which component.

## Steps

1. **Read the target component** and at least one existing spec to mirror the
   house style — look at `frontend/src/tests/lessonForm.test.ts`,
   `blockEditor.test.ts`, and the `*Teardown.test.ts` files. The stack is
   **Vitest + `@vue/test-utils` + jsdom** (config in `frontend/vitest`/`vite`
   config; `jsdom` is the env).
2. **Create the spec** at `frontend/src/tests/<ComponentName>.test.ts`. Cover, in
   priority order:
   - **Mount with realistic props**, including the case where async props are
     still `undefined` on first render (must not throw).
   - **Lifecycle / teardown** — this is the bug class that recurs here
     (autosave-on-unmount, editor destroy, listeners). If the component saves or
     cleans up in `onBeforeUnmount`/`onUnmounted`, assert it doesn't drop data or
     write to a deleted doc on teardown (see `lessonFormTeardown.test.ts`,
     `blockEditorTeardown.test.ts` for the pattern).
   - Key user interactions and the emitted events / resource calls they trigger.
   - i18n: assert via the rendered text, not hardcoded English, where `__()` is
     in play.
3. **Mock external boundaries** the existing specs mock — `frappe-ui`
   `createResource`/`call`, router, socket.io — rather than hitting a real
   backend. Reuse the mocking approach already present in the sibling specs.
4. **Run it** and iterate until green:
   ```bash
   cd /home/medo94my/apps/lms-src/frontend && npm test -- <ComponentName>
   ```
   (or `node_modules/.bin/vitest run src/tests/<ComponentName>.test.ts`.)
5. Report the file created and the pass/fail result. Note any behavior the test
   couldn't reach (e.g. needs a real backend) instead of weakening the assertion.

## Notes

- Prefer testing observable behavior (rendered output, emitted events, resource
  calls) over internal state.
- The PostToolUse `test-related-on-edit` hook will re-run the relevant specs on
  future edits, so a good teardown test here pays off on every later change.
