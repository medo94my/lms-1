import { describe, it, expect } from 'vitest'
import { getQuestionType, questionTypeNames } from '@/questionTypes'

describe('question type registry', () => {
	it('registers the three existing types', () => {
		const names = questionTypeNames()
		expect(names).toContain('Choices')
		expect(names).toContain('User Input')
		expect(names).toContain('Open Ended')
	})

	it('throws on an unknown type', () => {
		expect(() => getQuestionType('Nope')).toThrow()
	})
})

import { getQuestionType as gt } from '@/questionTypes'

describe('Choices helpers', () => {
	const question = {
		type: 'Choices',
		option_1: 'a',
		option_2: 'b',
		option_3: 'c',
	}

	it('getAnswers returns the selected option labels', () => {
		const def = gt('Choices')
		const answers = def.getAnswers(question, {
			selectedOptions: [1, 0, 1, ...Array(7).fill(0)],
		})
		expect(answers).toEqual(['a', 'c'])
	})

	it('loadAnswer marks the saved options as selected', () => {
		const def = gt('Choices')
		const state = def.loadAnswer(question, ['b'])
		expect(state.selectedOptions[1]).toBe(1)
		expect(state.selectedOptions[0]).toBe(0)
	})
})

describe('User Input helpers', () => {
	it('getAnswers wraps the text answer in an array', () => {
		const def = gt('User Input')
		expect(def.getAnswers({}, { possibleAnswer: 'hello' })).toEqual(['hello'])
	})
	it('loadAnswer restores the first saved answer', () => {
		const def = gt('User Input')
		expect(def.loadAnswer({}, ['hi']).possibleAnswer).toBe('hi')
	})
})

describe('Open Ended helpers', () => {
	it('is not auto-graded and has no live check', () => {
		const def = gt('Open Ended')
		expect(def.autoGraded).toBe(false)
		expect(def.hasLiveCheck).toBe(false)
	})
})
