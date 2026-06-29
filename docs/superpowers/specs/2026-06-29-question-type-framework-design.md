# Reusable Question-Type Framework — Design

**Date:** 2026-06-29
**Branch:** basiret-redesign
**Status:** Approved (design); implementation plan to follow

## Context

The Frappe LMS rebrand (Basiret Vakfı) needs to grow well beyond the three
built-in quiz question types. Today a question type is hardcoded in several
places, so adding one is a multi-file, error-prone change. The user wants a
**reusable** way to add question types — "drop in a plugin," not edit the core.

This is the **keystone** sub-project. Authoring UX, learner UX, and every future
question type build on the contract defined here.

### How the existing system works (ground truth)

A question type's logic is hardcoded at **four dispatch points**:

1. `lms/lms/doctype/lms_question/lms_question.py` → `validate_correct_answers()`
   — authoring-time validation, branches on `type`.
2. `lms/lms/doctype/lms_quiz/lms_quiz.py` → `submit()` (~line 160) — final
   scoring, branches Open Ended / User Input / Choices.
3. `lms/lms/doctype/lms_quiz/lms_quiz.py` → `check_answer()` (~line 300) — live
   "check my answer" feedback, branches on `type`.
4. Frontend `frontend/src/components/Modals/Question.vue` (authoring UI) and the
   learner player component (answering UI).

Answer data is stored as flat columns on `LMS Question`:
`option_1..10`, `is_correct_1..10`, `explanation_1..10`, `possibility_1..10`
(see `QUESTION_*_FIELDS` lists in `lms_question.py`).

`type` is a fixed Select (`Choices`, `User Input`, `Open Ended`) duplicated in
`LMS Question` and the `LMS Quiz Question` child table, plus hardcoded in
`Question.vue`.

Scoring details that MUST be preserved verbatim:
- Choices: multiple-correct → `multiple=1`; exact set match for multiple.
- User Input: fuzzy match via `fuzz.token_sort_ratio(...) > 85`.
- Open Ended: manual grading; answer sanitized + data-URL images extracted.
- Negative marking: `-marks_to_cut` when enabled and answer wrong.

## Scope

**In scope (this spec):**
- The extensibility framework (backend registry + frontend registry + contract).
- Re-implementing the existing 3 types through it with **zero behavior change**.

**Deferred (separate specs, each builds on this one):**
- New concrete types: True/False, Fill-in-the-blank, Matching/pairs, Ordering.
- Reusable *assessment kinds* (quiz / assignment / programming → more).
- Dummy-proof UX polish for authors and learners.

## Decisions

- **Storage: Approach A (hybrid).** Add one structured `data` (JSON) field to
  `LMS Question`. New types store their answer schema there. The existing 3 types
  keep using `option_1..10` etc. **No migration of live data up front.** A
  later, isolated, separately-tested task may unify storage.
- **Sequencing:** framework first; prove via existing tests; new types after.

## The type contract

One plugin = a backend part + a frontend part.

### Backend plugin — `lms/lms/question_types/<type>.py`

Each type exposes:
- `name` / `label`
- `validate(question)` — authoring-time checks (replaces dispatch point 1).
- `score(question, answer)` — final grading → marks/correctness (point 2).
- `live_check(question, answer)` *(optional)* — live feedback (point 3); types
  without it simply offer no live checking.
- `read_config(question)` — returns the type's answer data from **either** the
  legacy `option_1..10` columns (existing types) **or** the new `data` field
  (new types). This is the hybrid seam.

### Frontend plugin — `frontend/src/questionTypes/<type>.ts`

Each type registers:
- `label`, `defaultConfig`
- `AuthorComponent` — create/edit UI (rendered by `Question.vue`).
- `PlayerComponent` — learner answering UI (rendered by the player host).

## Backend changes

1. Add `data` (JSON) field to `LMS Question`. Existing types ignore it.
2. Build a registry (`lms/lms/question_types/__init__.py`) mapping
   `type → plugin`.
3. Replace the four branch points with `registry[type].method(...)`. The
   existing Choices / User Input / Open Ended logic moves **verbatim** into three
   plugin classes — same thresholds, negative marking, multiple-correct logic.
   No logic rewrite, only relocation behind the dispatch.
4. `type` allowed values come from the registry rather than a fixed Select, so a
   future type needs no DocType edit.

## Frontend changes

1. A type registry mirroring the backend.
2. `Modals/Question.vue` becomes a thin **host**: pick type → render that type's
   `AuthorComponent`. Current per-type markup moves into three author components.
3. The learner player becomes a host rendering the type's `PlayerComponent`.

## Migration / compatibility

**None up front.** Existing questions stay in `option_1..10`; their plugins'
`read_config` reads those columns. This makes "zero behavior change" literal and
keeps the foundational change off live data.

## Testing / success criteria

- The existing `lms/lms/doctype/lms_quiz/test_lms_quiz.py` cases (10-option
  scoring, legacy 2-option, 7th-possibility fuzzy match) **pass untouched**.
  This is the primary success criterion.
- Add registry-level tests: unknown type raises clearly; each registered type
  round-trips validate → score.
- Frontend: existing quiz authoring + answering behave identically.

## Non-goals

- No new question types in this spec.
- No storage migration of existing questions.
- No UX redesign beyond what the host-component refactor necessarily touches.
