# Secure Player Config Fetch Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stop the learner-facing quiz fetch from sending answer keys to the browser by sanitizing each question's `data` through a per-type `player_config()` method.

**Architecture:** Add `player_config(self, question) -> dict` to the backend `QuestionType` contract (default `{}`). The four `data`-based types (True/False, Fill-in-the-blank, Matching, Ordering) override it to return only what the player needs to render, with the answer key removed. `get_quiz_with_questions` (`lms/lms/utils.py`) replaces each question row's raw `data` with `player_config(row)` before returning, keeping the key name `data` so the frontend `parseConfig` keeps working. Frontend players adapt to the sanitized shapes; authoring is untouched (it fetches the full doc via `frappe.client.get`).

**Tech Stack:** Python (Frappe), Vue 3 `<script setup>` + frappe-ui, Vitest (frontend unit), Frappe test runner (backend, CI-only).

## Global Constraints

- **Keep the `data` key name** in the fetch response — the frontend `parseConfig(question)` reads `question.data`; do not rename it. Spec §"Approach".
- **`getAnswers` must return a FIXED-LENGTH array** (one entry per element, `?? ''` for unanswered) so `Quiz.vue`'s `.filter(a => a !== null && a !== undefined)` keeps per-element indices aligned with the backend. Existing convention.
- **`parseConfig` tolerates `data` as object OR JSON string** — already implemented; do not change it.
- **Authoring is untouched.** Only `get_quiz_with_questions` is sanitized. The author edit path (`frontend/src/components/Modals/Question.vue:128-129`, `frappe.client.get`) returns the full doc — confirmed during planning.
- **Reveal shows ✓/✗ ONLY.** Drop client-side correct-answer-text on reveal (Matching correct pairs, Fill-blank "Accepted:"). Correct-answer *text* on reveal is DEFERRED. Spec §"Scope decision".
- **No change to scoring, `live_check` correctness, or the flat-column types' behavior.** The backend scoring helpers read the real `data` from the DB by question name, unaffected by the fetch sanitization.
- **Python import order (ruff isort):** stdlib group, then third-party, then first-party, each separated by a blank line. Adding `import random` to a plugin means a new stdlib group ABOVE `import frappe`.
- **Frontend formatting:** Prettier 2.7.1 settings (`trailingComma: "es5"`) per `frontend/.prettierrc.json`. The format-on-edit hook handles this; do not hand-fight it.
- **Backend tests are CI-only** (no local bench). Local backend verification = `python -m py_compile <file>`. Frontend = `cd frontend && npx vitest run`.
- **Registry↔DocType drift guard** (`test_registry_matches_doctype_select_options`) is unaffected — this sub-project adds NO new types.

---

## File Structure

**Backend (modify):**
- `lms/lms/question_types/base.py` — add `player_config` default returning `{}`.
- `lms/lms/question_types/fill_blank.py` — override: `{ "blanks": [{ "label": ... }] }`.
- `lms/lms/question_types/matching.py` — override: `{ "lefts": [...], "rights": shuffle([...]) }` (+ `import random`).
- `lms/lms/question_types/ordering.py` — override: `{ "items": shuffle([...]) }` (+ `import random`).
- `lms/lms/utils.py` — `get_quiz_with_questions`: replace each row's `data` with `player_config(row)`.
- `lms/lms/question_types/test_question_types.py` — add `TestPlayerConfig` + sanitization integration test.

**Frontend (modify):**
- `frontend/src/questionTypes/matching.ts` — `getAnswers` length source `pairs` → `lefts`.
- `frontend/src/questionTypes/components/MatchingPlayer.vue` — consume `{lefts, rights}`, drop client shuffle, drop correct-answer reveal block.
- `frontend/src/questionTypes/components/OrderingPlayer.vue` — consume pre-shuffled `{items}`, drop client shuffle/re-shuffle loop.
- `frontend/src/questionTypes/components/FillBlankPlayer.vue` — drop the "Accepted:" reveal block.
- `frontend/src/tests/questionTypes.test.ts` — update Matching helper test to the sanitized shape; add sanitized-shape coverage for Ordering/FillBlank.

