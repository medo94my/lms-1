# Question-Type Framework — Backend Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the four hardcoded per-type dispatch points in the LMS quiz backend with a question-type registry, re-homing the existing Choices / User Input / Open Ended logic behind it with zero behavior change.

**Architecture:** A new `lms/lms/question_types/` package holds one plugin class per type plus a registry. Existing module-level functions in `lms_question.py` and `lms_quiz.py` stay put (the test suite imports them by name); plugins **delegate** to them. The three dispatch sites call `get_question_type(type).<method>(...)` instead of branching on `type`. A new JSON `data` field on `LMS Question` is added as the storage seam for future types but is unused by the existing three.

**Tech Stack:** Python 3.11+, Frappe framework, `bench run-tests` (CI only).

## Global Constraints

- **Zero behavior change.** `lms/lms/doctype/lms_quiz/test_lms_quiz.py` must pass **unmodified**. Do not edit that file.
- **Preserve public function names/signatures** in `lms_quiz.py` (`verify_answer`, `check_input_answers`, `check_choice_answers`, `get_question_details`, `_save_file`) and `lms_question.py` (`validate_correct_answers` and its helpers) — they are imported by tests and other modules.
- **No data migration.** Existing questions keep `option_1..10` / `possibility_1..10`; do not write a patch.
- **Backend tests run in CI only** (no local bench on this host). Verification gate per task = push branch, watch the **"Server Tests"** GitHub Actions workflow (`.github/workflows/ci.yml`, command `bench --site frappe.local run-tests --app lms --coverage`). Locally, the only available check is `python -m py_compile <file>` for syntax.
- Follow existing style: tabs for indentation (the repo uses tabs in these files), `from frappe import _` for translations.

---

## File Structure

- Create: `lms/lms/question_types/__init__.py` — registry: `get_question_type`, `get_question_type_names`, registration.
- Create: `lms/lms/question_types/base.py` — `QuestionType` base class (the contract).
- Create: `lms/lms/question_types/choices.py` — `ChoicesQuestion`.
- Create: `lms/lms/question_types/user_input.py` — `UserInputQuestion`.
- Create: `lms/lms/question_types/open_ended.py` — `OpenEndedQuestion`.
- Create: `lms/lms/question_types/test_question_types.py` — registry-level tests.
- Modify: `lms/lms/doctype/lms_question/lms_question.py` — `validate_correct_answers` dispatches to registry.
- Modify: `lms/lms/doctype/lms_quiz/lms_quiz.py` — `submit()` and `check_answer()` dispatch to registry.
- Modify: `lms/lms/doctype/lms_question/lms_question.json` — add `data` (JSON) field.

---

## Task 1: The registry and contract (no behavior wired yet)

**Files:**
- Create: `lms/lms/question_types/base.py`
- Create: `lms/lms/question_types/__init__.py`
- Test: `lms/lms/question_types/test_question_types.py`

**Interfaces:**
- Produces:
  - `class QuestionType` with attributes `name: str`, `label: str`, `is_auto_graded: bool`, `has_live_check: bool`; methods `validate(self, question) -> None`, `score(self, question_name: str, answer: list) -> bool | None`, `live_check(self, question_name: str, answer: list)`, `read_config(self, question) -> dict`.
  - `get_question_type(name: str) -> QuestionType` (raises `frappe.ValidationError` on unknown).
  - `get_question_type_names() -> list[str]`.

- [ ] **Step 1: Write the base contract**

Create `lms/lms/question_types/base.py`:

