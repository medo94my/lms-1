<template>
	<div class="space-y-3 mt-2">
		<div v-for="(left, i) in lefts" :key="i" class="flex items-center gap-3">
			<div class="flex-1 text-ink-gray-9" v-html="sanitizeRichHTML(left)" />
			<FormControl
				class="flex-1"
				type="select"
				:options="selectOptions"
				:model-value="selections[i] || ''"
				:disabled="showAnswers.length > 0"
				@update:model-value="(v) => setSelection(i, v)"
			/>
			<span
				v-if="showAnswers.length && perPair[i] === 1"
				class="lucide-check-circle w-4 h-4 text-ink-green-5"
			/>
			<span
				v-else-if="showAnswers.length && perPair[i] === 0"
				class="lucide-x-circle w-4 h-4 text-ink-red-6"
			/>
		</div>
	</div>
</template>
<script setup>
import { computed } from 'vue'
import { FormControl } from 'frappe-ui'
import { parseConfig } from '@/questionTypes/util'
import { sanitizeRichHTML } from '@/utils/sanitizeRichHTML'

const props = defineProps({
	question: { type: Object, required: true },
	showAnswers: { type: Array, default: () => [] },
	quizShowAnswers: { type: Boolean, default: false },
})
const state = defineModel('state')
const lefts = computed(() => parseConfig(props.question).lefts || [])
const rights = computed(() => parseConfig(props.question).rights || [])
const selections = computed(() => state.value?.selections || [])
const perPair = computed(() =>
	props.showAnswers.length ? props.showAnswers[0] || [] : []
)

// Rights arrive pre-shuffled from the server (player_config); use as-is.
const selectOptions = computed(() => [
	{ label: __('Select…'), value: '' },
	...rights.value.map((r) => ({ label: r, value: r })),
])

const setSelection = (i, v) => {
	const next = lefts.value.map((_, idx) => selections.value[idx] ?? '')
	next[i] = v
	state.value = { selections: next }
}
</script>