**No change (verified during planning):**
- `frontend/src/questionTypes/components/TrueFalsePlayer.vue` — reads nothing from `data`, no explanation-on-reveal code present. Verify-only.
- `frontend/src/questionTypes/ordering.ts` / `fillBlank.ts` `getAnswers` — read `items`/`blanks`, which survive sanitization. No change.
- All Author components — authoring path untouched.

---

## Task 1: Backend — per-type `player_config()` sanitizers

**Files:**
- Modify: `lms/lms/question_types/base.py`
- Modify: `lms/lms/question_types/fill_blank.py`
- Modify: `lms/lms/question_types/matching.py`
- Modify: `lms/lms/question_types/ordering.py`
- Test: `lms/lms/question_types/test_question_types.py`

**Interfaces:**
- Produces: `QuestionType.player_config(self, question) -> dict`. `question` is a row-like mapping with a `data` key holding the raw JSON (string or None), exactly as `frappe.get_all` returns it. Default returns `{}`. Overrides:
  - Fill in the Blank → `{"blanks": [{"label": <str>}, ...]}` (no `accepted`).
  - Matching → `{"lefts": [<str>, ...], "rights": [<str>, ...]}` where `rights` is a shuffled copy of the correct rights; no `pairs`, no left→right pairing.
  - Ordering → `{"items": [<str>, ...]}` shuffled away from the correct order for 2+ distinct items.
  - Choices / User Input / Open Ended / True/False → `{}` (inherit default).

- [ ] **Step 1: Write failing tests for all `player_config` sanitizers**

Append this class to `lms/lms/question_types/test_question_types.py` (the file already imports `json`, `unittest`, `frappe`, and `get_question_type`):

```python
class TestPlayerConfig(unittest.TestCase):
	def test_default_is_empty_for_flat_and_true_false_types(self):
		# Flat-column types and True/False expose nothing from data.
		self.assertEqual(get_question_type("Choices").player_config({"data": None}), {})
		self.assertEqual(get_question_type("User Input").player_config({"data": None}), {})
		self.assertEqual(get_question_type("Open Ended").player_config({"data": None}), {})
		tf = get_question_type("True/False")
		self.assertEqual(tf.player_config({"data": json.dumps({"correct": True})}), {})

	def test_fill_blank_keeps_labels_drops_accepted(self):
		qt = get_question_type("Fill in the Blank")
		row = {
			"data": json.dumps(
				{"blanks": [{"label": "1", "accepted": ["secret"]}, {"label": "2", "accepted": ["x"]}]}
			)
		}
		cfg = qt.player_config(row)
		self.assertEqual(cfg, {"blanks": [{"label": "1"}, {"label": "2"}]})
		self.assertNotIn("accepted", json.dumps(cfg))
		self.assertNotIn("secret", json.dumps(cfg))

	def test_matching_exposes_lefts_and_shuffled_rights_no_pairing(self):
		qt = get_question_type("Matching")
		row = {
			"data": json.dumps(
				{"pairs": [{"left": "France", "right": "Paris"}, {"left": "Japan", "right": "Tokyo"}]}
			)
		}
		cfg = qt.player_config(row)
		self.assertEqual(cfg["lefts"], ["France", "Japan"])
		self.assertEqual(sorted(cfg["rights"]), ["Paris", "Tokyo"])
		self.assertNotIn("pairs", cfg)
		# Only two keys — nothing that re-establishes the left->right mapping.
		self.assertEqual(set(cfg.keys()), {"lefts", "rights"})

	def test_ordering_shuffles_away_from_correct_order(self):
		qt = get_question_type("Ordering")
		correct = ["Mercury", "Venus", "Earth", "Mars"]
		row = {"data": json.dumps({"items": correct})}
		cfg = qt.player_config(row)
		self.assertEqual(sorted(cfg["items"]), sorted(correct))
		# Distinct 2+ items are guaranteed reordered.
		self.assertNotEqual(cfg["items"], correct)
		self.assertEqual(set(cfg.keys()), {"items"})
```

