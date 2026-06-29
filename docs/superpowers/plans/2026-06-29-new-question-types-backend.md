# New Question Types — Backend Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the True/False and multi-blank Fill-in-the-blank question types on the backend, plus the framework changes they require (fractional scoring, Float score fields, registry-driven live-check gate, `data` in the player fetch).

**Architecture:** Two new plugin classes in `lms/lms/question_types/` (registered alongside the existing three), storing their answer schema in `LMS Question.data` (JSON). The scoring contract becomes fractional (`score()` returns a float in `[0,1]`); because Python `True==1.0`/`False==0.0`, the existing bool-returning plugins remain correct unchanged. Submission score fields become `Float` so partial credit isn't truncated.

**Tech Stack:** Python 3.11+, Frappe; `bench run-tests` (CI only).

## Global Constraints

- **Zero behavior change for existing types.** `test_lms_quiz.py` and the existing cases in `test_question_types.py` must pass unmodified. Choices/User Input still score full-or-zero; Open Ended still manual.
- **Fractional scoring:** `score()` returns a float in `[0,1]`. `process_results` computes `earned = flt(fraction) * flt(marks)`; negative marking only when `fraction == 0`; `is_correct = 1` only when `fraction == 1`.
- **No data migration.** New types use `LMS Question.data`; Int→Float field changes are storage-compatible.
- **Matching semantics (fill-blank):** a blank is correct iff the learner value equals any accepted answer, compared case-insensitively and trimmed. No fuzzy matching.
- **Drift guard:** the `LMS Question.type` Select options must always equal the registry names (`test_registry_matches_doctype_select_options`). Add each new name to BOTH `lms_question.json` and `lms_quiz_question.json` `type` Select options in the same task that registers the plugin.
- **Tests run in CI only** (no local bench). Per-task local check: `python -m py_compile` for `.py`, `python -c "import json; json.load(open(...))"` for `.json`. Verification gate = push branch → "Server Tests" workflow (`bench --site frappe.local run-tests --app lms --coverage`). Style: tabs.

---

## File Structure

- Create: `lms/lms/question_types/true_false.py` — `TrueFalseQuestion`.
- Create: `lms/lms/question_types/fill_blank.py` — `FillBlankQuestion`.
- Modify: `lms/lms/question_types/__init__.py` — register the two new plugins.
- Modify: `lms/lms/question_types/test_question_types.py` — tests for both + the fractional-aggregation test.
- Modify: `lms/lms/doctype/lms_quiz/lms_quiz.py` — `process_results` fractional; `check_answer` live-check gate.
- Modify: `lms/lms/doctype/lms_quiz_submission/lms_quiz_submission.py` — `cint`→`flt`.
- Modify: `lms/lms/doctype/lms_quiz_submission/lms_quiz_submission.json` — score/score_out_of/percentage → Float.
- Modify: `lms/lms/doctype/lms_quiz_result/lms_quiz_result.json` — marks → Float.
- Modify: `lms/lms/doctype/lms_question/lms_question.json` and `lms/lms/doctype/lms_quiz_question/lms_quiz_question.json` — add the two new `type` Select options.
- Modify: `lms/lms/utils.py` — `get_quiz_with_questions` fetch includes `data`.

---

## Task 1: Float score fields + flt aggregation

**Files:**
- Modify: `lms/lms/doctype/lms_quiz_result/lms_quiz_result.json`
- Modify: `lms/lms/doctype/lms_quiz_submission/lms_quiz_submission.json`
- Modify: `lms/lms/doctype/lms_quiz_submission/lms_quiz_submission.py`
- Test: `lms/lms/question_types/test_question_types.py`

**Interfaces:**
- Produces: `LMS Quiz Result.marks` and `LMS Quiz Submission.score`/`score_out_of`/`percentage` are `Float`; `validate_marks` sums with `flt`.

- [ ] **Step 1: Change field types to Float**

In `lms/lms/doctype/lms_quiz_result/lms_quiz_result.json`, change the `marks` field's `"fieldtype": "Int"` to `"fieldtype": "Float"` (leave `marks_out_of` as `Int`).

