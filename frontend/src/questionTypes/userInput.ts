import type { QuestionTypeDef } from './types'
import UserInputAuthor from './components/UserInputAuthor.vue'
import UserInputPlayer from './components/UserInputPlayer.vue'

const MAX_OPTIONS = 10

const UserInput: QuestionTypeDef = {
	name: 'User Input',
	label: 'User Input',
	autoGraded: true,
	hasLiveCheck: true,

	defaultConfig() {
		const cfg: Record<string, any> = {}
		for (let n = 1; n <= MAX_OPTIONS; n++) cfg[`possibility_${n}`] = null
		return cfg
	},

	getAnswers(_question, state) {
		return [state?.possibleAnswer]
	},

	loadAnswer(_question, savedAnswers) {
		return { possibleAnswer: savedAnswers?.[0] ?? null }
	},

	AuthorComponent: UserInputAuthor,
	PlayerComponent: UserInputPlayer,
}

export default UserInput
