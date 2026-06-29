# FE Task 5 Report — Host per-type author components in Question modal

## Vitest output (questionTypes.test.ts — full run)

```
 RUN  v4.1.7 /home/medo94my/apps/lms-src/frontend

 ✓ question type registry > registers the three existing types
 ✓ question type registry > throws on an unknown type
 ✓ Choices helpers > getAnswers returns the selected option labels
 ✓ Choices helpers > loadAnswer marks the saved options as selected
 ✓ User Input helpers > getAnswers wraps the text answer in an array
 ✓ User Input helpers > loadAnswer restores the first saved answer
 ✓ Open Ended helpers > is not auto-graded and has no live check

 Test Files  1 passed (1)
      Tests  7 passed (7)
```

Full suite (18 files, 134 tests): all pass.

## Lint result

No ESLint config (`eslint.config.*` / `.eslintrc.*`) and no `lint` or `typecheck` script in `frontend/package.json`. ESLint is not configured for this project — cannot run. No lint step available.

## Vitest regression fix (side effect of this task)

`ChoicesAuthor.vue` and `UserInputAuthor.vue` import from `frappe-ui`, which has
`"type": "module"` and uses extensionless ESM internal imports
(`documentResource.js` → `import './resources'`) that fail under Node's strict ESM
resolver in Vitest. The stub components did not trigger this; the real components do.

**Fix applied:** `frontend/vitest.config.ts` — switched `resolve.alias` from
object-form to array-form and added a **regex exact-match** alias
`/^frappe-ui$/ → src/__mocks__/frappe-ui.ts`. The regex prevents sub-path imports
like `frappe-ui/frappe` from being caught (string aliases match by prefix).

**New file:** `frontend/src/__mocks__/frappe-ui.ts` — minimal PassThrough stubs for
all frappe-ui component exports plus `toast`, `createResource`, `useOnboarding`, etc.
Tests that call `vi.mock('frappe-ui', factory)` still use their explicit factory
(vi.mock intercepts before alias resolution); this stub is only used by tests that
import frappe-ui transitively without mocking it.

## What was removed from Question.vue

| Removed | Reason |
|---------|--------|
| `const visibleOptionCount = ref(2)` | Moved to ChoicesAuthor.vue |
| `const visiblePossibilityCount = ref(1)` | Moved to UserInputAuthor.vue |
| `addOption()` function | Moved to ChoicesAuthor.vue |
| `removeOption(pos)` function | Moved to ChoicesAuthor.vue |
| `addPossibility()` function | Moved to UserInputAuthor.vue |
| `removePossibility(pos)` function | Moved to UserInputAuthor.vue |
| `visibleOptionCount.value = Math.max(...)` in `onSuccess` | Handled by ChoicesAuthor watch |
| `visiblePossibilityCount.value = Math.max(...)` in `onSuccess` | Handled by UserInputAuthor watch |
| `visibleOptionCount.value = 2` in show-watcher reset block | Moved to ChoicesAuthor state |
| `visiblePossibilityCount.value = 1` in show-watcher reset block | Moved to UserInputAuthor state |
| Entire per-type template block (95 lines: Options heading, Choices grid, Add Option button, Possibilities heading, Possibilities grid, Add Possibility button) | Replaced with single `<component :is="..." v-model:question="question" />` |
| `:options="['Choices', 'User Input', 'Open Ended']"` on Type select | Replaced with `:options="questionTypeOptions()"` |

## Dangling references check

```
grep visibleOptionCount|visiblePossibilityCount|addOption|removeOption|addPossibility|removePossibility Question.vue
→ CLEAN — no dangling refs
```

All kept per brief: `populateFields()`, `MAX_OPTIONS`, all `createResource` instances
(`questionData`, `questionRow`, `questionCreation`, `questionUpdate`, `marksUpdate`),
the full `onSuccess` field-copy loop, `submitQuestion`, `addQuestion`, `addQuestionRow`,
`updateQuestion`.

## Concerns

