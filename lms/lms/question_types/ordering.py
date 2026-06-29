# Copyright (c) 2026, Frappe and contributors
# For license information, please see license.txt

import random

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

	def player_config(self, question) -> dict:
		items = [str(i) for i in (frappe.parse_json(question.get("data") or "{}").get("items") or [])]
		shuffled = items[:]
		# Avoid presenting the already-correct order for 2+ items. Bounded so a
		# list with duplicate values (which can never differ) cannot loop forever.
		for _attempt in range(10):
			random.SystemRandom().shuffle(shuffled)
			if len(items) < 2 or shuffled != items:
				break
		return {"items": shuffled}
