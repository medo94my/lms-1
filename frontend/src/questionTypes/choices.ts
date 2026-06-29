import type { QuestionTypeDef } from './types'
import ChoicesAuthor from './components/ChoicesAuthor.vue'
import ChoicesPlayer from './components/ChoicesPlayer.vue'

const MAX_OPTIONS = 10

const Choices: QuestionTypeDef = {
	name: 'Choices',
	label: 'Choices',
	autoGraded: true,
	hasLiveCheck: true,

	defaultConfig() {
		const cfg: Record<string, any> = {}
		for (let n = 1; n <= MAX_OPTIONS; n++) {
			cfg[`option_${n}`] = null
			cfg[`is_correct_${n}`] = false
			cfg[`explanation_${n}`] = null
		}
		return cfg
	},

	getAnswers(question, state) {
		const answers: string[] = []
		const selected: number[] = state?.selectedOptions || []
		selected.forEach((value, index) => {
			if (value) answers.push(question[`option_${index + 1}`])
		})
		return answers
	},

	loadAnswer(question, savedAnswers) {
		const selectedOptions = Array(MAX_OPTIONS).fill(0)
		;(savedAnswers || []).forEach((answer) => {
			for (let i = 1; i <= MAX_OPTIONS; i++) {
				if (question[`option_${i}`] === answer) selectedOptions[i - 1] = 1
			}
		})
		return { selectedOptions }
	},

	AuthorComponent: ChoicesAuthor,
	PlayerComponent: ChoicesPlayer,
}

export default Choices