**Timing: visibleCount watch on reactive question object.** In ChoicesAuthor/UserInputAuthor,
`watch(question, ..., { immediate: true })` fires immediately on mount. At that point
`question.value` is the parent's `reactive({})` object. If the modal opens in *edit mode*,
`questionData.onSuccess` runs first (it copies field values into the reactive object), then
Vue mounts the `<component>`. The `{ immediate: true }` watch fires on mount and sees the
populated fields — **correct behaviour**.

If somehow the component mounts before `onSuccess` fires (race condition), the watch would
see empty fields and set `visibleOptionCount = 2` (the fallback). However, since `auto: false`
and `questionData.fetch()` is called in the `watch(show)` handler only when
`props.questionDetail.question` is set, the sequence is: fetch → onSuccess → question fields
populated → component mounts (on next render cycle after question.type is set). This is safe.

**No other concerns.** The payload to LMS Question is unchanged: `questionCreation` spreads
`...question` which still has all `option_N`/`is_correct_N`/`explanation_N`/`possibility_N`
fields (set by `populateFields()` and mutated by the author components).

## rtl-i18n-reviewer findings and resolution

**SHOULD-FIX (both applied, committed ed3a586c):**

1. Interpolated label strings — `__('Option') + ' ' + n` and `__('Possibility') + ' ' + n`
   break translation extraction and cause bidi reordering hazard. Fixed to
   `__('Option {0}', [n])` / `__('Possibility {0}', [n])`.

2. Icon-only trash buttons lacked `aria-label`. Fixed to
   `:aria-label="__('Remove option {0}', [n])"` / `__('Remove possibility {0}', [n])"`.

**Pre-existing (not touched per surgical-changes guideline):**

- `<style>` block in Question.vue uses `theme('colors.gray.900')` for radio checked state
  instead of brand tokens — pre-existing before this task.
- Double-translation on `title` prop default — pre-existing before this task.

**RTL layout verdict:** CLEAN — no physical directional Tailwind classes in any changed file.

## vue-frontend-reviewer findings and resolution

**BLOCKER (fixed, committed 6abe3e1a):**

- `watch(question, ...)` in ChoicesAuthor.vue and UserInputAuthor.vue was missing
  `{ deep: true }`. `question` is a ModelRef over the host's `reactive({})` object,
  which `questionData.onSuccess` mutates *in place* (never replaced). A shallow
  ref-watch only fires on reference change, so it never re-fired after the saved
  `option_N`/`possibility_N` fields loaded — editing a saved question with >2 options
  or >1 possibility would render only the default rows and hide the rest. Added
  `{ immediate: true, deep: true }` to both watches. This restores the exact
  behaviour the host's old inline `Math.max` recomputation in `onSuccess` provided.

**SHOULD-FIX — deferred (out of this task's file scope / not reachable today):**

1. `questionTypes/index.ts:27` `questionTypeOptions()` returns raw `label` strings, so
   the select stores `question.type = label`. Works today because all three types have
   `name === label`. Would break the day a type's label diverges from its registry key.
   `index.ts` is outside this task's allowed file set (Question.vue + the 3 author
   components). **Recommend a follow-up** to return `{ value: name, label }` objects.

2. `Question.vue:45` `getQuestionType(question.type)` throws for an unregistered type,
   which would crash the modal render. Not reachable today: the select only offers
   registry types, `question.type` defaults to `'Choices'`, and saved data is always
   one of the three registered names. **Recommend a follow-up** guard if backend-only
   types are ever added.

**Pre-existing (not introduced by this diff — left per surgical-changes guideline):**

- `chooseFromExisting` is only reset in the new-question branch of `watch(show)`, not on
  edit-open. Same structure existed before this refactor.
- `<style>` radio override uses `theme('colors.gray.900')` instead of a brand token.

**NIT (already fixed, committed ed3a586c):** ordinal label concatenation replaced with
`__('Option {0}', [n])` / `__('Possibility {0}', [n])`.

## Post-review fixes (independent review: C1 Critical, I1 Important, M2 cleanup)

