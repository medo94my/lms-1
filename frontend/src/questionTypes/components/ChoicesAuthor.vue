<template>
	<div>
		<div class="text-base-semibold text-ink-gray-9 mb-5 mt-10">
			{{ __('Options') }}
		</div>
		<div class="grid grid-cols-2 gap-x-8 gap-y-4">
			<div v-for="n in visibleOptionCount" :key="n" class="space-y-4 py-2">
				<div class="flex items-center justify-between">
					<label class="block text-p-sm-medium text-ink-gray-7">
						{{ __('Option {0}', [n]) }}
					</label>
					<Button
						v-if="visibleOptionCount > 2"
						variant="ghost"
						size="sm"
						:aria-label="__('Remove option {0}', [n])"
						@click="removeOption(n)"
					>
						<span class="lucide-trash-2 size-4" />
					</Button>
				</div>
				<FormControl
					v-model="question[`option_${n}`]"
					:required="n <= 2 ? true : false"
				/>
				<FormControl
					:label="__('Explanation')"
					v-model="question[`explanation_${n}`]"
				/>
				<BooleanSwitch
					size="sm"
					:label="__('Correct Answer')"
					:description="__('Mark this option as a correct answer.')"
					v-model="question[`is_correct_${n}`]"
				/>
			</div>
		</div>
		<div class="mt-4">
			<Button v-if="visibleOptionCount < MAX_OPTIONS" @click="addOption()">
				<template #prefix>
					<span class="lucide-plus size-4" />
				</template>
				{{ __('Add Option') }}
			</Button>
		</div>
	</div>
</template>
<script setup>
import { ref, watch } from 'vue'
import { FormControl, Button } from 'frappe-ui'
import BooleanSwitch from '@/components/Controls/BooleanSwitch.vue'

const MAX_OPTIONS = 10
const question = defineModel('question')
const visibleOptionCount = ref(2)

// Restore the visible count when editing an existing question. `deep` is
// required: `question` is a ModelRef over the host's reactive object, mutated in
// place (never replaced) when questionData.onSuccess loads the saved option_N
// fields after this component has already mounted with empty defaults.
// The recompute is grow-only: it raises the count to reveal saved options but
// never lowers it, so a just-added empty row (e.g. option_3 still null) is not
// snapped away by a keystroke elsewhere. removeOption decrements explicitly.
watch(
	question,
	(q) => {
		if (!q) return
		const populated = Math.max(
			2,
			...Array.from({ length: MAX_OPTIONS }, (_, i) =>
				q[`option_${i + 1}`] ? i + 1 : 0,
			),
		)
		if (populated > visibleOptionCount.value)
			visibleOptionCount.value = populated
	},
	{ immediate: true, deep: true },
)

const addOption = () => {
	if (visibleOptionCount.value < MAX_OPTIONS) visibleOptionCount.value++
}

const removeOption = (pos) => {
	if (visibleOptionCount.value <= 2) return
	for (let n = pos; n < visibleOptionCount.value; n++) {
		question.value[`option_${n}`] = question.value[`option_${n + 1}`]
		question.value[`is_correct_${n}`] = question.value[`is_correct_${n + 1}`]
		question.value[`explanation_${n}`] = question.value[`explanation_${n + 1}`]
	}
	const last = visibleOptionCount.value
	question.value[`option_${last}`] = null
	question.value[`is_correct_${last}`] = false
	question.value[`explanation_${last}`] = null
	visibleOptionCount.value--
}
</script>
