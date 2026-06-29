# Secure Player Config Fetch — Design

**Date:** 2026-06-29
**Base branch:** basiret-redesign (7 question types merged, commit 0d920870)
**Status:** Approved (design); implementation plan + execution to run in a FRESH session

## Problem

`get_quiz_with_questions` (`lms/lms/utils.py`) sends each question's raw `data`
JSON field to the learner-facing player. For the `data`-based types
(Fill-in-the-blank, Matching, Ordering, True/False) that JSON **contains the
answer key** (fill-blank `accepted`, matching `pairs` left→right, ordering
`items` in correct order, true/false `correct`). A learner can read answers from
the page/network. Scoring is server-side and trustworthy, but the leak lets
someone cheat. The flat-column types (Choices / User Input / Open Ended) are
already safe — `get_quiz_with_questions` fetches `QUESTION_OPTION_FIELDS` and
`QUESTION_EXPLANATION_FIELDS` but NOT `QUESTION_CORRECTNESS_FIELDS`.

## Approach (chosen): per-type `player_config()`

Add a method to the `QuestionType` contract
(`lms/lms/question_types/base.py`):

```python
def player_config(self, question) -> dict:
    """Render data the learner-facing player needs, WITH THE ANSWER KEY REMOVED.
    Default: expose nothing from data."""
    return {}
```

`get_quiz_with_questions` replaces each question row's `data` with the sanitized
config before returning: `row["data"] = get_question_type(row["type"]).player_config(row)`
(keep the key name `data` so the frontend `parseConfig` keeps working; it now
parses the sanitized shape). The fetch still includes the raw `data` column to
feed `player_config`, but the raw value never leaves the server.

### Per-type `player_config` outputs

| Type | Returns | Answer key removed |
|---|---|---|
| Choices / User Input / Open Ended | `{}` | n/a (flat columns; correctness never sent) |
| True/False | `{}` | `correct` hidden (player renders True/False buttons) |
| Fill in the Blank | `{ "blanks": [{ "label": b.label }] }` | `accepted` stripped |
| Matching | `{ "lefts": [p.left, …], "rights": shuffle([p.right, …]) }` | left→right pairing removed; rights become an unordered pool |
| Ordering | `{ "items": shuffle([…]) }` | correct order hidden (server-shuffled) |

Shuffle server-side (Python `random` is fine — it is not security-sensitive
beyond hiding order; the answer key is already absent).

## Scope decision: reveal shows ✓/✗ only

Today the players show the **correct answer text** on reveal (e.g. Fill-blank
"Accepted: X", Matching correct pairing, Ordering correct order), read from the
client `data`. Removing the answer key from the client means the reveal can no
longer show that text from the client. For this fix, **reveal shows only
per-element ✓/✗** (which already comes from server `live_check`). Showing the
correct-answer *text* on reveal is DEFERRED — it would require the server to
return correct answers in the `check_answer`/`submit` response (a later
enhancement). This keeps the fix contained.

## Frontend player adaptations (consume the sanitized shape)

- **MatchingPlayer:** read `{ lefts, rights }` instead of `{ pairs }`. Dropdown
  options = `rights` (already shuffled server-side → remove the client-side
  shuffle/`onMounted` shuffledRights). Lefts shown from `lefts`. Reveal = ✓/✗
  only (drop the "correct pairs" block).
- **OrderingPlayer:** read server-shuffled `{ items }`. `state.order` initializes
  to `items` (already shuffled) — remove the client-side shuffle + re-shuffle
  loop. Reveal = ✓/✗ only.
- **FillBlankPlayer:** render from `{ blanks: [{label}] }` (already does). Drop
  the "Accepted: …" reveal block (no `accepted` on the client).
- **TrueFalsePlayer:** unchanged (reads nothing from `data`); drop any
  client-side explanation-on-reveal (explanation no longer sent).
- **Authoring is untouched** — Author components still read/write the full
  `data` via `frappe.client.get` (the doc fetch for editing returns the real
  doc; only the quiz-player fetch is sanitized). NOTE for the plan: confirm the
  author edit path (`Question.vue` `questionData` resource via
  `frappe.client.get`) still returns the full `data` — it should, since
  sanitization is only in `get_quiz_with_questions`.

## Testing / success criteria

- **Backend:** unit tests that `player_config` omits the answer key for each
  data-based type: Fill-blank result has `blanks` labels but no `accepted`;
  Matching has `lefts` + `rights` but no `pairs`/pairing; Ordering has `items`
  but not guaranteed-correct order; True/False returns `{}`. A test that
  `get_quiz_with_questions` returns sanitized `data` (no answer key) for a
  data-based question. Existing scoring/`live_check`/drift tests unchanged
  (server-side scoring is authoritative and untouched). `test_lms_quiz.py` /
  `test_api.py` stay green.
- **Frontend:** Vitest — players render from the sanitized shape; getAnswers
  still fixed-length. Manual preview: author (full config), then as learner the
  page/network contains no answer key; ✓/✗ reveal still works; scoring correct.

## Non-goals / deferred

- Correct-answer **text** on reveal (needs a server reveal-payload) — deferred.
- No change to scoring, `live_check` correctness, or authoring.
- No change to the flat-column types' behavior.

## Implementation note

This is a cross-cutting change (contract method + 4 `player_config` + 1 util +
4 player components + tests). Plan as backend + frontend split, executed
subagent-driven, like the prior three sub-projects. Backend tests are CI-only
(no local bench); frontend uses Vitest. Watch for: keeping the `data` key name
so `parseConfig` works; the author edit path must still get full `data`; the
Matching/Ordering players must drop their now-redundant client-side shuffles.
