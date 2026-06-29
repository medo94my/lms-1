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
