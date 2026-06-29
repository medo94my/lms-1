# Copyright (c) 2026, Frappe and contributors
# See license.txt

import json
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
