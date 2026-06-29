# New Question Types — True/False + Fill-in-the-blank — Design

**Date:** 2026-06-29
**Base branch:** basiret-redesign (question-type framework already merged, commit 108b191c)
**Status:** Approved (design); implementation plan to follow

## Context

The reusable question-type framework
([spec](2026-06-29-question-type-framework-design.md)) is merged. Each type is a
plugin: backend `validate` / `score` / `live_check` / `read_config`; frontend
`AuthorComponent` / `PlayerComponent` + `getAnswers` / `loadAnswer` / `defaultConfig`.
New types store their answer schema in the `LMS Question.data` JSON field
(existing types keep `option_1..10`).

This sub-project adds the **two simpler new types** — **True/False** and
**multi-blank Fill-in-the-blank** — and makes the framework changes those types
require. Matching and Ordering are a later, separate spec.

### Existing constraints discovered (ground truth)

- Submission scoring uses `cint(row.marks)` and the fields
  `LMS Quiz Submission.score` / `score_out_of` / `percentage` are **`Int`**
  (`lms/lms/doctype/lms_quiz_submission/lms_quiz_submission.py:37,46,49`). Integer
  truncation would silently destroy partial credit, so partial credit requires
  these to become `Float`.
- The framework's `score()` currently returns `bool`; `submit()` awards full
  marks or `-marks_to_cut`/0 (`lms/lms/doctype/lms_quiz/lms_quiz.py`).
- The live-check gate is still a hardcoded string: frontend
  `Quiz.vue` (`questionDetails.data.type != 'Open Ended'`) and backend
  `check_answer` has no gate. `questionTypeOptions()` returns `d.label`.

## Scope

**In scope:**
- Framework touch-ups (below).
- **True/False** question type (plugin: backend + frontend).
- **Fill-in-the-blank** (multi-blank, separate-list model) question type.

**Out of scope (later specs):** Matching/pairs, Ordering/sequence, UX polish.

## Framework touch-ups (prerequisites)

1. **Fractional scoring contract.** `QuestionType.score()` returns a float in
   `[0, 1]`. Existing plugins return `1.0` / `0.0` (Choices, User Input);
   Open Ended still returns `None` (manual). `submit()` computes
   `earned = flt(fraction * question.marks)` (no rounding — the marks field is
   now Float); negative marking applies only when `fraction == 0`. `is_correct = 1` only when `fraction == 1`
   (partial → `0`), preserving the existing ✓/✗ reveal semantics.
2. **Float score fields.** Change `LMS Quiz Submission.score`, `score_out_of`,
   `percentage`, and the result child row `marks` from `Int` to `Float`; switch
   `cint(...)` → `flt(...)` in `validate_marks` / `set_percentage`. Int→Float is
   storage-compatible; **no data migration**. Score display may now show
   decimals.
3. **Registry-driven type options.** `questionTypeOptions()` returns `name`
   (not `label`). The backend registry drift-guard test still asserts the
   DocType Select options equal the registry names.
4. **Registry-driven live-check gate.** Replace the hardcoded
   `type != 'Open Ended'` checks: frontend gates the "Check" button on
   `getQuestionType(type).hasLiveCheck`; backend `check_answer` raises a clean
   error (or no-ops) when `not get_question_type(type).has_live_check`. Both new
   types set `has_live_check = true` / `hasLiveCheck = true`.

## Type: True/False

- **Storage (`data`):** `{ "correct": true | false, "explanation": "<optional>" }`.
- **Backend plugin:**
  - `validate`: ensure `data.correct` is a boolean.
  - `score(question, answer)`: `1.0` if `answer[0]` (`"true"`/`"false"`) maps to
    `data.correct`, else `0.0`.
  - `live_check`: returns chosen-vs-correct (1/0).
  - `read_config`: parses `data`.
- **Frontend:**
  - `AuthorComponent`: choose correct answer (True / False) + optional explanation.
  - `PlayerComponent`: two selectable options; reveal shows correct + explanation.
  - `defaultConfig`: `{ correct: true, explanation: '' }`.
  - `getAnswers(state)`: `[state.choice]` (`"true"`/`"false"`).
  - `loadAnswer(savedAnswers)`: `{ choice: savedAnswers[0] ?? null }`.
- `autoGraded: true`, `hasLiveCheck: true`.

## Type: Fill-in-the-blank (multi-blank, separate-list)

- **Storage (`data`):**
  `{ "blanks": [ { "label": "1", "accepted": ["water", "H2O"] }, ... ] }`.
  The prompt remains normal rich text; the author may reference "(1), (2)" in the
  prompt text.
- **Matching semantics:** a blank is correct if the learner's value equals any
  `accepted` entry, compared **case-insensitively and trimmed** (not the fuzzy
  85% used by User Input — too loose for short fill-blank answers).
- **Backend plugin:**
  - `validate`: at least one blank; each blank has at least one non-empty
    accepted answer.
  - `score(question, answer)`: `fraction = (# correct blanks) / (# blanks)`,
    where `answer` is the per-blank value array.
  - `live_check`: returns a per-blank correctness array.
  - `read_config`: parses `data.blanks`.
- **Frontend:**
  - `AuthorComponent`: ordered list of blanks; per blank, one or more accepted
    answers; add/remove blank.
  - `PlayerComponent`: renders the prompt, then a labeled input per blank
    ("Blank 1 …"); reveal marks each blank ✓/✗ and shows accepted answer(s).
  - `defaultConfig`: `{ blanks: [{ label: '1', accepted: [] }] }`.
  - `getAnswers(state)`: array of per-blank strings.
  - `loadAnswer(savedAnswers)`: `{ values: savedAnswers ?? [] }`.
- `autoGraded: true`, `hasLiveCheck: true`.

## Data flow (both types)

Author writes prompt (shared rich text) + type config (AuthorComponent → `data`)
→ stored on `LMS Question` → player reads `data`, builds the answer array via the
type's `getAnswers` → `submit_quiz` / `check_answer` dispatch to the backend
plugin's `score` / `live_check` (fractional) → submission aggregates fractional
marks (Float).

## Testing / success criteria

- **Backend:** unit tests for each new plugin's `validate` (rejects bad config),
  `score` (incl. partial fractions for fill-blank: 0, 0.5, 1.0), and `live_check`.
  A test proving fractional marks aggregate correctly end-to-end (the Float
  change), e.g. a 3-blank, 3-mark question with 2 correct → 2.0 marks and correct
  percentage. Existing `test_lms_quiz.py` stays green.
- **Frontend:** Vitest for each type's `getAnswers` / `loadAnswer`; registry
  drift-guard updated to include `True/False` and `Fill in the Blank`.
- **Manual (preview):** author + answer + reveal for both types; partial-credit
  score shows correctly.

## Non-goals

- No Matching/Ordering.
- No drag-and-drop interactions.
- No fuzzy matching for fill-blank (case-insensitive exact only).
- No change to existing types' behavior or storage.
