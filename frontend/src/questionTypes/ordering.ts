import type { QuestionTypeDef } from './types'
import { parseConfig } from './util'
import OrderingAuthor from './components/OrderingAuthor.vue'
import OrderingPlayer from './components/OrderingPlayer.vue'

const Ordering: QuestionTypeDef = {
	name: 'Ordering',
	label: 'Ordering',
	autoGraded: true,
	hasLiveCheck: true,
	defaultConfig() {
		return { data: { items: ['', ''] } }
	},
	getAnswers(question, state) {
		const items = parseConfig(question).items || []
		const order = state?.order || []
		return items.map((_: any, i: number) => order[i] ?? '')
	},
	loadAnswer(_question, savedAnswers) {
		return { order: savedAnswers ?? [] }
	},
	AuthorComponent: OrderingAuthor,
	PlayerComponent: OrderingPlayer,
}

export default Ordering