```python
# Copyright (c) 2026, Frappe and contributors
# For license information, please see license.txt

import frappe


class QuestionType:
	"""Contract every quiz question type implements.

	The existing scoring/validation helpers still live in lms_question.py and
	lms_quiz.py; concrete types delegate to them. New types implement the
	methods directly and store their answer schema in LMS Question.data.
	"""

	name: str = ""
	label: str = ""
	# Auto-graded types return True/False from score(); manual types (Open
	# Ended) return None and are graded by an instructor.
	is_auto_graded: bool = True
	# Whether the live "Check" button is offered for this type.
	has_live_check: bool = False

	def validate(self, question) -> None:
		"""Authoring-time validation. Raise via frappe.throw if invalid."""
		pass

	def score(self, question_name: str, answer: list):
		"""Return True/False for auto-graded types, or None for manual."""
		raise NotImplementedError

	def live_check(self, question_name: str, answer: list):
		"""Return the per-type live-feedback payload for the Check button."""
		raise NotImplementedError

	def read_config(self, question) -> dict:
		"""Return the type's answer schema. New types read LMS Question.data;
		legacy types read their flat columns inside the delegated helpers, so
		the default returns the parsed JSON blob."""
		return frappe.parse_json(question.get("data") or "{}")
```

- [ ] **Step 2: Write the registry**

Create `lms/lms/question_types/__init__.py`:

```python
# Copyright (c) 2026, Frappe and contributors
# For license information, please see license.txt

import frappe
from frappe import _

from lms.lms.question_types.base import QuestionType
from lms.lms.question_types.choices import ChoicesQuestion
from lms.lms.question_types.open_ended import OpenEndedQuestion
from lms.lms.question_types.user_input import UserInputQuestion

_REGISTRY: dict[str, QuestionType] = {}


def register(question_type: type[QuestionType]) -> None:
	instance = question_type()
	_REGISTRY[instance.name] = instance


def get_question_type(name: str) -> QuestionType:
	question_type = _REGISTRY.get(name)
	if question_type is None:
		frappe.throw(_("Unknown question type: {0}").format(name), frappe.ValidationError)
	return question_type


def get_question_type_names() -> list[str]:
	return list(_REGISTRY.keys())


register(ChoicesQuestion)
register(UserInputQuestion)
register(OpenEndedQuestion)
```

> NOTE: This imports the three concrete classes created in Tasks 2-4. Until those files exist the package won't import. Implement Tasks 2-4's files alongside this step (they are small) OR temporarily stub the three classes in their files first. The committed state at the end of Task 1 must import cleanly, so create the three module files with their final content (Tasks 2-4) before committing Task 1. Practically: do Tasks 1-4 as one push.

- [ ] **Step 3: Write registry tests**

Create `lms/lms/question_types/test_question_types.py`:

```python
# Copyright (c) 2026, Frappe and contributors
# See license.txt

import unittest

import frappe

from lms.lms.question_types import get_question_type, get_question_type_names


class TestQuestionTypeRegistry(unittest.TestCase):
	def test_existing_types_are_registered(self):
		names = get_question_type_names()
		self.assertIn("Choices", names)
		self.assertIn("User Input", names)
		self.assertIn("Open Ended", names)

	def test_unknown_type_raises(self):
		with self.assertRaises(frappe.ValidationError):
			get_question_type("Nonexistent Type")

	def test_choices_is_auto_graded_open_ended_is_not(self):
		self.assertTrue(get_question_type("Choices").is_auto_graded)
		self.assertFalse(get_question_type("Open Ended").is_auto_graded)

	def test_registry_matches_doctype_select_options(self):
		# Guard against drift: the LMS Question.type Select options must equal
		# the registered type names. Adding a type means updating both.
		meta = frappe.get_meta("LMS Question")
		options = [o for o in (meta.get_field("type").options or "").split("\n") if o]
		self.assertEqual(sorted(options), sorted(get_question_type_names()))
```

- [ ] **Step 4: Local syntax check**

Run: `python -m py_compile lms/lms/question_types/base.py lms/lms/question_types/__init__.py lms/lms/question_types/test_question_types.py`
Expected: no output (exit 0). (Cannot import frappe locally; this only catches syntax.)

- [ ] **Step 5: Commit (with Tasks 2-4 files present — see note in Step 2)**

