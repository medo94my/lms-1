import type { QuestionTypeDef } from './types'
import OpenEndedAuthor from './components/OpenEndedAuthor.vue'
import OpenEndedPlayer from './components/OpenEndedPlayer.vue'

const OpenEnded: QuestionTypeDef = {
	name: 'Open Ended',
	label: 'Open Ended',
	autoGraded: false,
	hasLiveCheck: false,

	defaultConfig() {
		return {}
	},

	getAnswers(_question, state) {
		return [state?.possibleAnswer]
	},

	loadAnswer(_question, savedAnswers) {
		return { possibleAnswer: savedAnswers?.[0] ?? null }
	},

	AuthorComponent: OpenEndedAuthor,
	PlayerComponent: OpenEndedPlayer,
}

export default OpenEnded
