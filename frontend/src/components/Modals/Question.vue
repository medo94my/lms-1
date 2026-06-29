<template>
	<Dialog v-model:open="show" size="3xl">
		<template #body>
			<div class="p-5 space-y-5">
				<div class="text-xl-semibold text-ink-gray-9 mb-5">
					{{ __(props.title) }}
				</div>
				<BooleanSwitch
					v-if="!editMode"
					size="sm"
					:label="__('Choose an existing question')"
					:description="__('Select from questions you have already created')"
					v-model="chooseFromExisting"
					class="!p-0"
				/>
				<div v-if="!chooseFromExisting || editMode">
					<div>
						<label class="block text-p-sm-medium text-ink-gray-7 mb-1.5">
							{{ __('Question') }}
						</label>
						<TextEditor
							:content="question.question"
							@change="(val) => (question.question = val)"
							:editable="true"
							:fixedMenu="true"
							editorClass="prose-sm max-w-none border-b border-x border-outline-elevation-2 bg-surface-gray-2 rounded-b-md py-1 px-2 min-h-[7rem]"
						/>
					</div>
					<div class="grid grid-cols-2 gap-8 mt-4">
						<FormControl
							v-model="question.marks"
							:label="__('Marks')"
							type="number"
						/>
						<FormControl
							:label="__('Type')"
							v-model="question.type"
							type="select"
							:options="questionTypeOptions()"
							class="pb-2"
							:required="true"
						/>
					</div>
					<component
						:is="getQuestionType(question.type).AuthorComponent"
						v-model:question="question"
					/>
				</div>
				<div v-else-if="chooseFromExisting" class="space-y-2">
					<Link
						v-model="existingQuestion.question"
						:label="__('Select a question')"
						doctype="LMS Question"
					/>
					<FormControl
						v-model="existingQuestion.marks"
						:label="__('Marks')"
						type="number"
					/>
				</div>
				<div class="flex items-center justify-end gap-x-2 mt-5">
					<Button variant="solid" @click="submitQuestion()">
						{{ __('Save') }}
					</Button>
				</div>
			</div>
		</template>
	</Dialog>
</template>
<script setup>
import {
	Dialog,
	FormControl,
	TextEditor,
	createResource,
	Button,
	toast,
} from 'frappe-ui'
import BooleanSwitch from '@/components/Controls/BooleanSwitch.vue'
import { watch, reactive, ref, inject } from 'vue'
import Link from '@/components/Controls/Link.vue'
import { useOnboarding } from 'frappe-ui/frappe'
import { getQuestionType, questionTypeOptions } from '@/questionTypes'

const show = defineModel()
const quiz = defineModel('quiz')
const chooseFromExisting = ref(false)
const editMode = ref(false)
const user = inject('$user')
const { updateOnboardingStep } = useOnboarding('learning')

const existingQuestion = reactive({
	question: '',
	marks: 1,
})

const question = reactive({
	question: '',
	type: 'Choices',
	marks: 1,
})

const MAX_OPTIONS = 10

const populateFields = () => {
	let fields = ['option', 'is_correct', 'explanation', 'possibility']
	fields.forEach((field) => {
		for (let counter = 1; counter <= MAX_OPTIONS; counter++) {
			question[`${field}_${counter}`] = field === 'is_correct' ? false : null
		}
	})
}

populateFields()

const props = defineProps({
	title: {
		type: String,
		default: __('Add new question'),
	},
	questionDetail: {
		type: [Object, null],
		required: true,
	},
})

const questionData = createResource({
	url: 'frappe.client.get',
	makeParams() {
		return {
			doctype: 'LMS Question',
			name: props.questionDetail.question,
		}
	},
	auto: false,
	onSuccess(data) {
		editMode.value = true
		Object.keys(data).forEach((key) => {
			if (Object.hasOwn(question, key)) question[key] = data[key]
		})
		for (let counter = 1; counter <= MAX_OPTIONS; counter++) {
			question[`is_correct_${counter}`] = data[`is_correct_${counter}`]
				? true
				: false
		}
		question.marks = props.questionDetail.marks
	},
})

watch(show, () => {
	if (show.value) {
		editMode.value = false
		if (props.questionDetail.question) questionData.fetch()
		else {
			question.question = ''
			question.marks = 1
			question.type = 'Choices'
			existingQuestion.question = ''
			existingQuestion.marks = 1
			chooseFromExisting.value = false
			populateFields()
		}

		if (props.questionDetail.marks) question.marks = props.questionDetail.marks
	}
})

const questionRow = createResource({
	url: 'frappe.client.insert',
	makeParams(values) {
		return {
			doc: {
				doctype: 'LMS Quiz Question',
				parent: quiz.value.doc.name,
				parentfield: 'questions',
				parenttype: 'LMS Quiz',
				...values,
			},
		}
	},
})

const questionCreation = createResource({
	url: 'frappe.client.insert',
	makeParams(values) {
		return {
			doc: {
				doctype: 'LMS Question',
				...question,
			},
		}
	},
})

const submitQuestion = () => {
	if (props.questionDetail?.question) updateQuestion()
	else addQuestion()
}

const addQuestion = () => {
	if (chooseFromExisting.value) {
		addQuestionRow({
			question: existingQuestion.question,
			marks: existingQuestion.marks,
		})
	} else {
		questionCreation.submit(
			{},
			{
				onSuccess(data) {
					addQuestionRow({
						question: data.name,
						marks: question.marks,
					})
				},
				onError(err) {
					toast.error(err.messages?.[0] || err)
				},
			}
		)
	}
}

const addQuestionRow = (question) => {
	questionRow.submit(
		{
			...question,
		},
		{
			onSuccess() {
				if (user.data?.is_system_manager)
					updateOnboardingStep('create_first_quiz')

				show.value = false
				toast.success(__('Question added successfully'))
				quiz.value.reload()
				show.value = false
			},
			onError(err) {
				toast.error(err.messages?.[0] || err)
				show.value = false
			},
		}
	)
}

const questionUpdate = createResource({
	url: 'frappe.client.set_value',
	auto: false,
	makeParams(values) {
		return {
			doctype: 'LMS Question',
			name: questionData.data?.name,
			fieldname: {
				...question,
			},
		}
	},
})

const marksUpdate = createResource({
	url: 'frappe.client.set_value',
	auto: false,
	makeParams(values) {
		return {
			doctype: 'LMS Quiz Question',
			name: props.questionDetail.name,
			fieldname: {
				marks: question.marks,
			},
		}
	},
})

const updateQuestion = () => {
	questionUpdate.submit(
		{},
		{
			onSuccess() {
				marksUpdate.submit(
					{},
					{
						onSuccess() {
							show.value = false
							toast.success(__('Question updated successfully'))
							quiz.value.reload()
						},
					}
				)
			},
			onError(err) {
				toast.error(err.messages?.[0] || err)
			},
		}
	)
}
</script>
<style>
input[type='radio']:checked {
	background-color: theme('colors.gray.900') !important;
	border-color: theme('colors.gray.900') !important;
	--tw-ring-color: theme('colors.gray.900') !important;
}
</style>