```bash
git add lms/lms/question_types/
git commit -m "feat(quiz): add question-type registry and contract"
```

---

## Task 2: ChoicesQuestion plugin (delegates to existing helpers)

**Files:**
- Create: `lms/lms/question_types/choices.py`

**Interfaces:**
- Consumes: `verify_answer`, `check_choice_answers` from `lms_quiz.py`; `validate_correct_answers` helpers from `lms_question.py`.
- Produces: `class ChoicesQuestion(QuestionType)` with `name="Choices"`, `is_auto_graded=True`, `has_live_check=True`.

- [ ] **Step 1: Write the test (added to test_question_types.py)**

Append to `lms/lms/question_types/test_question_types.py`:

```python
class TestChoicesPlugin(unittest.TestCase):
	def setUp(self):
		self.q = frappe.new_doc("LMS Question")
		self.q.question = "Plugin choices"
		self.q.type = "Choices"
		self.q.option_1 = "a"
		self.q.is_correct_1 = 1
		self.q.option_2 = "b"
		self.q.save()

	def tearDown(self):
		frappe.delete_doc("LMS Question", self.q.name, force=True)

	def test_score_delegates_to_verify_answer(self):
		qt = get_question_type("Choices")
		self.assertTrue(qt.score(self.q.name, ["a"]))
		self.assertFalse(qt.score(self.q.name, ["b"]))

	def test_live_check_returns_per_option_list(self):
		qt = get_question_type("Choices")
		result = qt.live_check(self.q.name, ["a"])
		self.assertIsInstance(result, list)
```

- [ ] **Step 2: Implement the plugin**

Create `lms/lms/question_types/choices.py`:

```python
# Copyright (c) 2026, Frappe and contributors
# For license information, please see license.txt

from lms.lms.doctype.lms_question.lms_question import (
	validate_correct_options,
	validate_duplicate_options,
	validate_minimum_options,
)
from lms.lms.question_types.base import QuestionType


class ChoicesQuestion(QuestionType):
	name = "Choices"
	label = "Choices"
	is_auto_graded = True
	has_live_check = True

	def validate(self, question) -> None:
		validate_duplicate_options(question)
		validate_minimum_options(question)
		validate_correct_options(question)

	def score(self, question_name: str, answer: list):
		from lms.lms.doctype.lms_quiz.lms_quiz import verify_answer

		return verify_answer(question_name, answer)

	def live_check(self, question_name: str, answer: list):
		from lms.lms.doctype.lms_quiz.lms_quiz import check_choice_answers

		return check_choice_answers(question_name, answer)
```

> Imports of `lms_quiz` are function-local to avoid a circular import at module load (`lms_quiz` imports the registry).

- [ ] **Step 3: Local syntax check**

Run: `python -m py_compile lms/lms/question_types/choices.py`
Expected: exit 0.

- [ ] **Step 4: Commit** — folded into Task 1's commit (file must exist for `__init__.py` to import). If committing separately after Task 1, use:

```bash
git add lms/lms/question_types/choices.py lms/lms/question_types/test_question_types.py
git commit -m "feat(quiz): add Choices question-type plugin"
```

---

## Task 3: UserInputQuestion plugin

**Files:**
- Create: `lms/lms/question_types/user_input.py`

**Interfaces:**
- Consumes: `check_input_answers` from `lms_quiz.py`; `validate_possible_answer` from `lms_question.py`.
- Produces: `class UserInputQuestion(QuestionType)` with `name="User Input"`, `is_auto_graded=True`, `has_live_check=True`.

- [ ] **Step 1: Write the test (append to test_question_types.py)**

```python
class TestUserInputPlugin(unittest.TestCase):
	def setUp(self):
		self.q = frappe.new_doc("LMS Question")
		self.q.question = "Plugin input"
		self.q.type = "User Input"
		self.q.possibility_1 = "paris"
		self.q.save()

	def tearDown(self):
		frappe.delete_doc("LMS Question", self.q.name, force=True)

	def test_score_uses_first_answer_and_fuzzy_match(self):
		qt = get_question_type("User Input")
		self.assertTrue(qt.score(self.q.name, ["paris"]))
		self.assertFalse(qt.score(self.q.name, ["london"]))
```