- [ ] **Step 2: Run the tests to verify they fail**

Run (CI, on PR): `bench --site frappe.local run-tests --app lms --module lms.lms.question_types.test_question_types`
Expected: FAIL — `player_config` is `AttributeError`/`NotImplementedError`-free only after implementation; the overrides return wrong shapes until implemented.
Local fallback: `python -m py_compile lms/lms/question_types/test_question_types.py` (syntax only).

- [ ] **Step 3: Add the `player_config` default to the base contract**

In `lms/lms/question_types/base.py`, add this method to the `QuestionType` class (after `read_config`):

```python
	def player_config(self, question) -> dict:
		"""Render the data the learner-facing player needs, WITH THE ANSWER KEY
		REMOVED. `question` is a row-like mapping whose `data` holds the raw JSON.
		Default: expose nothing from data."""
		return {}
```

- [ ] **Step 4: Override `player_config` in Fill in the Blank**

In `lms/lms/question_types/fill_blank.py`, add this method to `FillBlankQuestion` (after `live_check`):

```python
	def player_config(self, question) -> dict:
		blanks = frappe.parse_json(question.get("data") or "{}").get("blanks") or []
		return {"blanks": [{"label": b.get("label", "")} for b in blanks]}
```

- [ ] **Step 5: Override `player_config` in Matching**

In `lms/lms/question_types/matching.py`, add `import random` as a stdlib import group ABOVE `import frappe` (top of file becomes):

```python
# Copyright (c) 2026, Frappe and contributors
# For license information, please see license.txt

import random

import frappe
from frappe import _

from lms.lms.question_types.base import QuestionType
```

Then add this method to `MatchingQuestion` (after `live_check`):

```python
	def player_config(self, question) -> dict:
		pairs = frappe.parse_json(question.get("data") or "{}").get("pairs") or []
		lefts = [str(p.get("left") or "") for p in pairs]
		rights = [str(p.get("right") or "") for p in pairs]
		random.shuffle(rights)
		return {"lefts": lefts, "rights": rights}
```

- [ ] **Step 6: Override `player_config` in Ordering**

In `lms/lms/question_types/ordering.py`, add `import random` as a stdlib import group ABOVE `import frappe` (same pattern as Step 5). Then add this method to `OrderingQuestion` (after `live_check`):

```python
	def player_config(self, question) -> dict:
		items = [str(i) for i in (frappe.parse_json(question.get("data") or "{}").get("items") or [])]
		shuffled = items[:]
		# Avoid presenting the already-correct order for 2+ items. Bounded so a
		# list with duplicate values (which can never differ) cannot loop forever.
		for _attempt in range(10):
			random.shuffle(shuffled)
			if len(items) < 2 or shuffled != items:
				break
		return {"items": shuffled}
```

- [ ] **Step 7: Run the tests to verify they pass**

Run (CI, on PR): `bench --site frappe.local run-tests --app lms --module lms.lms.question_types.test_question_types`
Expected: PASS — all `TestPlayerConfig` cases plus the existing classes.
Local: `python -m py_compile lms/lms/question_types/base.py lms/lms/question_types/fill_blank.py lms/lms/question_types/matching.py lms/lms/question_types/ordering.py lms/lms/question_types/test_question_types.py`
Expected: no output (compiles clean).

- [ ] **Step 8: Commit**

```bash
git add lms/lms/question_types/base.py lms/lms/question_types/fill_blank.py lms/lms/question_types/matching.py lms/lms/question_types/ordering.py lms/lms/question_types/test_question_types.py
git commit -m "feat(quiz): add per-type player_config to strip answer keys"
```

---

## Task 2: Backend — sanitize `get_quiz_with_questions`

**Files:**
- Modify: `lms/lms/utils.py:1444-1476` (`get_quiz_with_questions`)
- Test: `lms/lms/question_types/test_question_types.py`