Commit `9d016c45` — `fix(quiz-fe): monotonic row-count watch + scope frappe-ui test mock`

### C1 (Critical, FIXED) — deep watch caused a new add-row regression

The `{ deep: true }` watch (from 6abe3e1a) recomputed the visible count via
`Math.max(...)` on **every** mutation, including keystrokes. Sequence that broke:
"Add Option" → count 3, `option_3` still null → type in any field → watch fires →
`Math.max(2,1,2,0) = 2` → count snaps back to 2 and the just-added empty row vanishes.

Fix = grow-only recompute. Keep `{ immediate: true, deep: true }`, but only ever
**raise** the count, never lower it. `removeOption`/`removePossibility` keep their
explicit decrements, so deletion still works and added-empty rows are preserved.

ChoicesAuthor.vue:
```js
const populated = Math.max(
	2,
	...Array.from({ length: MAX_OPTIONS }, (_, i) =>
		q[`option_${i + 1}`] ? i + 1 : 0,
	),
)
if (populated > visibleOptionCount.value) visibleOptionCount.value = populated
```
UserInputAuthor.vue — identical pattern with `possibility_${i+1}`, floor `1`, and
`visiblePossibilityCount`.

### I1 (Important, FIXED) — global frappe-ui mock alias had too broad a blast radius

The `find: /^frappe-ui$/` alias in `vitest.config.ts` injected the stub into **all**
test files, so any spec importing frappe-ui transitively would silently get stubbed
`createResource` (data:null) / div components → risk of false greens.

- **Reverted** `vitest.config.ts` to its exact original (object-form `@` alias only;
  `git diff` confirms it matches `09141429`).
- **Mock now lives** as an explicit `vi.mock('frappe-ui', () => ({...}))` factory at the
  top of `src/tests/questionTypes.test.ts` — the only spec that transitively imports the
  author components via `@/questionTypes`. Factory stubs only `FormControl`, `Button`
  (author components) and `Switch` (BooleanSwitch) — the full set of frappe-ui named
  imports in that module graph. The test never mounts, so template-string stubs suffice.
- **Deleted** the now-unused `src/__mocks__/frappe-ui.ts` (it lived under `src/`, not
  adjacent to `node_modules`, so Vitest never auto-applied it; nothing imports it now).
- **Confirmed** the other 17 test files still pass after the revert — proving none of
  them depended on the global alias.

### M2 (cleanup) — NOT reverted; explanation

The trailing-comma changes on the three `submit()` call objects in `Question.vue` are
**not** discretionary churn — they are produced by the repo's own PostToolUse
`format-on-edit.sh` hook, which runs `prettier --write` on every edited `.vue` file.
Verified facts:
- Local `.prettierrc` is `{ semi:false, singleQuote:true }`; Prettier 3.8.1 defaults
  `trailingComma` to `"all"`, which adds trailing commas to multiline call args.
- `npx prettier --check` on the comma-less variant **fails** (Prettier wants them).
- The pre-task base file (`8c8a3296`) was **already** prettier-noncompliant — the repo
  ships noncompliant, and my legitimate edits triggered the hook to bring the whole file
  CI-clean.

Reverting would be auto-undone by the hook on the next edit and would leave the file
failing `prettier --check`. Per CLAUDE.md the project formatter wins where it conflicts,
so the commas stay. (A truly minimal diff would require a separate prior format-only
commit on the base, which is out of scope.)

### Verification

```
$ npx vitest run
 Test Files  18 passed (18)
      Tests  134 passed (134)

$ npx vitest run src/tests/questionTypes.test.ts   # 7/7 pass
$ npx prettier --check <all changed files>          # all clean
```

## Final commits

- `d705236e` refactor(quiz-fe): host per-type author components in Question modal
- `ed3a586c` fix(quiz-fe): i18n placeholders + aria-labels in author components
- `6abe3e1a` fix(quiz-fe): deep-watch question in author components so edit restores rows
- `9d016c45` fix(quiz-fe): monotonic row-count watch + scope frappe-ui test mock
