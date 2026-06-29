<template>
	<div>
		<FormControl
			:model-value="state?.possibleAnswer"
			@update:model-value="(v) => (state = { possibleAnswer: v })"
			type="textarea"
			:disabled="showAnswers.length ? true : false"
			class="my-2"
		/>
		<div v-if="showAnswers.length">
			<Badge v-if="showAnswers[0]" :label="__('Correct')" theme="green">
				<template #prefix>
					<span class="lucide-check-circle w-4 h-4 text-ink-green-5 me-1" />
				</template>
			</Badge>
			<Badge v-else theme="red" :label="__('Incorrect')">
				<template #prefix>
					<span class="lucide-x-circle w-4 h-4 text-ink-red-6 me-1" />
				</template>
			</Badge>
		</div>
	</div>
</template>
<script setup>
import { FormControl, Badge } from 'frappe-ui'

defineProps({
	question: { type: Object, required: true },
	showAnswers: { type: Array, default: () => [] },
	quizShowAnswers: { type: Boolean, default: false },
})
const state = defineModel('state')
</script>
