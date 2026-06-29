<template>
	<div class="space-y-4">
		<div class="text-base-semibold text-ink-gray-9">{{ __('Pairs') }}</div>
		<p class="text-xs text-ink-gray-6">
			{{
				__(
					'Each left item matches exactly one right item. Use distinct right values.'
				)
			}}
		</p>
		<div
			v-for="(pair, i) in pairs"
			:key="i"
			class="border border-outline-elevation-2 rounded-md p-3 grid grid-cols-2 gap-3"
		>
			<FormControl
				:label="__('Left {0}', [i + 1])"
				:model-value="pair.left"
				@update:model-value="(v) => setField(i, 'left', v)"
			/>
			<div class="flex items-end gap-2">
				<FormControl
					class="flex-1"
					:label="__('Right {0}', [i + 1])"
					:model-value="pair.right"
					@update:model-value="(v) => setField(i, 'right', v)"
				/>
				<Button
					v-if="pairs.length > 2"
					variant="ghost"
					size="sm"
					:aria-label="__('Remove pair {0}', [i + 1])"
					@click="removePair(i)"
				>
					<span class="lucide-trash-2 size-4" />
				</Button>
			</div>
		</div>
		<Button @click="addPair">
			<template #prefix><span class="lucide-plus size-4" /></template>
			{{ __('Add Pair') }}
		</Button>
	</div>
</template>
<script setup>
import { computed, watch } from 'vue'
import { FormControl, Button } from 'frappe-ui'
import { parseConfig } from '@/questionTypes/util'

let question = defineModel('question')
const pairs = computed(() => parseConfig(question.value).pairs || [])

watch(
	question,
	(q) => {
		if (!q) return
		const c = parseConfig(q)
		if (!c.pairs) {
			question.value.data = {
				pairs: [
					{ left: '', right: '' },
					{ left: '', right: '' },
				],
			}
		} else if (typeof q.data === 'string') {
			question.value.data = c
		}
	},
	{ immediate: true, deep: true }
)

const write = (next) => {
	question.value.data = { pairs: next }
}
const setField = (i, key, value) => {
	const next = pairs.value.map((p) => ({ ...p }))
	next[i][key] = value
	write(next)
}
const addPair = () => {
	write([...pairs.value.map((p) => ({ ...p })), { left: '', right: '' }])
}
const removePair = (i) => {
	write(pairs.value.filter((_, idx) => idx !== i).map((p) => ({ ...p })))
}
</script>
