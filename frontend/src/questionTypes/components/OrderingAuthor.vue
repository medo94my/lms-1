<template>
	<div class="space-y-4">
		<div class="text-base-semibold text-ink-gray-9">
			{{ __('Items in correct order') }}
		</div>
		<p class="text-xs text-ink-gray-6">
			{{
				__(
					'Enter items in the correct order. Learners will see them shuffled. Use distinct values.'
				)
			}}
		</p>
		<div v-for="(item, i) in items" :key="i" class="flex items-end gap-2">
			<FormControl
				class="flex-1"
				:label="__('Item {0}', [i + 1])"
				:model-value="item"
				@update:model-value="(v) => setItem(i, v)"
			/>
			<Button
				v-if="items.length > 2"
				variant="ghost"
				size="sm"
				:aria-label="__('Remove item {0}', [i + 1])"
				@click="removeItem(i)"
			>
				<span class="lucide-trash-2 size-4" />
			</Button>
		</div>
		<Button @click="addItem">
			<template #prefix><span class="lucide-plus size-4" /></template>
			{{ __('Add Item') }}
		</Button>
	</div>
</template>
<script setup>
import { computed, watch } from 'vue'
import { FormControl, Button } from 'frappe-ui'
import { parseConfig } from '@/questionTypes/util'

let question = defineModel('question')
const items = computed(() => parseConfig(question.value).items || [])

watch(
	question,
	(q) => {
		if (!q) return
		const c = parseConfig(q)
		if (!c.items) {
			question.value.data = { items: ['', ''] }
		} else if (typeof q.data === 'string') {
			question.value.data = c
		}
	},
	{ immediate: true, deep: true }
)

const write = (next) => {
	question.value.data = { items: next }
}
const setItem = (i, v) => {
	const next = [...items.value]
	next[i] = v
	write(next)
}
const addItem = () => {
	write([...items.value, ''])
}
const removeItem = (i) => {
	write(items.value.filter((_, idx) => idx !== i))
}
</script>