**Interfaces:**
- Consumes: `get_question_type(name)` from `lms.lms.question_types`; `QuestionType.player_config(row) -> dict` from Task 1.
- Produces: `get_quiz_with_questions(quiz)` returns `{"quiz": ..., "questions_by_name": {name: row}}` where each `row["data"]` is the sanitized dict from `player_config`, never the raw answer key.

- [ ] **Step 1: Write the failing sanitization test**

Append to `lms/lms/question_types/test_question_types.py`:

```python
class TestQuizFetchSanitizesAnswerKey(unittest.TestCase):
	def test_fetch_strips_fill_blank_answer_key(self):
		from lms.lms.utils import get_quiz_with_questions

		q = frappe.new_doc("LMS Question")
		q.question = "Capital of France is (1)"
		q.type = "Fill in the Blank"
		q.data = json.dumps({"blanks": [{"label": "1", "accepted": ["secretparis"]}]})
		q.save()
		quiz = frappe.new_doc("LMS Quiz")
		quiz.title = "Sanitize Quiz"
		quiz.passing_percentage = 50
		quiz.append("questions", {"question": q.name, "marks": 1})
		quiz.save()

		result = get_quiz_with_questions(quiz.name)
		row = result["questions_by_name"][q.name]
		serialized = json.dumps(row["data"])
		self.assertNotIn("secretparis", serialized)
		self.assertNotIn("accepted", serialized)
		self.assertIn("blanks", row["data"])

		frappe.delete_doc("LMS Quiz", quiz.name, force=True)
		frappe.delete_doc("LMS Question", q.name, force=True)
```

- [ ] **Step 2: Run the test to verify it fails**

Run (CI, on PR): `bench --site frappe.local run-tests --app lms --module lms.lms.question_types.test_question_types`
Expected: FAIL — the raw `data` (with `accepted`/`secretparis`) is still in the response.

- [ ] **Step 3: Wire sanitization into the fetch**

In `lms/lms/utils.py`, edit `get_quiz_with_questions`. Add the registry import next to the existing local import, and sanitize each row after `rows` is built. The function becomes:

```python
@frappe.whitelist()
def get_quiz_with_questions(quiz: str) -> dict:
	"""Return the quiz doc plus every question's details in a single round trip."""
	from lms.lms.doctype.lms_question.lms_question import (
		QUESTION_EXPLANATION_FIELDS,
		QUESTION_OPTION_FIELDS,
	)
	from lms.lms.question_types import get_question_type

	if not has_lms_role():
		frappe.throw(_("You are not authorized to view this quiz."))

	quiz_doc = frappe.get_doc("LMS Quiz", quiz).as_dict()

	question_names = [row.get("question") for row in quiz_doc.get("questions") or [] if row.get("question")]
	questions_by_name = {}
	if question_names:
		fields = [
			"name",
			"question",
			"type",
			"data",
			"multiple",
			*QUESTION_OPTION_FIELDS,
			*QUESTION_EXPLANATION_FIELDS,
		]
		rows = frappe.get_all(
			"LMS Question",
			filters=[["name", "in", question_names]],
			fields=fields,
			ignore_permissions=True,
		)
		for row in rows:
			# Replace the raw answer key with the type's sanitized player config.
			row["data"] = get_question_type(row["type"]).player_config(row)
		questions_by_name = {row["name"]: row for row in rows}

	return {"quiz": quiz_doc, "questions_by_name": questions_by_name}
```

- [ ] **Step 4: Run the tests to verify they pass**

Run (CI, on PR): `bench --site frappe.local run-tests --app lms --module lms.lms.question_types.test_question_types`
Expected: PASS — including the existing `TestQuizFetchIncludesData` (still finds `"data"` in the row, now `{}` for Choices) and the new `TestQuizFetchSanitizesAnswerKey`.
Local: `python -m py_compile lms/lms/utils.py`
Expected: no output.

- [ ] **Step 5: Commit**

```bash
git add lms/lms/utils.py lms/lms/question_types/test_question_types.py
git commit -m "feat(quiz): sanitize question data in get_quiz_with_questions"
```

---

## Task 3: Frontend — Matching player consumes `{lefts, rights}`

