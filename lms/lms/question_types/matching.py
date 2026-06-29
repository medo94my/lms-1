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
