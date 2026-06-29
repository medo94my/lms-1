<template>
	<div class="space-y-3 mt-2">
		<div v-for="(blank, i) in blanks" :key="i" class="space-y-1">
			<label class="text-p-sm-medium text-ink-gray-7">
				{{ __('Blank {0}', [i + 1]) }}
			</label>
			<div class="flex items-center gap-2">
				<FormControl
					class="flex-1"
					:model-value="values[i] || ''"
					:disabled="showAnswers.length > 0"
					@update:model-value="(v) => setValue(i, v)"
				/>
				<span
					v-if="showAnswers.length && perBlank[i] === 1"
					class="lucide-check-circle w-4 h-4 text-ink-green-5"
				/>
				<span
					v-else-if="showAnswers.length && perBlank[i] === 0"
					class="lucide-x-circle w-4 h-4 text-ink-red-6"
				/>
			</div>
			<div
				v-if="showAnswers.length && perBlank[i] === 0"
				class="text-xs text-ink-gray-6"
			>
				{{ __('Accepted:') }}
				<bdi>{{ (blank.accepted || []).join('، ') }}</bdi>
			</div>
		</div>
	</div>
</template>
<script setup>
import { computed } from 'vue'
import { FormControl } from 'frappe-ui'
import { parseConfig } from '@/questionTypes/util'

const props = defineProps({
	question: { type: Object, required: true },
	showAnswers: { type: Array, default: () => [] },
	quizShowAnswers: { type: Boolean, default: false },
})
const state = defineModel('state')
const blanks = computed(() => parseConfig(props.question).blanks || [])
const values = computed(() => state.value?.values || [])
// checkAnswer pushes the per-blank array as showAnswers[0].
const perBlank = computed(() =>
	props.showAnswers.length ? props.showAnswers[0] || [] : []
)

const setValue = (i, v) => {
	const next = blanks.value.map((_, idx) => values.value[idx] ?? '')
	next[i] = v
	state.value = { values: next }
}
</script>