- [ ] **Step 2: Implement the plugin**

Create `lms/lms/question_types/user_input.py`:

```python
# Copyright (c) 2026, Frappe and contributors
# For license information, please see license.txt

from lms.lms.doctype.lms_question.lms_question import validate_possible_answer
from lms.lms.question_types.base import QuestionType


class UserInputQuestion(QuestionType):
	name = "User Input"
	label = "User Input"
	is_auto_graded = True
	has_live_check = True

	def validate(self, question) -> None:
		validate_possible_answer(question)

	def score(self, question_name: str, answer: list):
		from lms.lms.doctype.lms_quiz.lms_quiz import check_input_answers

		# Matches the original submit() path: User Input scores the first
		# (only) supplied answer string.
		return bool(check_input_answers(question_name, answer[0]))

	def live_check(self, question_name: str, answer: list):
		from lms.lms.doctype.lms_quiz.lms_quiz import check_input_answers

		return check_input_answers(question_name, answer[0])
```

- [ ] **Step 3: Local syntax check**

Run: `python -m py_compile lms/lms/question_types/user_input.py`
Expected: exit 0.

- [ ] **Step 4: Commit** (or fold into Task 1 push):

```bash
git add lms/lms/question_types/user_input.py lms/lms/question_types/test_question_types.py
git commit -m "feat(quiz): add User Input question-type plugin"
```

---

## Task 4: OpenEndedQuestion plugin

**Files:**
- Create: `lms/lms/question_types/open_ended.py`

**Interfaces:**
- Produces: `class OpenEndedQuestion(QuestionType)` with `name="Open Ended"`, `is_auto_graded=False`, `has_live_check=False`.

- [ ] **Step 1: Write the test (append to test_question_types.py)**

```python
class TestOpenEndedPlugin(unittest.TestCase):
	def test_validate_is_noop_and_not_auto_graded(self):
		qt = get_question_type("Open Ended")
		self.assertFalse(qt.is_auto_graded)
		self.assertFalse(qt.has_live_check)
		# validate must not raise for a bare open-ended question
		q = frappe.new_doc("LMS Question")
		q.question = "Explain"
		q.type = "Open Ended"
		qt.validate(q)  # no exception
```

- [ ] **Step 2: Implement the plugin**

Create `lms/lms/question_types/open_ended.py`:

```python
# Copyright (c) 2026, Frappe and contributors
# For license information, please see license.txt

from lms.lms.question_types.base import QuestionType


class OpenEndedQuestion(QuestionType):
	name = "Open Ended"
	label = "Open Ended"
	is_auto_graded = False
	has_live_check = False

	def validate(self, question) -> None:
		# Open-ended questions have no correctness data to validate.
		pass

	def score(self, question_name: str, answer: list):
		# Graded manually by an instructor; the submit() flow stores the answer
		# rather than scoring it.
		return None
```

- [ ] **Step 3: Local syntax check**

Run: `python -m py_compile lms/lms/question_types/open_ended.py`
Expected: exit 0.

- [ ] **Step 4: Commit & push Tasks 1-4 together**

```bash
git add lms/lms/question_types/
git commit -m "feat(quiz): add Open Ended question-type plugin"
git push
```

Verification gate: open the **"Server Tests"** Actions run for this branch. Expected: PASS (new registry tests green; `test_lms_quiz.py` untouched and green — nothing is wired into it yet).

---

## Task 5: Add the `data` storage field to LMS Question

**Files:**
- Modify: `lms/lms/doctype/lms_question/lms_question.json`

**Interfaces:**
- Produces: an `LMS Question.data` field (JSON) available to future types; ignored by the existing three.

- [ ] **Step 1: Add the field to the DocType JSON**

