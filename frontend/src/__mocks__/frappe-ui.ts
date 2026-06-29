/**
 * Minimal frappe-ui stub for Vitest.
 *
 * frappe-ui's src/resources/documentResource.js uses extensionless ESM
 * imports (import './resources') which fail under Node's strict ESM
 * resolution. Tests that explicitly call vi.mock('frappe-ui', factory) are
 * unaffected — vi.mock intercepts before module resolution. This stub is used
 * only by tests that import frappe-ui transitively without mocking it.
 */
import { defineComponent, h } from 'vue'

const PassThrough = defineComponent({
	name: 'FrappeUIStub',
	setup(_props, { slots }) {
		return () => h('div', slots.default?.())
	},
})

export const FormControl = PassThrough
export const Button = PassThrough
export const Dialog = PassThrough
export const TextEditor = PassThrough
export const Badge = PassThrough
export const Input = PassThrough
export const Autocomplete = PassThrough
export const Dropdown = PassThrough
export const Avatar = PassThrough
export const Tabs = PassThrough
export const Alert = PassThrough
export const Tooltip = PassThrough
export const Spinner = PassThrough
export const toast = { success: () => {}, error: () => {}, warning: () => {} }
export const createResource = () => ({
	data: null,
	loading: false,
	fetch: () => {},
	submit: () => {},
	reload: () => {},
})
export const createListResource = () => ({
	data: [],
	loading: false,
	fetch: () => {},
	reload: () => {},
})
export const createDocumentResource = () => ({
	doc: null,
	loading: false,
	fetch: () => {},
	reload: () => {},
})
export const setConfig = () => {}
export const frappeRequest = () => Promise.resolve()
export const useOnboarding = () => ({ updateOnboardingStep: () => {} })
