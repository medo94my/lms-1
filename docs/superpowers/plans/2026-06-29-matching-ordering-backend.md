# Matching + Ordering — Backend Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the Matching and Ordering question-type plugins on the backend, registered alongside the existing five. No framework changes (fractional scoring, the `data` field, the live-check gate, and `data`-in-fetch already exist).

**Architecture:** Two new plugin classes in `lms/lms/question_types/`, mirroring the merged `fill_blank.py` exactly: read config from `LMS Question.data` (JSON), return a fractional `score` (`correct / total`) and a per-element `live_check` list. Both registered and added to the `type` Select in both DocTypes.

**Tech Stack:** Python 3.11+, Frappe; `bench run-tests` (CI only).

## Global Constraints

- **Zero behavior change for existing types.** `test_lms_quiz.py`, `test_api.py`, and existing `test_question_types.py` cases pass unmodified.
- **Fractional scoring (already in framework):** `score()` returns a float in `[0,1]`; `process_results` already multiplies by marks. Both new types return `correct/total`.
- **Matching:** strict 1:1 `{ "pairs": [{ "left", "right" }] }`; a pair is correct iff the learner's chosen right (selected from a dropdown — so an exact right string) equals `pairs[i].right` (strip, case-sensitive — NOT casefold, since the learner selects rather than types). Right values assumed distinct.
- **Ordering:** `{ "items": [...] }` in correct order; absolute-position scoring — position `i` correct iff `answer[i] == items[i]`. Items assumed distinct.
- **Drift guard:** the `LMS Question.type` Select options must equal the registry names. Add each new name to BOTH `lms_question.json` and `lms_quiz_question.json` `type` Select in the same task that registers the plugin.
- **Import order:** keep imports in `__init__.py` alphabetical (ruff isort runs in CI Linters and fails on unsorted imports — a prior task hit this).
- **Tests run in CI only** (no local bench). Per-task local check: `python -m py_compile` for `.py`, `python -c "import json; json.load(open(...))"` for `.json`. Verification gate = push → "Server Tests". Style: tabs.

---

## File Structure

- Create: `lms/lms/question_types/matching.py` — `MatchingQuestion`.
- Create: `lms/lms/question_types/ordering.py` — `OrderingQuestion`.
- Modify: `lms/lms/question_types/__init__.py` — import + register both (alphabetical import order).
- Modify: `lms/lms/question_types/test_question_types.py` — tests for both.
- Modify: `lms/lms/doctype/lms_question/lms_question.json` + `lms/lms/doctype/lms_quiz_question/lms_quiz_question.json` — add `Matching` and `Ordering` to the `type` Select.

---

## Task 1: MatchingQuestion plugin

**Files:**
- Create: `lms/lms/question_types/matching.py`
- Modify: `lms/lms/question_types/__init__.py`
- Modify: `lms/lms/doctype/lms_question/lms_question.json`, `lms/lms/doctype/lms_quiz_question/lms_quiz_question.json`
- Test: `lms/lms/question_types/test_question_types.py`

**Interfaces:**
- Produces: `class MatchingQuestion(QuestionType)`, `name="Matching"`, `is_auto_graded=True`, `has_live_check=True`. Config `{"pairs":[{"left","right"}]}`. `score`→float `correct/total`; `live_check`→`list[int]` per-left.

- [ ] **Step 1: Write the tests (append to test_question_types.py)**

```python
class TestMatchingPlugin(unittest.TestCase):
	def _q(self):
		q = frappe.new_doc("LMS Question")
		q.question = "Match capitals"
		q.type = "Matching"
		q.data = json.dumps(
			{"pairs": [{"left": "France", "right": "Paris"}, {"left": "Japan", "right": "Tokyo"}]}
		)
		q.save()
		return q

	def test_validate_requires_two_complete_pairs(self):
		q = frappe.new_doc("LMS Question")
		q.question = "Bad matching"
		q.type = "Matching"
		q.data = json.dumps({"pairs": [{"left": "France", "right": ""}]})
		self.assertRaises(frappe.ValidationError, q.save)

	def test_score_full_partial_zero(self):
		q = self._q()
		qt = get_question_type("Matching")
		self.assertEqual(qt.score(q.name, ["Paris", "Tokyo"]), 1.0)
		self.assertEqual(qt.score(q.name, ["Paris", "Berlin"]), 0.5)
		self.assertEqual(qt.score(q.name, ["", ""]), 0.0)
		frappe.delete_doc("LMS Question", q.name, force=True)

	def test_live_check_per_pair(self):
		q = self._q()
		qt = get_question_type("Matching")
		self.assertEqual(qt.live_check(q.name, ["Paris", "Berlin"]), [1, 0])
		frappe.delete_doc("LMS Question", q.name, force=True)
```

