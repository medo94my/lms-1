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
