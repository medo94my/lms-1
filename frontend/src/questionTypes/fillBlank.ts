import type { QuestionTypeDef } from './types'
import { parseConfig } from './util'
import FillBlankAuthor from './components/FillBlankAuthor.vue'
import FillBlankPlayer from './components/FillBlankPlayer.vue'

const FillBlank: QuestionTypeDef = {
	name: 'Fill in the Blank',
	label: 'Fill in the Blank',
	autoGraded: true,
	hasLiveCheck: true,
	defaultConfig() {
		return { data: { blanks: [{ label: '1', accepted: [] }] } }
	},
	getAnswers(question, state) {
		const blanks = parseConfig(question).blanks || []
		const values = state?.values || []
		return blanks.map((_: any, i: number) => values[i] ?? '')
	},
	loadAnswer(_question, savedAnswers) {
		return { values: savedAnswers ?? [] }
	},
	AuthorComponent: FillBlankAuthor,
	PlayerComponent: FillBlankPlayer,
}

export default FillBlank
