<template>
	<div class="space-y-4">
		<div>
			<label class="block text-p-sm-medium text-ink-gray-7 mb-1.5">
				{{ __('Correct answer') }}
			</label>
			<div class="flex gap-2">
				<Button
					:variant="config.correct === true ? 'solid' : 'subtle'"
					@click="setCorrect(true)"
				>
					{{ __('True') }}
				</Button>
				<Button
					:variant="config.correct === false ? 'solid' : 'subtle'"
					@click="setCorrect(false)"
				>
					{{ __('False') }}
				</Button>
			</div>
		</div>
		<FormControl
			type="textarea"
			:label="__('Explanation (optional)')"
			:model-value="config.explanation"
			@update:model-value="(v) => set('explanation', v)"
		/>
	</div>
</template>
<script setup>
import { computed, watch } from 'vue'
import { FormControl, Button } from 'frappe-ui'
import { parseConfig } from '@/questionTypes/util'

const question = defineModel('question')
const config = computed(() => parseConfig(question.value))

// Ensure data exists with defaults on first mount / type switch.
watch(
	question,
	(q) => {
		if (!q) return
		const c = parseConfig(q)
		if (c.correct === undefined) {
			question.value.data = { correct: true, explanation: c.explanation || '' }
		} else if (typeof q.data === 'string') {
			question.value.data = c
		}
	},
	{ immediate: true }
)

const set = (key, value) => {
	question.value.data = { ...parseConfig(question.value), [key]: value }
}
const setCorrect = (v) => set('correct', v)
</script>
