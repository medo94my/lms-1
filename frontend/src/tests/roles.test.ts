import { describe, it, expect } from 'vitest'
import { isCourseCreator } from '@/utils/roles'

describe('isCourseCreator', () => {
	it('is true for instructor, moderator, or system manager', () => {
		expect(isCourseCreator({ is_instructor: true })).toBe(true)
		expect(isCourseCreator({ is_moderator: true })).toBe(true)
		expect(isCourseCreator({ is_system_manager: true })).toBe(true)
		expect(isCourseCreator({ is_instructor: 1 })).toBe(true)
	})
	it('is false for a plain student and for a missing user', () => {
		expect(isCourseCreator({ is_student: true })).toBe(false)
		expect(isCourseCreator({})).toBe(false)
		expect(isCourseCreator(null)).toBe(false)
		expect(isCourseCreator(undefined)).toBe(false)
	})
})
