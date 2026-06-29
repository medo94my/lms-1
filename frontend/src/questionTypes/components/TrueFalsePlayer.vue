<template>
	<div class="space-y-3 mt-2">
		<label
			v-for="opt in options"
			:key="opt.value"
			class="flex items-center bg-surface-gray-3 rounded-md p-3 w-full cursor-pointer"
		>
			<input
				v-if="!showAnswers.length"
				type="radio"
				class="w-3.5 h-3.5 text-ink-gray-9"
				:name="encodeURIComponent(question.question)"
				:checked="state?.choice === opt.value"
				@change="select(opt.value)"
			/>
			<span class="ms-2 text-ink-gray-9">{{ opt.label }}</span>
		</label>
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
import { Badge } from 'frappe-ui'

defineProps({
	question: { type: Object, required: true },
	showAnswers: { type: Array, default: () => [] },
	quizShowAnswers: { type: Boolean, default: false },
})
const state = defineModel('state')
const options = [
	{ value: 'true', label: __('True') },
	{ value: 'false', label: __('False') },
]
const select = (value) => {
	state.value = { choice: value }
}
</script>