In `lms/lms/doctype/lms_question/lms_question.json`, add `"data"` to the `field_order` array (place it immediately after `"type"`), and add this object to the `fields` array:

```json
{
 "fieldname": "data",
 "fieldtype": "JSON",
 "label": "Type Data",
 "description": "Answer schema for question types that do not use the option_1..10 columns."
}
```

- [ ] **Step 2: Add a test that the field exists (append to test_question_types.py)**

```python
class TestQuestionDataField(unittest.TestCase):
	def test_data_field_exists(self):
		meta = frappe.get_meta("LMS Question")
		field = meta.get_field("data")
		self.assertIsNotNone(field)
		self.assertEqual(field.fieldtype, "JSON")
```

- [ ] **Step 3: Validate the JSON is well-formed locally**

Run: `python -c "import json; json.load(open('lms/lms/doctype/lms_question/lms_question.json'))"`
Expected: exit 0 (no JSON error).

- [ ] **Step 4: Commit & push**

```bash
git add lms/lms/doctype/lms_question/lms_question.json lms/lms/question_types/test_question_types.py
git commit -m "feat(quiz): add JSON data field to LMS Question for new types"
git push
```

Verification gate: "Server Tests" run green (CI runs `bench migrate` implicitly via site setup; the new field is created).

---

## Task 6: Dispatch authoring-time validation through the registry

**Files:**
- Modify: `lms/lms/doctype/lms_question/lms_question.py:25-32` (`validate_correct_answers`)

**Interfaces:**
- Consumes: `get_question_type` from `lms.lms.question_types`.
- Produces: `validate_correct_answers(question)` now dispatches; the per-type helpers (`validate_duplicate_options`, etc.) remain and are called by plugins.

- [ ] **Step 1: Confirm the existing behavior tests exist**

`test_lms_quiz.py` already covers this dispatch indirectly:
`test_with_multiple_options`, `test_with_no_correct_option`, `test_with_no_possible_answers`. These must stay green. Do not edit them.

- [ ] **Step 2: Replace the branch with a registry call**

In `lms/lms/doctype/lms_question/lms_question.py`, replace:

```python
def validate_correct_answers(question):
	if question.type == "Choices":
		validate_duplicate_options(question)
		validate_minimum_options(question)
		validate_correct_options(question)
	elif question.type == "User Input":
		validate_possible_answer(question)
```

with:

```python
def validate_correct_answers(question):
	from lms.lms.question_types import get_question_type

	get_question_type(question.type).validate(question)
```

Leave `validate_duplicate_options`, `validate_minimum_options`, `validate_correct_options`, `validate_possible_answer`, `get_correct_options` exactly as they are — the plugins call them.

- [ ] **Step 3: Local syntax check**

Run: `python -m py_compile lms/lms/doctype/lms_question/lms_question.py`
Expected: exit 0.

- [ ] **Step 4: Commit & push**

```bash
git add lms/lms/doctype/lms_question/lms_question.py
git commit -m "refactor(quiz): dispatch question validation through registry"
git push
```

Verification gate: "Server Tests" green — especially `test_with_multiple_options` (sets `multiple` via `validate_correct_options`), `test_with_no_correct_option`, `test_with_no_possible_answers`.

---

## Task 7: Dispatch scoring and live-check through the registry

**Files:**
- Modify: `lms/lms/doctype/lms_quiz/lms_quiz.py` — `submit()` (~lines 171-181) and `check_answer()` (~lines 314-318).

**Interfaces:**
- Consumes: `get_question_type` from `lms.lms.question_types`.
- Produces: `submit()` and `check_answer()` branch via the registry; `verify_answer`, `check_input_answers`, `check_choice_answers`, `get_question_details` remain unchanged (plugins + tests use them).

- [ ] **Step 1: Existing tests cover this**

