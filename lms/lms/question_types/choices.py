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
