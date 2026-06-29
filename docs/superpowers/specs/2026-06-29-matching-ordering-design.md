# New Question Types — Matching + Ordering — Design

**Date:** 2026-06-29
**Base branch:** basiret-redesign (question-type framework + 5 types merged, commit d0e9b6ad)
**Status:** Approved (design); implementation plan to follow

## Context

The question-type framework
([spec](2026-06-29-question-type-framework-design.md)) and five types (Choices,
User Input, Open Ended, True/False, Fill in the Blank) are merged. This
sub-project adds the two interactive types — **Matching** and **Ordering** — as
plugins. The framework changes they need already exist (fractional scoring via
`score()` returning a float `[0,1]`; the `LMS Question.data` JSON field;
registry-driven `questionTypeOptions()`; the `has_live_check`/`hasLiveCheck`
live-check gate; `data` included in the player fetch). So **no framework changes
are required** — these are pure drop-in plugins.

### Existing facts to reuse (ground truth)

- `vuedraggable@4.1.0` is already a frontend dependency (drag-to-reorder).
- `Quiz.vue` has a Fisher–Yates `shuffleArray` helper (used for
  `shuffle_questions`); the new players replicate that pattern to shuffle options.
- Plugin contract: backend `validate`/`score`/`live_check`/`read_config`
  (`lms/lms/question_types/base.py`); frontend `QuestionTypeDef`
  (`name`/`label`/`autoGraded`/`hasLiveCheck`/`defaultConfig`/`getAnswers`/
  `loadAnswer`/`AuthorComponent`/`PlayerComponent`).
- `getAnswers` must return a FIXED-LENGTH array (one entry per element, `''`/empty
  for unanswered) so `Quiz.vue`'s `.filter(a => a !== null && a !== undefined)`
  never shortens it and backend per-element indices stay aligned.
- `check_answer`'s live-check payload surfaces in the player as `showAnswers[0]`
  for non-Choices types (per the framework's `Quiz.vue` `checkAnswer` else-branch).

## Scope

**In scope:** the **Matching** and **Ordering** plugins (backend + frontend),
registered alongside the existing five; both `autoGraded: true`,
`hasLiveCheck: true`, fractional scoring. Add `Matching` and `Ordering` to the
`type` Select options in BOTH `lms_question.json` and `lms_quiz_question.json`,
and to both registries (drift guard).

**Out of scope:** framework changes (none needed); other types; UX polish;
distractor right-options (Matching is strict 1:1).

## Type: Matching (dropdown-per-left, strict 1:1)

- **Storage (`data`):** `{ "pairs": [{ "left": str, "right": str }, ...] }` —
  the author's correct left↔right pairs. Right values are assumed **distinct**
  (value-equality scoring).
- **Backend plugin:**
  - `validate`: at least two pairs; every pair has a non-empty `left` and
    non-empty `right`.
  - `score(question, answer)`: `answer[i]` is the learner's chosen right for
    `pairs[i].left` (left order). `fraction = (# i where answer[i] == pairs[i].right) / len(pairs)`.
  - `live_check`: per-left correctness `list[int]` (1 if `answer[i] ==
    pairs[i].right`).
  - `read_config`: parses `data.pairs`.
- **Frontend:**
  - `AuthorComponent`: ordered list of pairs; per pair a left input + right
    input; add/remove pair; a hint that right values should be distinct.
  - `PlayerComponent`: left items in author order; each row has a **dropdown**
    whose options are all `right` values **shuffled** (Fisher–Yates). On reveal:
    per-left ✓/✗ + the correct right.
  - `defaultConfig`: `{ data: { pairs: [{ left: '', right: '' }, { left: '', right: '' }] } }`.
  - `getAnswers(question, state)`: `pairs.map((_, i) => state?.selections?.[i] ?? '')`
    (fixed length, in left order).
  - `loadAnswer(_q, saved)`: `{ selections: saved ?? [] }`.
- `autoGraded: true`, `hasLiveCheck: true`.

## Type: Ordering (drag-to-reorder, absolute-position)

- **Storage (`data`):** `{ "items": [str, ...] }` in the **correct** order.
  Item values are assumed **distinct**.
- **Backend plugin:**
  - `validate`: at least two items; all non-empty.
  - `score(question, answer)`: `answer` is the learner's ordered item list.
    `fraction = (# positions i where answer[i] == items[i]) / len(items)`
    (absolute position).
  - `live_check`: per-position correctness `list[int]`.
  - `read_config`: parses `data.items`.
- **Frontend:**
  - `AuthorComponent`: ordered list of item inputs (add/remove/reorder); the
    saved order is the correct order.
  - `PlayerComponent`: items shown **shuffled** (re-shuffle if the shuffle equals
    the correct order); learner reorders via **`vuedraggable`**, AND each row has
    **up/down arrow buttons** as a keyboard/RTL-safe fallback (drag alone has weak
    a11y). On reveal: per-position ✓/✗.
  - `defaultConfig`: `{ data: { items: ['', ''] } }`.
  - `getAnswers(question, state)`: the learner's current ordered list
    (`state?.order ?? []`), length == items count.
  - `loadAnswer(_q, saved)`: `{ order: saved ?? [] }`.
- `autoGraded: true`, `hasLiveCheck: true`.

## Data flow (both types)

Author writes config (AuthorComponent → `question.data`) → stored on
`LMS Question` → player reads `data` (via the existing `data`-in-fetch util),
shuffles presentation, builds the fixed-length answer array via `getAnswers` →
`submit_quiz` / `check_answer` dispatch to the backend plugin's `score` /
`live_check` (fractional) → submission aggregates fractional marks.

## Edge cases

- **Distinct values:** Matching right values and Ordering items are assumed
  distinct (scoring compares by value). The author UI notes this; non-distinct
  values are not rejected but may score ambiguously.
- **Ordering shuffle:** if the shuffled presentation equals the correct order,
  re-shuffle (avoid a trivially-correct initial state). For a 1-item list (not
  allowed by `validate`) this would loop — `validate` requires ≥2 items.
- **Unanswered:** Matching unselected dropdowns yield `''` (scored wrong, length
  preserved). Ordering always has all items present (only the order varies).

## Testing / success criteria

- **Backend:** per-plugin `validate` (rejects <2 pairs/items or empty),
  `score` (full / partial / zero — e.g. ordering 3-of-5 → 0.6, matching 1-of-2 →
  0.5), `live_check` per-element. Existing tests stay green; the registry↔DocType
  drift guard updated to include `Matching` and `Ordering`.
- **Frontend:** Vitest for each type's `getAnswers` (fixed-length alignment,
  empty-for-unanswered) and `loadAnswer`. The `vuedraggable` reorder + up/down
  buttons verified manually in the preview (drag isn't unit-tested).

## Non-goals

- No framework changes.
- No distractor right-options (strict 1:1 matching).
- No adjacency-based ordering score (absolute position only).
- No change to existing types.
