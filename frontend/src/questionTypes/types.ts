import type { Component } from 'vue'

export interface QuestionTypeDef {
	name: string
	label: string
	autoGraded: boolean
	hasLiveCheck: boolean
	/** Initial per-type fields merged into a new question object. */
	defaultConfig(): Record<string, any>
	/** Normalize the learner's current UI state into the answer array the
	 *  backend expects (the same shape today's getAnswers() returns). */
	getAnswers(question: any, state: any): string[]
	/** Given saved answers from localStorage, return the UI state to restore. */
	loadAnswer(question: any, savedAnswers: string[]): any
	AuthorComponent: Component
	PlayerComponent: Component
}
