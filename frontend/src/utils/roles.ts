type RoleFlag = boolean | number | undefined
interface RoleUser {
	is_instructor?: RoleFlag
	is_moderator?: RoleFlag
	is_system_manager?: RoleFlag
}

/** Roles allowed to author courses — and therefore see the creation onboarding.
 *  `is_system_manager` is included so the original onboarding audience (system
 *  managers) never regresses. Pure and dependency-free so it stays unit-testable. */
export function isCourseCreator(user: RoleUser | null | undefined): boolean {
	return Boolean(
		user?.is_instructor || user?.is_moderator || user?.is_system_manager
	)
}
