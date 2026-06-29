import type { QuestionTypeDef } from './types'
import choices from './choices'
import userInput from './userInput'
import openEnded from './openEnded'
import trueFalse from './trueFalse'
import fillBlank from './fillBlank'

const REGISTRY: Record<string, QuestionTypeDef> = {}

function register(def: QuestionTypeDef) {
	REGISTRY[def.name] = def
}

register(choices)
register(userInput)
register(openEnded)
register(trueFalse)
register(fillBlank)

export function getQuestionType(name: string): QuestionTypeDef {
	const def = REGISTRY[name]
	if (!def) throw new Error(`Unknown question type: ${name}`)
	return def
}

export function questionTypeNames(): string[] {
	return Object.keys(REGISTRY)
}

export function questionTypeOptions(): string[] {
	return Object.values(REGISTRY).map((d) => d.name)
}