**Files:**
- Modify: `frontend/src/questionTypes/matching.ts:21-25` (`getAnswers`)
- Modify: `frontend/src/questionTypes/components/MatchingPlayer.vue`
- Test: `frontend/src/tests/questionTypes.test.ts:133-152` (Matching helpers)

**Interfaces:**
- Consumes: sanitized question shape `question.data = { lefts: string[], rights: string[] }` from Task 2.
- Produces: `Matching.getAnswers(question, state)` returns a fixed-length array of length `lefts.length`, `state.selections[i] ?? ''` per left.

- [ ] **Step 1: Confirm no other consumer reads the Matching answer key on the player side**

Run: `grep -rn "\.pairs\|\.accepted\|\.correct\b" frontend/src/components/Quiz.vue`
Expected: no matches that read a correct-answer field from `question.data` (Quiz.vue dispatches to per-type players; reveal data comes from server `showAnswers`). If a match appears, stop and report — it is an additional consumer the spec did not account for.

- [ ] **Step 2: Update the Matching helper test to the sanitized shape**

In `frontend/src/tests/questionTypes.test.ts`, replace the `describe('Matching helpers', ...)` block (lines 133-152) with:

```typescript
describe('Matching helpers', () => {
	// Player receives the sanitized shape: lefts + a shuffled rights pool, no pairs.
	const q = {
		data: {
			lefts: ['A', 'B'],
			rights: ['2', '1'],
		},
	}
	it('getAnswers returns one entry per left, empty for missing', () => {
		expect(
			getQuestionType('Matching').getAnswers(q, { selections: ['1'] })
		).toEqual(['1', ''])
	})
	it('loadAnswer restores selections', () => {
		expect(
			getQuestionType('Matching').loadAnswer(q, ['1', '2']).selections
		).toEqual(['1', '2'])
	})
})
```

- [ ] **Step 3: Run the Matching test to verify it fails**

Run: `cd frontend && npx vitest run src/tests/questionTypes.test.ts -t "Matching helpers"`
Expected: FAIL — `getAnswers` still keys off `parseConfig(question).pairs`, which is absent in the sanitized shape, so it returns `[]`.

- [ ] **Step 4: Update `getAnswers` to key off `lefts`**

In `frontend/src/questionTypes/matching.ts`, replace the `getAnswers` method (lines 21-25):

```typescript
	getAnswers(question, state) {
		const lefts = parseConfig(question).lefts || []
		const selections = state?.selections || []
		return lefts.map((_: any, i: number) => selections[i] ?? '')
	},
```

(Leave `defaultConfig`, `loadAnswer`, and the component imports unchanged — `defaultConfig` still produces `{ pairs: [...] }` for the *authoring* path, which is correct.)

- [ ] **Step 5: Run the Matching test to verify it passes**

Run: `cd frontend && npx vitest run src/tests/questionTypes.test.ts -t "Matching helpers"`
Expected: PASS.

- [ ] **Step 6: Rewrite `MatchingPlayer.vue` to consume `{lefts, rights}`**

Replace the entire contents of `frontend/src/questionTypes/components/MatchingPlayer.vue` with:

