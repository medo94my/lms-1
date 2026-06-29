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


class TestQuestionDataField(unittest.TestCase):
	def test_data_field_exists(self):
		meta = frappe.get_meta("LMS Question")
		field = meta.get_field("data")
		self.assertIsNotNone(field)
		self.assertEqual(field.fieldtype, "JSON")


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


class TestLiveCheckGate(unittest.TestCase):
	def test_open_ended_has_no_live_check(self):
		self.assertFalse(get_question_type("Open Ended").has_live_check)