(`import json` and `from lms.lms.question_types import get_question_type` are already at the top of the test file from earlier work — verify; add if missing.)

- [ ] **Step 2: Implement the plugin**

Create `lms/lms/question_types/matching.py`:

```python
# Copyright (c) 2026, Frappe and contributors
# For license information, please see license.txt

import frappe
from frappe import _

from lms.lms.question_types.base import QuestionType


class MatchingQuestion(QuestionType):
	name = "Matching"
	label = "Matching"
	is_auto_graded = True
	has_live_check = True

	def validate(self, question) -> None:
		pairs = frappe.parse_json(question.get("data") or "{}").get("pairs") or []
		if len(pairs) < 2:
			frappe.throw(_("Add at least two pairs."))
		for pair in pairs:
			if not str(pair.get("left") or "").strip() or not str(pair.get("right") or "").strip():
				frappe.throw(_("Each pair needs a left and a right value."))

	def _pairs(self, question_name: str) -> list:
		data = frappe.db.get_value("LMS Question", question_name, "data")
		return frappe.parse_json(data or "{}").get("pairs") or []

	def _per_pair(self, question_name: str, answer: list) -> list:
		results = []
		for i, pair in enumerate(self._pairs(question_name)):
			given = str(answer[i]).strip() if i < len(answer) else ""
			correct = str(pair.get("right") or "").strip()
			results.append(1 if given and given == correct else 0)
		return results

	def score(self, question_name: str, answer: list) -> float:
		per_pair = self._per_pair(question_name, answer)
		if not per_pair:
			return 0.0
		return sum(per_pair) / len(per_pair)

	def live_check(self, question_name: str, answer: list) -> list:
		return self._per_pair(question_name, answer)
```

- [ ] **Step 3: Register + add the Select option**

In `lms/lms/question_types/__init__.py`, add the import in alphabetical position (between `fill_blank` and `open_ended`):

```python
from lms.lms.question_types.matching import MatchingQuestion
```

and add `register(MatchingQuestion)` with the other registrations.

In `lms/lms/doctype/lms_question/lms_question.json` and `lms/lms/doctype/lms_quiz_question/lms_quiz_question.json`, change the `type` field `options` from `"Choices\nUser Input\nOpen Ended\nTrue/False\nFill in the Blank"` to `"Choices\nUser Input\nOpen Ended\nTrue/False\nFill in the Blank\nMatching"`.

- [ ] **Step 4: Local checks**

Run: `python -m py_compile lms/lms/question_types/matching.py lms/lms/question_types/__init__.py`
Run: `python -c "import json; json.load(open('lms/lms/doctype/lms_question/lms_question.json')); json.load(open('lms/lms/doctype/lms_quiz_question/lms_quiz_question.json'))"`
Expected: exit 0.

- [ ] **Step 5: Commit**

```bash
git add lms/lms/question_types/matching.py lms/lms/question_types/__init__.py lms/lms/doctype/lms_question/lms_question.json lms/lms/doctype/lms_quiz_question/lms_quiz_question.json lms/lms/question_types/test_question_types.py
git commit -m "feat(quiz): add Matching question type plugin"
```

(No push yet — Task 2 pushes both.)

---

## Task 2: OrderingQuestion plugin

**Files:**
- Create: `lms/lms/question_types/ordering.py`
- Modify: `lms/lms/question_types/__init__.py`
- Modify: `lms/lms/doctype/lms_question/lms_question.json`, `lms/lms/doctype/lms_quiz_question/lms_quiz_question.json`
- Test: `lms/lms/question_types/test_question_types.py`

**Interfaces:**
- Produces: `class OrderingQuestion(QuestionType)`, `name="Ordering"`, `is_auto_graded=True`, `has_live_check=True`. Config `{"items":[...]}` (correct order). `score`→float (absolute-position `correct/total`); `live_check`→`list[int]` per-position.

- [ ] **Step 1: Write the tests (append to test_question_types.py)**

