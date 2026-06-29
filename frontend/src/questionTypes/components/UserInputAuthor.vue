<template>
	<div>
		<div class="text-base-semibold text-ink-gray-9 mb-5 mt-5">
			{{ __('Possibilities') }}
		</div>
		<div class="grid grid-cols-2 gap-x-8 gap-y-4 py-2">
			<div
				v-for="n in visiblePossibilityCount"
				:key="n"
				class="flex items-end gap-2"
			>
				<FormControl
					class="flex-1"
					:label="__('Possibility {0}', [n])"
					v-model="question[`possibility_${n}`]"
					:required="n == 1 ? true : false"
				/>
				<Button
					v-if="visiblePossibilityCount > 1"
					variant="ghost"
					:aria-label="__('Remove possibility {0}', [n])"
					@click="removePossibility(n)"
				>
					<span class="lucide-trash-2 size-4" />
				</Button>
			</div>
		</div>
		<div class="mt-4">
			<Button
				v-if="visiblePossibilityCount < MAX_OPTIONS"
				@click="addPossibility()"
			>
				<template #prefix>
					<span class="lucide-plus size-4" />
				</template>
				{{ __('Add Possibility') }}
			</Button>
		</div>
	</div>
</template>
<script setup>
import { ref, watch } from 'vue'
import { FormControl, Button } from 'frappe-ui'

const MAX_OPTIONS = 10
const question = defineModel('question')
const visiblePossibilityCount = ref(1)

// `deep` is required: `question` is a ModelRef over the host's reactive object,
// mutated in place (never replaced) when questionData.onSuccess loads the saved
// possibility_N fields after this component has already mounted with empty
// defaults. The recompute is grow-only: it raises the count to reveal saved
// possibilities but never lowers it, so a just-added empty row is not snapped
// away by a keystroke elsewhere. removePossibility decrements explicitly.
watch(
	question,
	(q) => {
		if (!q) return
		const populated = Math.max(
			1,
			...Array.from({ length: MAX_OPTIONS }, (_, i) =>
				q[`possibility_${i + 1}`] ? i + 1 : 0,
			),
		)
		if (populated > visiblePossibilityCount.value)
			visiblePossibilityCount.value = populated
	},
	{ immediate: true, deep: true },
)

const addPossibility = () => {
	if (visiblePossibilityCount.value < MAX_OPTIONS)
		visiblePossibilityCount.value++
}

const removePossibility = (pos) => {
	if (visiblePossibilityCount.value <= 1) return
	for (let n = pos; n < visiblePossibilityCount.value; n++) {
		question.value[`possibility_${n}`] = question.value[`possibility_${n + 1}`]
	}
	question.value[`possibility_${visiblePossibilityCount.value}`] = null
	visiblePossibilityCount.value--
}
</script>
