# Copyright (c) 2026, Frappe and contributors
# For license information, please see license.txt

import frappe
from frappe import _

from lms.lms.question_types.base import QuestionType
from lms.lms.question_types.choices import ChoicesQuestion
from lms.lms.question_types.open_ended import OpenEndedQuestion
from lms.lms.question_types.true_false import TrueFalseQuestion
from lms.lms.question_types.user_input import UserInputQuestion

_REGISTRY: dict[str, QuestionType] = {}


def register(question_type: type[QuestionType]) -> None:
	instance = question_type()
	_REGISTRY[instance.name] = instance


def get_question_type(name: str) -> QuestionType:
	question_type = _REGISTRY.get(name)
	if question_type is None:
		frappe.throw(_("Unknown question type: {0}").format(name), frappe.ValidationError)
	return question_type


def get_question_type_names() -> list[str]:
	return list(_REGISTRY.keys())


register(ChoicesQuestion)
register(UserInputQuestion)
register(OpenEndedQuestion)
register(TrueFalseQuestion)
