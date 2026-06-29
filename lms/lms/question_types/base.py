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