In `lms/lms/doctype/lms_quiz_submission/lms_quiz_submission.json`, change the `fieldtype` of `score`, `score_out_of`, and `percentage` from `Int` to `Float`.

- [ ] **Step 2: Switch cint→flt in the controller**

In `lms/lms/doctype/lms_quiz_submission/lms_quiz_submission.py`:
- Change the import `from frappe.utils import cint` to `from frappe.utils import flt`.
- In `validate_marks`, replace the body's `cint(...)` calls and accumulation:

```python
	def validate_marks(self):
		self.score = 0
		for row in self.result:
			if flt(row.marks) > flt(row.marks_out_of):
				frappe.throw(
					_(
						"Marks for question number {0} cannot be greater than the marks allotted for that question."
					).format(row.idx)
				)
			else:
				self.score += flt(row.marks)
```

(There are no other `cint` uses in this file after this change; if `py_compile`/grep shows a remaining `cint`, leave its logic but import both. Verify with `grep -n cint lms/lms/doctype/lms_quiz_submission/lms_quiz_submission.py`.)

- [ ] **Step 3: Write the fractional-aggregation test**

Append to `lms/lms/question_types/test_question_types.py`:

```python
class TestFractionalMarksAggregation(unittest.TestCase):
	def test_submission_sums_fractional_marks(self):
		sub = frappe.new_doc("LMS Quiz Submission")
		sub.quiz = "Test Quiz"
		sub.score_out_of = 3
		sub.passing_percentage = 50
		sub.append("result", {"marks": 2.0, "marks_out_of": 3, "is_correct": 0})
		sub.append("result", {"marks": 1.0, "marks_out_of": 1, "is_correct": 1})
		sub.validate_marks()
		self.assertEqual(sub.score, 3.0)

	def test_partial_fraction_not_truncated(self):
		sub = frappe.new_doc("LMS Quiz Submission")
		sub.quiz = "Test Quiz"
		sub.score_out_of = 1
		sub.passing_percentage = 50
		sub.append("result", {"marks": 0.5, "marks_out_of": 1, "is_correct": 0})
		sub.validate_marks()
		self.assertEqual(sub.score, 0.5)
```