```python
class TestOrderingPlugin(unittest.TestCase):
	def _q(self):
		q = frappe.new_doc("LMS Question")
		q.question = "Order the planets by distance"
		q.type = "Ordering"
		q.data = json.dumps({"items": ["Mercury", "Venus", "Earth"]})
		q.save()
		return q

	def test_validate_requires_two_items(self):
		q = frappe.new_doc("LMS Question")
		q.question = "Bad ordering"
		q.type = "Ordering"
		q.data = json.dumps({"items": ["only one"]})
		self.assertRaises(frappe.ValidationError, q.save)

	def test_score_absolute_position(self):
		q = self._q()
		qt = get_question_type("Ordering")
		self.assertEqual(qt.score(q.name, ["Mercury", "Venus", "Earth"]), 1.0)
		# first correct, last two swapped -> 1 of 3
		self.assertAlmostEqual(qt.score(q.name, ["Mercury", "Earth", "Venus"]), 1 / 3)
		self.assertEqual(qt.score(q.name, ["Earth", "Venus", "Mercury"]), 1 / 3)
		frappe.delete_doc("LMS Question", q.name, force=True)

	def test_live_check_per_position(self):
		q = self._q()
		qt = get_question_type("Ordering")
		self.assertEqual(qt.live_check(q.name, ["Mercury", "Earth", "Venus"]), [1, 0, 0])
		frappe.delete_doc("LMS Question", q.name, force=True)
```

- [ ] **Step 2: Implement the plugin**

Create `lms/lms/question_types/ordering.py`:

```python
# Copyright (c) 2026, Frappe and contributors
# For license information, please see license.txt

import frappe
from frappe import _

from lms.lms.question_types.base import QuestionType


class OrderingQuestion(QuestionType):
	name = "Ordering"
	label = "Ordering"
	is_auto_graded = True
	has_live_check = True

	def validate(self, question) -> None:
		items = frappe.parse_json(question.get("data") or "{}").get("items") or []
		if len([i for i in items if str(i).strip()]) < 2:
			frappe.throw(_("Add at least two items."))

	def _items(self, question_name: str) -> list:
		data = frappe.db.get_value("LMS Question", question_name, "data")
		return frappe.parse_json(data or "{}").get("items") or []

	def _per_position(self, question_name: str, answer: list) -> list:
		results = []
		for i, item in enumerate(self._items(question_name)):
			given = str(answer[i]).strip() if i < len(answer) else ""
			correct = str(item or "").strip()
			results.append(1 if given and given == correct else 0)
		return results

	def score(self, question_name: str, answer: list) -> float:
		per_position = self._per_position(question_name, answer)
		if not per_position:
			return 0.0
		return sum(per_position) / len(per_position)

	def live_check(self, question_name: str, answer: list) -> list:
		return self._per_position(question_name, answer)
```

- [ ] **Step 3: Register + add the Select option**

In `lms/lms/question_types/__init__.py`, add the import in alphabetical position (between `open_ended` and `true_false`):

```python
from lms.lms.question_types.ordering import OrderingQuestion
```

and add `register(OrderingQuestion)` with the other registrations.

In both `lms_question.json` and `lms_quiz_question.json`, change the `type` options to `"Choices\nUser Input\nOpen Ended\nTrue/False\nFill in the Blank\nMatching\nOrdering"`.

- [ ] **Step 4: Local checks**

Run: `python -m py_compile lms/lms/question_types/ordering.py lms/lms/question_types/__init__.py`
Run: `python -c "import json; json.load(open('lms/lms/doctype/lms_question/lms_question.json')); json.load(open('lms/lms/doctype/lms_quiz_question/lms_quiz_question.json'))"`
Expected: exit 0.

- [ ] **Step 5: Commit & push**

```bash
git add lms/lms/question_types/ordering.py lms/lms/question_types/__init__.py lms/lms/doctype/lms_question/lms_question.json lms/lms/doctype/lms_quiz_question/lms_quiz_question.json lms/lms/question_types/test_question_types.py
git commit -m "feat(quiz): add Ordering question type plugin"
git push
```

Verification gate: full "Server Tests" green — both plugins validate/score/live_check; drift guard passes with the two new options; existing tests untouched.

---

## Self-Review

- **Spec coverage:** Matching plugin (Task 1) ✓; Ordering plugin (Task 2) ✓; strict-1:1 value-equality matching (Task 1 `_per_pair`) ✓; absolute-position ordering (Task 2 `_per_position`) ✓; fractional score + per-element live_check both ✓; Select options + registry both updated ✓; no framework changes ✓.
- **Placeholder scan:** none.
- **Type consistency:** `score`→float, `live_check`→`list[int]`, names `"Matching"`/`"Ordering"` used identically in plugin, registration, Select options, and tests. `frappe.parse_json(... or "{}")` for `data` everywhere, mirroring `fill_blank.py`.
- **Cross-plan dependency:** the frontend plan's registry `name`s and the answer-array shapes (matching: chosen-right-per-left in left order; ordering: learner's ordered item list) must match these plugins exactly. The Select-option strings here must equal the frontend registry names.
- **Import-order note:** `__init__.py` imports stay alphabetical (`...choices, fill_blank, matching, open_ended, ordering, true_false, user_input`) to satisfy CI's ruff isort.