```vue
<template>
	<div class="space-y-3 mt-2">
		<div v-for="(left, i) in lefts" :key="i" class="flex items-center gap-3">
			<div class="flex-1 text-ink-gray-9" v-html="sanitizeRichHTML(left)" />
			<FormControl
				class="flex-1"
				type="select"
				:options="selectOptions"
				:model-value="selections[i] || ''"
				:disabled="showAnswers.length > 0"
				@update:model-value="(v) => setSelection(i, v)"
			/>
			<span
				v-if="showAnswers.length && perPair[i] === 1"
				class="lucide-check-circle w-4 h-4 text-ink-green-5"
			/>
			<span
				v-else-if="showAnswers.length && perPair[i] === 0"
				class="lucide-x-circle w-4 h-4 text-ink-red-6"
			/>
		</div>
	</div>
</template>
<script setup>
import { computed } from 'vue'
import { FormControl } from 'frappe-ui'
import { parseConfig } from '@/questionTypes/util'
import { sanitizeRichHTML } from '@/utils/sanitizeRichHTML'

const props = defineProps({
	question: { type: Object, required: true },
	showAnswers: { type: Array, default: () => [] },
	quizShowAnswers: { type: Boolean, default: false },
})
const state = defineModel('state')
const lefts = computed(() => parseConfig(props.question).lefts || [])
const rights = computed(() => parseConfig(props.question).rights || [])
const selections = computed(() => state.value?.selections || [])
const perPair = computed(() =>
	props.showAnswers.length ? props.showAnswers[0] || [] : []
)

// Rights arrive pre-shuffled from the server (player_config); use as-is.
const selectOptions = computed(() => [
	{ label: __('Select…'), value: '' },
	...rights.value.map((r) => ({ label: r, value: r })),
])

const setSelection = (i, v) => {
	const next = lefts.value.map((_, idx) => selections.value[idx] ?? '')
	next[i] = v
	state.value = { selections: next }
}
</script>
```

Changes vs. before: loops over `lefts` (strings) instead of `pairs`; dropdown options come from the server-shuffled `rights` (removed `onMounted`/`ref`/`shuffle` client shuffle); `setSelection` lengths off `lefts`; **removed the correct-answer reveal block** (the `v-for ... perPair[i] === 0 → "{left} → {right}"` rows) — reveal is ✓/✗ only. Removed now-unused imports (`ref`, `onMounted`, `shuffle`) and the `stripTags` helper.

- [ ] **Step 7: Run the full frontend suite**

Run: `cd frontend && npx vitest run`
Expected: PASS (all files). The Matching block now reflects the sanitized shape; no other test references `MatchingPlayer` internals.

- [ ] **Step 8: Commit**

```bash
git add frontend/src/questionTypes/matching.ts frontend/src/questionTypes/components/MatchingPlayer.vue frontend/src/tests/questionTypes.test.ts
git commit -m "feat(quiz): MatchingPlayer reads sanitized lefts/rights"
```

---

## Task 4: Frontend — Ordering player consumes pre-shuffled `{items}`

**Files:**
- Modify: `frontend/src/questionTypes/components/OrderingPlayer.vue`
- Test: `frontend/src/tests/questionTypes.test.ts:154-166` (Ordering helpers)

**Interfaces:**
- Consumes: sanitized question shape `question.data = { items: string[] }` already shuffled away from the correct order (Task 1, Ordering). `Ordering.getAnswers` is unchanged (keys off `items`, which survives sanitization).

- [ ] **Step 1: Verify the Ordering helper test already matches the sanitized shape**

The existing block (`frontend/src/tests/questionTypes.test.ts:154-166`) uses `const q = { data: { items: ['a', 'b', 'c'] } }` — already the sanitized shape. Leave it. Add one assertion documenting that `getAnswers` lengths off the server `items`. Replace the `describe('Ordering helpers', ...)` block with:

```typescript
describe('Ordering helpers', () => {
	// Player receives the sanitized shape: items pre-shuffled by the server.
	const q = { data: { items: ['a', 'b', 'c'] } }
	it('getAnswers returns the current order, fixed length', () => {
		expect(
			getQuestionType('Ordering').getAnswers(q, { order: ['b', 'a'] })
		).toEqual(['b', 'a', ''])
	})
	it('getAnswers length follows the server items, not the learner order', () => {
		expect(getQuestionType('Ordering').getAnswers(q, { order: [] })).toEqual([
			'',
			'',
			'',
		])
	})
	it('loadAnswer restores order', () => {
		expect(
			getQuestionType('Ordering').loadAnswer(q, ['c', 'b', 'a']).order
		).toEqual(['c', 'b', 'a'])
	})
})
```

- [ ] **Step 2: Run the Ordering test (expected PASS — getAnswers is unchanged)**

Run: `cd frontend && npx vitest run src/tests/questionTypes.test.ts -t "Ordering helpers"`
Expected: PASS — confirms the helper contract holds for the sanitized shape before touching the player.