`test_scores_question_with_ten_options`, `test_legacy_two_option_question_still_scores` (call `verify_answer` directly), `test_user_input_matches_seventh_possibility` (calls `check_input_answers` directly). These call the helpers directly, so they pin the delegated logic. Keep them untouched.

- [ ] **Step 2: Replace the scoring branch in `submit()`**

In `lms/lms/doctype/lms_quiz/lms_quiz.py`, inside the `for result in results:` loop, replace this block:

```python
		if question_details.type != "Open Ended":
			if question_details.type == "User Input":
				correct = bool(check_input_answers(question_details.question, result["answer"][0]))
			else:
				correct = verify_answer(question_details.question, result["answer"])
			result["answer"] = ", ".join(result["answer"])
			if correct:
				result["marks"] = question_details.marks
			else:
				result["marks"] = -quiz_details.marks_to_cut if quiz_details.enable_negative_marking else 0
			result["is_correct"] = 1 if correct else 0

		else:
```

with:

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

		else:
```

(The `else:` open-ended block below it — sanitize + `_save_file` image handling — stays exactly as-is.)

- [ ] **Step 3: Replace the branch in `check_answer()`**

Replace:

```python
	answers = answers and json.loads(answers)
	if question_type == "Choices":
		return check_choice_answers(question, answers)
	else:
		return check_input_answers(question, answers[0])
```

with:

```python
	answers = answers and json.loads(answers)
	return get_question_type(question_type).live_check(question, answers)
```

Note: the `check_answer` parameter is named `question_type` (a string). `get_question_type(question_type)` resolves it to the plugin. Confirm the local string variable name doesn't shadow the import — it does not, because `get_question_type` is the imported function and `question_type` is the string arg.

- [ ] **Step 4: Add the import**

At the top of `lms/lms/doctype/lms_quiz/lms_quiz.py`, add to the imports:

```python
from lms.lms.question_types import get_question_type
```

Place it with the other `from lms...` imports. This is safe (no circular import at module load: `question_types/__init__.py` imports the plugin classes, which import `lms_quiz` only inside functions).

- [ ] **Step 5: Local syntax check**

Run: `python -m py_compile lms/lms/doctype/lms_quiz/lms_quiz.py`
Expected: exit 0.

- [ ] **Step 6: Commit & push**

```bash
git add lms/lms/doctype/lms_quiz/lms_quiz.py
git commit -m "refactor(quiz): dispatch scoring and live-check through registry"
git push
```

Verification gate: **full "Server Tests" run green** — this is the spec's primary success criterion. Confirm `TestLMSQuiz` and `TestQuizAnswerImageUpload` both pass, plus all `test_question_types.py` cases.

---

## Self-Review

- **Spec coverage:**
  - "Add `data` JSON field" → Task 5. ✓
  - "Registry mapping type→plugin" → Task 1. ✓
  - "Replace four branch points" → validation (Task 6), submit scoring + check_answer (Task 7). The fourth point (frontend `Question.vue` + player) is the **frontend plan**. ✓
  - "type allowed values come from the registry" → partially: Task 1's `test_registry_matches_doctype_select_options` guards drift between the Select and the registry. **Intentional scope choice:** the Select stays the source of allowed values with a guard test, rather than converting `type` to a dynamic/Link field now. Full dynamic typing is deferred to the new-types spec. (Flag to user — override if you want a Link DocType instead.)
  - "Existing types re-homed, zero behavior change" → Tasks 2-4 delegate; Tasks 6-7 dispatch; `test_lms_quiz.py` untouched. ✓
- **Placeholder scan:** none.
- **Type consistency:** `get_question_type` / `get_question_type_names` / `is_auto_graded` / `has_live_check` / `score` / `live_check` / `validate` / `read_config` used consistently across all tasks. ✓
- **Note on TDD loop:** because backend tests run only in CI, the per-step local "see it fail" is replaced by `py_compile` + JSON-validity checks locally, with the red/green gate at each push. Tasks 1-4 are pushed together (the package must import as a unit).
