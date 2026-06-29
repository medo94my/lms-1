<template>
	<div class="space-y-4">
		<div class="text-base-semibold text-ink-gray-9">{{ __('Blanks') }}</div>
		<p class="text-xs text-ink-gray-6">
			{{
				__(
					'Reference blanks in your question text as (1), (2), … Learners fill them in order.'
				)
			}}
		</p>
		<div
			v-for="(blank, i) in blanks"
			:key="i"
			class="border border-outline-elevation-2 rounded-md p-3 space-y-2"
		>
			<div class="flex items-center justify-between">
				<label class="text-p-sm-medium text-ink-gray-7">
					{{ __('Blank {0}', [i + 1]) }}
				</label>
				<Button
					v-if="blanks.length > 1"
					variant="ghost"
					size="sm"
					:aria-label="__('Remove blank {0}', [i + 1])"
					@click="removeBlank(i)"
				>
					<span class="lucide-trash-2 size-4" />
				</Button>
			</div>
			<FormControl
				type="textarea"
				:label="__('Accepted answers (one per line)')"
				:model-value="(blank.accepted || []).join('\n')"
				@update:model-value="(v) => setAccepted(i, v)"
			/>
		</div>
		<Button @click="addBlank">
			<template #prefix><span class="lucide-plus size-4" /></template>
			{{ __('Add Blank') }}
		</Button>
	</div>
</template>
<script setup>
import { computed, watch } from 'vue'
import { FormControl, Button } from 'frappe-ui'
import { parseConfig } from '@/questionTypes/util'

const question = defineModel('question')
const blanks = computed(() => parseConfig(question.value).blanks || [])

// `deep` is required: `question` is a ModelRef over the host's reactive object,
// mutated in place (never replaced) when questionData.onSuccess loads the saved
// `data` field after this component has already mounted with empty defaults.
// A shallow watch would stay silent and the author UI would show zero blanks.
watch(
	question,
	(q) => {
		if (!q) return
		const c = parseConfig(q)
		if (!c.blanks) {
			question.value.data = { blanks: [{ label: '1', accepted: [] }] }
		} else if (typeof q.data === 'string') {
			question.value.data = c
		}
	},
	{ immediate: true, deep: true }
)

const write = (next) => {
	question.value.data = { blanks: next }
}
const setAccepted = (i, text) => {
	const next = blanks.value.map((b) => ({ ...b }))
	next[i].accepted = text
		.split('\n')
		.map((s) => s.trim())
		.filter(Boolean)
	write(next)
}
const addBlank = () => {
	const next = blanks.value.map((b) => ({ ...b }))
	next.push({ label: String(next.length + 1), accepted: [] })
	write(next)
}
const removeBlank = (i) => {
	const next = blanks.value.filter((_, idx) => idx !== i)
	next.forEach((b, idx) => (b.label = String(idx + 1)))
	write(next)
}
</script>
