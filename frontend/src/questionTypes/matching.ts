import type { QuestionTypeDef } from './types'
import { parseConfig } from './util'
import MatchingAuthor from './components/MatchingAuthor.vue'
import MatchingPlayer from './components/MatchingPlayer.vue'

const Matching: QuestionTypeDef = {
	name: 'Matching',
	label: 'Matching',
	autoGraded: true,
	hasLiveCheck: true,
	defaultConfig() {
		return {
			data: {
				pairs: [
					{ left: '', right: '' },
					{ left: '', right: '' },
				],
			},
		}
	},
	getAnswers(question, state) {
		const pairs = parseConfig(question).pairs || []
		const selections = state?.selections || []
		return pairs.map((_: any, i: number) => selections[i] ?? '')
	},
	loadAnswer(_question, savedAnswers) {
		return { selections: savedAnswers ?? [] }
	},
	AuthorComponent: MatchingAuthor,
	PlayerComponent: MatchingPlayer,
}

export default Matching
