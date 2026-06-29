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
