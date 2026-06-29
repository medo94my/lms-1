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

Reviewer reports from vue-frontend-reviewer and rtl-i18n-reviewer are running in background;
findings will be addressed if any blocking issues are surfaced before commit.