- [ ] **Step 3: Drop the client-side shuffle in `OrderingPlayer.vue`**

In `frontend/src/questionTypes/components/OrderingPlayer.vue`, change the `<script setup>` so the initial order is the server-shuffled `items` (no client shuffle/re-shuffle). Replace the import line and the `watch` block.

Replace:

```javascript
import { computed, watch } from 'vue'
import { Button } from 'frappe-ui'
import draggable from 'vuedraggable'
import { parseConfig, shuffle } from '@/questionTypes/util'
import { sanitizeRichHTML } from '@/utils/sanitizeRichHTML'
```

with (drop `shuffle` from the import):

```javascript
import { computed, watch } from 'vue'
import { Button } from 'frappe-ui'
import draggable from 'vuedraggable'
import { parseConfig } from '@/questionTypes/util'
import { sanitizeRichHTML } from '@/utils/sanitizeRichHTML'
```

Replace the entire `watch(items, ...)` block:

```javascript
// Once items are available, shuffle them once if there is no restored order.
// Use a watch with immediate:true so async question props are also handled.
// Re-shuffle until result differs from correct order (guaranteed distinct for
// 2+ items after at most a few attempts).
watch(
	items,
	(newItems) => {
		if (!newItems.length || order.value.length) return
		let next = shuffle(newItems)
		while (newItems.length > 1 && next.every((v, i) => v === newItems[i]))
			next = shuffle(newItems)
		order.value = next
	},
	{ immediate: true }
)
```

with:

```javascript
// Items arrive pre-shuffled from the server (player_config). Seed the learner's
// working order from them, unless a saved answer was already restored.
watch(
	items,
	(newItems) => {
		if (!newItems.length || order.value.length) return
		order.value = [...newItems]
	},
	{ immediate: true }
)
```

(Leave the template, `move`, `order` computed, and `perPosition` unchanged — reveal is already ✓/✗ only.)

- [ ] **Step 4: Run the full frontend suite**

Run: `cd frontend && npx vitest run`
Expected: PASS (all files).

- [ ] **Step 5: Commit**

```bash
git add frontend/src/questionTypes/components/OrderingPlayer.vue frontend/src/tests/questionTypes.test.ts
git commit -m "feat(quiz): OrderingPlayer uses server-shuffled items"
```

---

## Task 5: Frontend — FillBlank player drops the "Accepted:" reveal

**Files:**
- Modify: `frontend/src/questionTypes/components/FillBlankPlayer.vue:23-29` (reveal block)
- Test: `frontend/src/tests/questionTypes.test.ts:112-131` (Fill in the Blank helpers)

**Interfaces:**
- Consumes: sanitized question shape `question.data = { blanks: [{ label }] }` (no `accepted`). `FillBlank.getAnswers` is unchanged (keys off `blanks`, which survives sanitization).

- [ ] **Step 1: Update the Fill-blank helper test to the sanitized shape**

In `frontend/src/tests/questionTypes.test.ts`, replace the `describe('Fill in the Blank helpers', ...)` block (lines 112-131) with (drop `accepted` from the fixture to mirror the sanitized shape):

```typescript
describe('Fill in the Blank helpers', () => {
	// Player receives the sanitized shape: labels only, no accepted answers.
	const q = {
		data: {
			blanks: [{ label: '1' }, { label: '2' }],
		},
	}
	it('getAnswers returns one entry per blank, empty for missing', () => {
		expect(
			getQuestionType('Fill in the Blank').getAnswers(q, { values: ['x'] })
		).toEqual(['x', ''])
	})
	it('loadAnswer restores values', () => {
		expect(
			getQuestionType('Fill in the Blank').loadAnswer(q, ['p', 'q']).values
		).toEqual(['p', 'q'])
	})
})
```

- [ ] **Step 2: Run the Fill-blank test (expected PASS — getAnswers unchanged)**

Run: `cd frontend && npx vitest run src/tests/questionTypes.test.ts -t "Fill in the Blank helpers"`
Expected: PASS — confirms the helper contract holds for the sanitized shape.

