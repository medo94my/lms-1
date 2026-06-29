<template>
	<div class="mt-2">
		<draggable
			v-model="order"
			:item-key="(item) => item"
			handle=".drag-handle"
			:disabled="showAnswers.length > 0"
		>
			<template #item="{ element, index }">
				<div
					class="flex items-center gap-2 bg-surface-gray-3 rounded-md p-3 mb-2"
				>
					<span
						class="drag-handle lucide-grip-vertical size-4 text-ink-gray-5 cursor-grab"
						:class="{ 'opacity-40': showAnswers.length }"
					/>
					<span
						class="flex-1 text-ink-gray-9"
						dir="auto"
						v-html="sanitizeRichHTML(element)"
					/>
					<span
						v-if="showAnswers.length && perPosition[index] === 1"
						class="lucide-check-circle w-4 h-4 text-ink-green-5"
					/>
					<span
						v-else-if="showAnswers.length && perPosition[index] === 0"
						class="lucide-x-circle w-4 h-4 text-ink-red-6"
					/>
					<template v-else>
						<Button
							variant="ghost"
							size="sm"
							:disabled="index === 0"
							:aria-label="__('Move up')"
							@click="move(index, -1)"
						>
							<span class="lucide-chevron-up size-4" />
						</Button>
						<Button
							variant="ghost"
							size="sm"
							:disabled="index === order.length - 1"
							:aria-label="__('Move down')"
							@click="move(index, 1)"
						>
							<span class="lucide-chevron-down size-4" />
						</Button>
					</template>
				</div>
			</template>
		</draggable>
	</div>
</template>
<script setup>
import { computed, watch } from 'vue'
import { Button } from 'frappe-ui'
import draggable from 'vuedraggable'
import { parseConfig } from '@/questionTypes/util'
import { sanitizeRichHTML } from '@/utils/sanitizeRichHTML'

const props = defineProps({
	question: { type: Object, required: true },
	showAnswers: { type: Array, default: () => [] },
	quizShowAnswers: { type: Boolean, default: false },
})
const state = defineModel('state')
const items = computed(() => parseConfig(props.question).items || [])
const perPosition = computed(() =>
	props.showAnswers.length ? props.showAnswers[0] || [] : []
)

const order = computed({
	get: () => state.value?.order || [],
	set: (val) => {
		state.value = { order: val }
	},
})

// Items arrive pre-shuffled from the server (player_config). Seed the learner's
// working order from them, unless a saved answer was already restored.
watch(
	items,
	(newItems) => {
		if (!newItems.length || order.value.length) return
		order.value = [...newItems]
	},
	{ immediate: true }
)

const move = (index, delta) => {
	const target = index + delta
	if (target < 0 || target >= order.value.length) return
	const next = [...order.value]
	;[next[index], next[target]] = [next[target], next[index]]
	order.value = next
}
</script>
