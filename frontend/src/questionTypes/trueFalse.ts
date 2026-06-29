import type { QuestionTypeDef } from './types'
import TrueFalseAuthor from './components/TrueFalseAuthor.vue'
import TrueFalsePlayer from './components/TrueFalsePlayer.vue'

const TrueFalse: QuestionTypeDef = {
	name: 'True/False',
	label: 'True/False',
	autoGraded: true,
	hasLiveCheck: true,
	defaultConfig() {
		return { data: { correct: true, explanation: '' } }
	},
	getAnswers(_question, state) {
		return [state?.choice]
	},
	loadAnswer(_question, savedAnswers) {
		return { choice: savedAnswers?.[0] ?? null }
	},
	AuthorComponent: TrueFalseAuthor,
	PlayerComponent: TrueFalsePlayer,
}

export default TrueFalse
