<template>
	<TextEditor
		class="mt-4"
		:content="state?.possibleAnswer"
		@change="(val) => (state = { possibleAnswer: val })"
		:editable="true"
		:fixedMenu="true"
		editorClass="prose-sm max-w-none border-b border-x border-outline-elevation-2 bg-surface-gray-2 rounded-b-md py-1 px-2 min-h-[7rem]"
	/>
</template>
<script setup>
import { TextEditor } from 'frappe-ui'

defineProps({
	question: { type: Object, required: true },
	showAnswers: { type: Array, default: () => [] },
	quizShowAnswers: { type: Boolean, default: false },
})
const state = defineModel('state')
</script>
