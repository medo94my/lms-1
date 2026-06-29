import { describe, it, expect, vi } from 'vitest'

// Importing @/questionTypes pulls in the author components, which import
// frappe-ui — and frappe-ui's internal extensionless ESM imports fail under
// Node's strict resolver in Vitest. Stub the few named exports the transitive
// graph touches (FormControl/Button from the author components, Switch from
// BooleanSwitch). The test only calls registry helper fns, never mounts, so
// minimal template stubs suffice. Scoped to THIS file so no other spec is
// affected.
vi.mock('frappe-ui', () => ({
	FormControl: { template: '<input />' },
	Button: { template: '<button><slot /></button>' },
	Switch: { template: '<input type="checkbox" />' },
	Badge: { template: '<span><slot /></span>' },
	TextEditor: { template: '<div />' },
}))

import {
	getQuestionType,
	questionTypeNames,
	questionTypeOptions,
} from '@/questionTypes'
import { parseConfig } from '@/questionTypes/util'

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

describe('Choices helpers', () => {
	const question = {
		type: 'Choices',
		option_1: 'a',
		option_2: 'b',
		option_3: 'c',
	}

	it('getAnswers returns the selected option labels', () => {
		const def = getQuestionType('Choices')
		const answers = def.getAnswers(question, {
			selectedOptions: [1, 0, 1, ...Array(7).fill(0)],
		})
		expect(answers).toEqual(['a', 'c'])
	})

	it('loadAnswer marks the saved options as selected', () => {
		const def = getQuestionType('Choices')
		const state = def.loadAnswer(question, ['b'])
		expect(state.selectedOptions[1]).toBe(1)
		expect(state.selectedOptions[0]).toBe(0)
	})
})

describe('User Input helpers', () => {
	it('getAnswers wraps the text answer in an array', () => {
		const def = getQuestionType('User Input')
		expect(def.getAnswers({}, { possibleAnswer: 'hello' })).toEqual(['hello'])
	})
	it('loadAnswer restores the first saved answer', () => {
		const def = getQuestionType('User Input')
		expect(def.loadAnswer({}, ['hi']).possibleAnswer).toBe('hi')
	})
})

describe('Open Ended helpers', () => {
	it('is not auto-graded and has no live check', () => {
		const def = getQuestionType('Open Ended')
		expect(def.autoGraded).toBe(false)
		expect(def.hasLiveCheck).toBe(false)
	})
})

describe('framework touch-ups', () => {
	it('questionTypeOptions returns names (not labels)', () => {
		const opts = questionTypeOptions()
		expect(opts).toContain('Choices')
		expect(opts).toContain('User Input')
		expect(opts).toContain('Open Ended')
	})
	it('parseConfig handles object and JSON string', () => {
		expect(parseConfig({ data: { a: 1 } })).toEqual({ a: 1 })
		expect(parseConfig({ data: '{"a":2}' })).toEqual({ a: 2 })
		expect(parseConfig({})).toEqual({})
		expect(parseConfig({ data: null })).toEqual({})
	})
})

describe('True/False helpers', () => {
	it('getAnswers wraps the choice', () => {
		expect(
			getQuestionType('True/False').getAnswers({}, { choice: 'true' })
		).toEqual(['true'])
	})
	it('loadAnswer restores the choice', () => {
		expect(getQuestionType('True/False').loadAnswer({}, ['false']).choice).toBe(
			'false'
		)
	})
})
