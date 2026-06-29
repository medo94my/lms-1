<template>
	<div class="space-y-3 mt-2">
		<div v-for="(pair, i) in pairs" :key="i" class="flex items-center gap-3">
			<div
				class="flex-1 text-ink-gray-9"
				v-html="sanitizeRichHTML(pair.left)"
			/>
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
		<div v-if="showAnswers.length" class="text-xs text-ink-gray-6 space-y-1">
			<div v-for="(pair, i) in pairs" :key="i" v-show="perPair[i] === 0">
				{{ __('{0} → {1}', [stripTags(pair.left), pair.right]) }}
			</div>
		</div>
	</div>
</template>
<script setup>
import { computed, ref, onMounted } from 'vue'
import { FormControl } from 'frappe-ui'
import { parseConfig, shuffle } from '@/questionTypes/util'
import { sanitizeRichHTML } from '@/utils/sanitizeRichHTML'

const props = defineProps({
	question: { type: Object, required: true },
	showAnswers: { type: Array, default: () => [] },
	quizShowAnswers: { type: Boolean, default: false },
})
const state = defineModel('state')
const pairs = computed(() => parseConfig(props.question).pairs || [])
const selections = computed(() => state.value?.selections || [])
const perPair = computed(() =>
	props.showAnswers.length ? props.showAnswers[0] || [] : []
)

// Shuffle the right-hand options ONCE on mount (presentation only).
const shuffledRights = ref([])
onMounted(() => {
	shuffledRights.value = shuffle(pairs.value.map((p) => p.right))
})
const selectOptions = computed(() => [
	{ label: __('Select…'), value: '' },
	...shuffledRights.value.map((r) => ({ label: r, value: r })),
])

const stripTags = (html) => String(html || '').replace(/<[^>]*>/g, '')

const setSelection = (i, v) => {
	const next = pairs.value.map((_, idx) => selections.value[idx] ?? '')
	next[i] = v
	state.value = { selections: next }
}
</script>
