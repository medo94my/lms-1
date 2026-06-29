<template>
	<div v-for="index in MAX_OPTIONS" :key="index">
		<label
			v-if="question[`option_${index}`]"
			class="flex items-center bg-surface-gray-3 rounded-md p-3 mt-4 w-full cursor-pointer focus:border-primary-600"
		>
			<input
				v-if="!showAnswers.length && !question.multiple"
				type="radio"
				:name="encodeURIComponent(question.question)"
				class="w-3.5 h-3.5 text-ink-gray-9 focus:ring-outline-elevation-2"
				@change="markAnswer(index)"
				:checked="selected[index - 1]"
			/>
			<input
				v-else-if="!showAnswers.length && question.multiple"
				type="checkbox"
				:name="encodeURIComponent(question.question)"
				class="w-3.5 h-3.5 text-ink-gray-9 rounded-sm focus:ring-outline-elevation-2"
				@change="markAnswer(index)"
				:checked="selected[index - 1]"
			/>
			<div
				v-else-if="quizShowAnswers"
				v-for="(answer, idx) in showAnswers"
				:key="idx"
			>
				<div v-if="index - 1 == idx">
					<span
						v-if="answer == 1"
						class="lucide-check-circle w-4 h-4 text-ink-green-5"
					/>
					<span
						v-else-if="answer == 2"
						class="lucide-minus-circle w-4 h-4 text-ink-green-5"
					/>
					<span
						v-else-if="answer == 0"
						class="lucide-x-circle w-4 h-4 text-ink-red-6"
					/>
					<span v-else class="lucide-minus-circle w-4 h-4" />
				</div>
			</div>
			<span
				class="ms-2 text-ink-gray-9"
				v-html="sanitizeRichHTML(question[`option_${index}`])"
			/>
		</label>
		<div
			v-if="question[`explanation_${index}`]"
			class="mt-2 text-xs text-ink-gray-7"
			v-show="showAnswers.length"
		>
			{{ question[`explanation_${index}`] }}
		</div>
	</div>
</template>
<script setup>
import { computed } from 'vue'
import { sanitizeRichHTML } from '@/utils/sanitizeRichHTML'

const MAX_OPTIONS = 10
const props = defineProps({
	question: { type: Object, required: true },
	showAnswers: { type: Array, default: () => [] },
	quizShowAnswers: { type: Boolean, default: false },
})
const state = defineModel('state')
const selected = computed(
	() => state.value?.selectedOptions || Array(MAX_OPTIONS).fill(0)
)

const markAnswer = (index) => {
	const next = props.question.multiple
		? [...selected.value]
		: Array(MAX_OPTIONS).fill(0)
	next[index - 1] = selected.value[index - 1] ? 0 : 1
	state.value = { selectedOptions: next }
}
</script>