- [ ] **Step 3: Remove the "Accepted:" reveal block from `FillBlankPlayer.vue`**

In `frontend/src/questionTypes/components/FillBlankPlayer.vue`, delete the reveal block (lines 23-29):

```vue
			<div
				v-if="showAnswers.length && perBlank[i] === 0"
				class="text-xs text-ink-gray-6"
			>
				{{ __('Accepted:') }}
				<bdi>{{ (blank.accepted || []).join('، ') }}</bdi>
			</div>
```

After deletion, the `v-for` row keeps the label, the input, and the ✓/✗ spans only. The `blank` loop variable is still used for `:key`/label, so no other change is needed in `<script setup>`.

- [ ] **Step 4: Run the full frontend suite**

Run: `cd frontend && npx vitest run`
Expected: PASS (all files).

- [ ] **Step 5: Verify True/False player needs no change**

Run: `grep -n "data\|accepted\|correct\|explanation" frontend/src/questionTypes/components/TrueFalsePlayer.vue`
Expected: no reads of `question.data` / answer-key fields (it renders fixed True/False buttons and shows ✓/✗ from `showAnswers`). No edit required — this step is a confirmation only.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/questionTypes/components/FillBlankPlayer.vue frontend/src/tests/questionTypes.test.ts
git commit -m "feat(quiz): FillBlankPlayer drops accepted-answer reveal"
```

---

## Manual verification (after all tasks, in the preview)

1. As an author, create one of each data-based type (True/False, Fill-blank, Matching, Ordering). Confirm authoring still shows/saves the full config.
2. As a learner, open the quiz. In DevTools → Network, inspect the `get_quiz_with_questions` response: each question's `data` must contain NO answer key (no `accepted`, no `pairs`/pairing, no correct `items` order, no `correct`).
3. Answer and submit: scoring is correct (server-side, unchanged).
4. On reveal: per-element ✓/✗ shows; no correct-answer text leaks.

---

## Self-Review

**Spec coverage:**
- `player_config` contract method → Task 1 Step 3. ✓
- Per-type outputs (Fill-blank/Matching/Ordering/True-False/flat) → Task 1 Steps 3-6 + tests Step 1. ✓
- `get_quiz_with_questions` replaces `data` → Task 2 Step 3. ✓
- Reveal = ✓/✗ only → Matching reveal block removed (Task 3 Step 6), Fill-blank "Accepted:" removed (Task 5 Step 3); Ordering already ✓/✗. ✓
- MatchingPlayer reads `{lefts, rights}`, drop client shuffle → Task 3 Step 6. ✓
- OrderingPlayer reads pre-shuffled `{items}`, drop client shuffle/re-shuffle → Task 4 Step 3. ✓
- FillBlankPlayer drops "Accepted:" → Task 5 Step 3. ✓
- TrueFalsePlayer unchanged → Task 5 Step 5 (verify-only). ✓
- Authoring untouched → confirmed (Global Constraints); no author files modified. ✓
- Backend tests (player_config omits answer key; fetch sanitized) → Task 1 + Task 2 tests. ✓
- Frontend tests (players render from sanitized shape; getAnswers fixed-length) → Tasks 3-5 tests. ✓
- Deferred: correct-answer text on reveal → not implemented (per spec). ✓

**Extra coverage beyond the spec (justified):** the spec's `getAnswers` example for Matching kept `pairs`; planning found the sanitized shape removes `pairs`, so Matching `getAnswers` MUST switch to `lefts` (Task 3 Step 4) — otherwise answer alignment silently breaks. This is a correctness requirement implied by the sanitization, not scope creep.

**Placeholder scan:** none — every code step shows full code; every run step shows the command and expected result.

**Type consistency:** `player_config(self, question) -> dict` identical across base + 3 overrides; sanitized keys (`blanks`/`lefts`/`rights`/`items`) match between backend producers (Task 1), the util (Task 2), the frontend consumers (`parseConfig(...).lefts|rights|items|blanks`), and the tests. `getAnswers` length sources (`lefts`/`items`/`blanks`) all exist in the sanitized shape.