(`Test Quiz` is created in `test_lms_quiz.py`'s `setUpClass`; these tests run in the same `bench run-tests` session. They call `validate_marks()` directly without saving, so no quiz dependency is exercised.)

- [ ] **Step 4: Local checks**

Run: `python -m py_compile lms/lms/doctype/lms_quiz_submission/lms_quiz_submission.py`
Run: `python -c "import json; json.load(open('lms/lms/doctype/lms_quiz_result/lms_quiz_result.json')); json.load(open('lms/lms/doctype/lms_quiz_submission/lms_quiz_submission.json'))"`
Expected: exit 0 for both.

- [ ] **Step 5: Commit**

```bash
git add lms/lms/doctype/lms_quiz_result/lms_quiz_result.json lms/lms/doctype/lms_quiz_submission/ lms/lms/question_types/test_question_types.py
git commit -m "feat(quiz): float score fields so partial credit isn't truncated"
```

---

## Task 2: Fractional scoring in process_results

**Files:**
- Modify: `lms/lms/doctype/lms_quiz/lms_quiz.py` (`process_results`, ~lines 170-181)

**Interfaces:**
- Consumes: `QuestionType.score()` now interpreted as a float in `[0,1]` (existing bool returns are arithmetically compatible: `True==1.0`, `False==0.0`).
- Produces: `result["marks"]` may be fractional; `is_correct` is 1 only at fraction 1.

- [ ] **Step 1: Confirm backward-compat coverage exists**

`test_lms_quiz.py` already exercises Choices/User Input scoring via `verify_answer`/`check_input_answers`, and submit via the quiz flow. These pin that full-or-zero behavior is unchanged. Do not edit them.

- [ ] **Step 2: Make the scoring branch fractional**

In `lms/lms/doctype/lms_quiz/lms_quiz.py`, add `flt` to the `frappe.utils` import line (it already imports from `frappe.utils`; add `flt` to that import). Then replace the auto-graded branch in `process_results`:

```python
		question_type = get_question_type(question_details.type)
		if question_type.is_auto_graded:
			correct = question_type.score(question_details.question, result["answer"])
			result["answer"] = ", ".join(result["answer"])
			if correct:
				result["marks"] = question_details.marks
			else:
				result["marks"] = -quiz_details.marks_to_cut if quiz_details.enable_negative_marking else 0
			result["is_correct"] = 1 if correct else 0
```

with:

```python
		question_type = get_question_type(question_details.type)
		if question_type.is_auto_graded:
			fraction = flt(question_type.score(question_details.question, result["answer"]))
			result["answer"] = ", ".join(result["answer"])
			if fraction > 0:
				result["marks"] = fraction * flt(question_details.marks)
			else:
				result["marks"] = -quiz_details.marks_to_cut if quiz_details.enable_negative_marking else 0
			result["is_correct"] = 1 if fraction == 1 else 0
```

(For Choices/User Input, `score` returns `True`/`False` → `flt(True)=1.0`/`flt(False)=0.0`, so `fraction>0` and `fraction==1` behave exactly as the old `correct` boolean. No behavior change.)

- [ ] **Step 3: Local check**

Run: `python -m py_compile lms/lms/doctype/lms_quiz/lms_quiz.py`
Expected: exit 0.

- [ ] **Step 4: Commit & push (Tasks 1-2 ready for the first CI gate)**

```bash
git add lms/lms/doctype/lms_quiz/lms_quiz.py
git commit -m "refactor(quiz): fractional scoring in process_results"
git push
```

Verification gate: "Server Tests" green (existing scoring tests unchanged; fractional aggregation tests pass).

---

## Task 3: Registry-driven live-check gate (backend)

**Files:**
- Modify: `lms/lms/doctype/lms_quiz/lms_quiz.py` (`check_answer`, ~line 314)

**Interfaces:**
- Produces: `check_answer` rejects types whose plugin has `has_live_check = False`.

- [ ] **Step 1: Add the test**

Append to `lms/lms/question_types/test_question_types.py`:

```python
class TestLiveCheckGate(unittest.TestCase):
	def test_open_ended_has_no_live_check(self):
		self.assertFalse(get_question_type("Open Ended").has_live_check)
```

(The whitelisted `check_answer` requires a real quiz/permission context; the unit test pins the flag the gate reads. The gate's wiring is verified by the existing flow + this flag.)

- [ ] **Step 2: Gate check_answer on has_live_check**

In `check_answer`, replace the final two lines:

```python
	answers = answers and json.loads(answers)
	return get_question_type(question_type).live_check(question, answers)
```

with:

```python
	question_type_def = get_question_type(question_type)
	if not question_type_def.has_live_check:
		frappe.throw(_("Live answer checking is not available for this question type."))

	answers = answers and json.loads(answers)
	return question_type_def.live_check(question, answers)
```

- [ ] **Step 3: Local check + commit**

Run: `python -m py_compile lms/lms/doctype/lms_quiz/lms_quiz.py` → exit 0.

```bash
git add lms/lms/doctype/lms_quiz/lms_quiz.py lms/lms/question_types/test_question_types.py
git commit -m "feat(quiz): gate check_answer on has_live_check"
```

---

## Task 4: Include `data` in the player question fetch

**Files:**
- Modify: `lms/lms/utils.py` (`get_quiz_with_questions`)

**Interfaces:**
- Produces: each entry in `questions_by_name` includes the `data` JSON field, so the player can read new-type config.

- [ ] **Step 1: Add the test**

Append to `lms/lms/question_types/test_question_types.py`:

```python
class TestQuizFetchIncludesData(unittest.TestCase):
	def test_get_quiz_with_questions_returns_data_field(self):
		from lms.lms.utils import get_quiz_with_questions

		q = frappe.new_doc("LMS Question")
		q.question = "Fetch data field"
		q.type = "Choices"
		q.option_1 = "a"
		q.is_correct_1 = 1
		q.option_2 = "b"
		q.save()
		quiz = frappe.new_doc("LMS Quiz")
		quiz.title = "Fetch Data Quiz"
		quiz.passing_percentage = 50
		quiz.append("questions", {"question": q.name, "marks": 1})
		quiz.save()

		result = get_quiz_with_questions(quiz.name)
		row = result["questions_by_name"][q.name]
		self.assertIn("data", row)

		frappe.delete_doc("LMS Quiz", quiz.name, force=True)
		frappe.delete_doc("LMS Question", q.name, force=True)
```

- [ ] **Step 2: Add `data` to the fetch fields**

In `lms/lms/utils.py`, in `get_quiz_with_questions`, change the `fields` list to include `"data"`:

```python
		fields = [
			"name",
			"question",
			"type",
			"data",
			"multiple",
			*QUESTION_OPTION_FIELDS,
			*QUESTION_EXPLANATION_FIELDS,
		]
```

- [ ] **Step 3: Local check + commit & push**

Run: `python -m py_compile lms/lms/utils.py` → exit 0.

```bash
git add lms/lms/utils.py lms/lms/question_types/test_question_types.py
git commit -m "feat(quiz): include data field in get_quiz_with_questions"
git push
```

Verification gate: "Server Tests" green.

---

## Task 5: TrueFalseQuestion plugin

**Files:**
- Create: `lms/lms/question_types/true_false.py`
- Modify: `lms/lms/question_types/__init__.py`
- Modify: `lms/lms/doctype/lms_question/lms_question.json`, `lms/lms/doctype/lms_quiz_question/lms_quiz_question.json`
- Test: `lms/lms/question_types/test_question_types.py`

**Interfaces:**
- Produces: `class TrueFalseQuestion(QuestionType)`, `name="True/False"`, `is_auto_graded=True`, `has_live_check=True`. Config in `LMS Question.data` = `{"correct": bool, "explanation": str}`. `score` returns `1.0`/`0.0`; `live_check` returns `1`/`0`.

- [ ] **Step 1: Write the tests**

Append to `lms/lms/question_types/test_question_types.py`:

```python
class TestTrueFalsePlugin(unittest.TestCase):
	def _q(self, correct):
		q = frappe.new_doc("LMS Question")
		q.question = "Sky is blue"
		q.type = "True/False"
		q.data = json.dumps({"correct": correct, "explanation": ""})
		q.save()
		return q

	def test_validate_requires_boolean(self):
		q = frappe.new_doc("LMS Question")
		q.question = "Bad TF"
		q.type = "True/False"
		q.data = json.dumps({"explanation": "x"})
		self.assertRaises(frappe.ValidationError, q.save)

	def test_score_true_correct(self):
		q = self._q(True)
		qt = get_question_type("True/False")
		self.assertEqual(qt.score(q.name, ["true"]), 1.0)
		self.assertEqual(qt.score(q.name, ["false"]), 0.0)
		frappe.delete_doc("LMS Question", q.name, force=True)

	def test_live_check_returns_correctness(self):
		q = self._q(False)
		qt = get_question_type("True/False")
		self.assertEqual(qt.live_check(q.name, ["false"]), 1)
		self.assertEqual(qt.live_check(q.name, ["true"]), 0)
		frappe.delete_doc("LMS Question", q.name, force=True)
```

(Ensure `import json` is present at the top of the test file; it already is from earlier tasks — if not, add it.)

- [ ] **Step 2: Implement the plugin**

Create `lms/lms/question_types/true_false.py`:

```python
# Copyright (c) 2026, Frappe and contributors
# For license information, please see license.txt

import frappe
from frappe import _

from lms.lms.question_types.base import QuestionType


class TrueFalseQuestion(QuestionType):
	name = "True/False"
	label = "True/False"
	is_auto_graded = True
	has_live_check = True

	def validate(self, question) -> None:
		config = frappe.parse_json(question.get("data") or "{}")
		if not isinstance(config.get("correct"), bool):
			frappe.throw(_("Select the correct answer (True or False)."))

	def _correct(self, question_name: str) -> bool:
		data = frappe.db.get_value("LMS Question", question_name, "data")
		return bool(frappe.parse_json(data or "{}").get("correct"))

	def _chosen(self, answer: list) -> bool:
		return str(answer[0]).strip().lower() == "true"

	def score(self, question_name: str, answer: list) -> float:
		if not answer:
			return 0.0
		return 1.0 if self._chosen(answer) == self._correct(question_name) else 0.0

	def live_check(self, question_name: str, answer: list) -> int:
		return 1 if self.score(question_name, answer) == 1.0 else 0
```

- [ ] **Step 3: Register + add the Select option**

In `lms/lms/question_types/__init__.py`: add `from lms.lms.question_types.true_false import TrueFalseQuestion` with the other imports, and `register(TrueFalseQuestion)` after the existing registrations.

In `lms/lms/doctype/lms_question/lms_question.json` and `lms/lms/doctype/lms_quiz_question/lms_quiz_question.json`, change the `type` field's `"options": "Choices\nUser Input\nOpen Ended"` to `"options": "Choices\nUser Input\nOpen Ended\nTrue/False"`.

- [ ] **Step 4: Local checks**

Run: `python -m py_compile lms/lms/question_types/true_false.py lms/lms/question_types/__init__.py`
Run: `python -c "import json; json.load(open('lms/lms/doctype/lms_question/lms_question.json')); json.load(open('lms/lms/doctype/lms_quiz_question/lms_quiz_question.json'))"`
Expected: exit 0.

- [ ] **Step 5: Commit & push**

```bash
git add lms/lms/question_types/true_false.py lms/lms/question_types/__init__.py lms/lms/doctype/lms_question/lms_question.json lms/lms/doctype/lms_quiz_question/lms_quiz_question.json lms/lms/question_types/test_question_types.py
git commit -m "feat(quiz): add True/False question type plugin"
git push
```

Verification gate: "Server Tests" green (incl. drift guard with the new option).

---

## Task 6: FillBlankQuestion plugin

**Files:**
- Create: `lms/lms/question_types/fill_blank.py`
- Modify: `lms/lms/question_types/__init__.py`
- Modify: `lms/lms/doctype/lms_question/lms_question.json`, `lms/lms/doctype/lms_quiz_question/lms_quiz_question.json`
- Test: `lms/lms/question_types/test_question_types.py`

**Interfaces:**
- Produces: `class FillBlankQuestion(QuestionType)`, `name="Fill in the Blank"`, `is_auto_graded=True`, `has_live_check=True`. Config = `{"blanks": [{"label": str, "accepted": [str, ...]}, ...]}`. `score` returns `correct_blanks / total_blanks` (float). `live_check` returns a per-blank `list[int]`.

- [ ] **Step 1: Write the tests**

Append to `lms/lms/question_types/test_question_types.py`:

```python
class TestFillBlankPlugin(unittest.TestCase):
	def _q(self):
		q = frappe.new_doc("LMS Question")
		q.question = "Water is (1) and (2)"
		q.type = "Fill in the Blank"
		q.data = json.dumps(
			{
				"blanks": [
					{"label": "1", "accepted": ["hydrogen", "H"]},
					{"label": "2", "accepted": ["oxygen"]},
				]
			}
		)
		q.save()
		return q

	def test_validate_requires_a_blank_with_answer(self):
		q = frappe.new_doc("LMS Question")
		q.question = "Empty blanks"
		q.type = "Fill in the Blank"
		q.data = json.dumps({"blanks": [{"label": "1", "accepted": []}]})
		self.assertRaises(frappe.ValidationError, q.save)

	def test_score_full_partial_zero(self):
		q = self._q()
		qt = get_question_type("Fill in the Blank")
		self.assertEqual(qt.score(q.name, ["hydrogen", "oxygen"]), 1.0)
		self.assertEqual(qt.score(q.name, ["  Hydrogen ", "wrong"]), 0.5)
		self.assertEqual(qt.score(q.name, ["no", "no"]), 0.0)
		frappe.delete_doc("LMS Question", q.name, force=True)

	def test_live_check_per_blank(self):
		q = self._q()
		qt = get_question_type("Fill in the Blank")
		self.assertEqual(qt.live_check(q.name, ["H", "oxygen"]), [1, 1])
		self.assertEqual(qt.live_check(q.name, ["x", "oxygen"]), [0, 1])
		frappe.delete_doc("LMS Question", q.name, force=True)
```

- [ ] **Step 2: Implement the plugin**

Create `lms/lms/question_types/fill_blank.py`:

```python
# Copyright (c) 2026, Frappe and contributors
# For license information, please see license.txt

import frappe
from frappe import _

from lms.lms.question_types.base import QuestionType


class FillBlankQuestion(QuestionType):
	name = "Fill in the Blank"
	label = "Fill in the Blank"
	is_auto_graded = True
	has_live_check = True

	def validate(self, question) -> None:
		blanks = frappe.parse_json(question.get("data") or "{}").get("blanks") or []
		if not blanks:
			frappe.throw(_("Add at least one blank."))
		for blank in blanks:
			accepted = [a for a in (blank.get("accepted") or []) if str(a).strip()]
			if not accepted:
				frappe.throw(_("Each blank needs at least one accepted answer."))

	def _blanks(self, question_name: str) -> list:
		data = frappe.db.get_value("LMS Question", question_name, "data")
		return frappe.parse_json(data or "{}").get("blanks") or []

	def _norm(self, value) -> str:
		return str(value or "").strip().casefold()

	def _per_blank(self, question_name: str, answer: list) -> list:
		results = []
		for i, blank in enumerate(self._blanks(question_name)):
			given = self._norm(answer[i]) if i < len(answer) else ""
			accepted = {self._norm(a) for a in (blank.get("accepted") or [])}
			results.append(1 if given and given in accepted else 0)
		return results

	def score(self, question_name: str, answer: list) -> float:
		per_blank = self._per_blank(question_name, answer)
		if not per_blank:
			return 0.0
		return sum(per_blank) / len(per_blank)

	def live_check(self, question_name: str, answer: list) -> list:
		return self._per_blank(question_name, answer)
```

- [ ] **Step 3: Register + add the Select option**

In `lms/lms/question_types/__init__.py`: add `from lms.lms.question_types.fill_blank import FillBlankQuestion` and `register(FillBlankQuestion)`.

In both `lms_question.json` and `lms_quiz_question.json`, change the `type` options to `"Choices\nUser Input\nOpen Ended\nTrue/False\nFill in the Blank"`.

- [ ] **Step 4: Local checks**

Run: `python -m py_compile lms/lms/question_types/fill_blank.py lms/lms/question_types/__init__.py`
Run: `python -c "import json; json.load(open('lms/lms/doctype/lms_question/lms_question.json')); json.load(open('lms/lms/doctype/lms_quiz_question/lms_quiz_question.json'))"`
Expected: exit 0.

- [ ] **Step 5: Commit & push**

```bash
git add lms/lms/question_types/fill_blank.py lms/lms/question_types/__init__.py lms/lms/doctype/lms_question/lms_question.json lms/lms/doctype/lms_quiz_question/lms_quiz_question.json lms/lms/question_types/test_question_types.py
git commit -m "feat(quiz): add Fill in the Blank question type plugin"
git push
```

Verification gate: full "Server Tests" green — both new types validate/score/live_check; drift guard passes with both new options; partial-credit aggregation correct; existing tests untouched.

---

## Self-Review

- **Spec coverage:** fractional contract (Task 2) ✓; Float fields (Task 1) ✓; live-check gate backend (Task 3) ✓; `questionTypeOptions` name fix is FRONTEND (frontend plan) — noted; `data` in fetch (Task 4) ✓; True/False (Task 5) ✓; Fill-blank (Task 6) ✓; matching = casefold+trim exact (Task 6 `_norm`) ✓; partial fractions tested (Tasks 1, 6) ✓.
- **Placeholder scan:** none — every step has concrete code/commands.
- **Type consistency:** `score`→float, `live_check`→int (True/False) / list[int] (fill-blank), `name` strings (`"True/False"`, `"Fill in the Blank"`) used identically in plugin, registration, Select options, and tests. `frappe.parse_json` used for `data` everywhere.
- **Cross-plan dependency:** the frontend plan must add the same two names to its registry and set `data` as a first-class field; the Select-option strings here must match the frontend registry `name`s exactly.
