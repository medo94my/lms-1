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
