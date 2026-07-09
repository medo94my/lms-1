# Guided Authoring Flow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make a Course Creator always know the next action and never hit an unguided blank screen — by fixing/widening the onboarding checklist, landing them in the Course editor, and giving empty authoring states one clear CTA.

**Architecture:** Frontend-only Vue changes. Two new pure, unit-tested helpers (`isCourseCreator`, `resolveTabIndex`) become the single source of truth for "who sees onboarding" and "which tab a hash maps to." The rest is surgical wiring + empty-state markup in existing components.

**Tech Stack:** Vue 3 `<script setup>`, frappe-ui, vue-router, Vitest (+ `@vue/test-utils`/jsdom available).

## Global Constraints

- **Frontend-only.** No backend, DocType, or API changes.
- **Single predicate for onboarding gates:** a new pure `isCourseCreator(user)` returning `is_instructor || is_moderator || is_system_manager`. Use it at every onboarding gate. Do NOT modify the existing `canCreateCourse()` (keeps the Create-course button behavior unchanged).
- **i18n / RTL:** wrap every new user-facing string in `__()`; use logical spacing (`ps-`/`pe-`/`ms-`/`me-`, never hardcoded left/right) so RTL holds.
- **Brand styling:** reuse existing frappe-ui `Button` and the project's ink/surface theme tokens; no new color literals.
- **Surgical:** touch only the files named in each task. Do not redesign the editor, the course form, or the quiz builder. Preserve the `useOnboarding('learning')` mechanism and any currently-working deep-links (label-match fallback).
- **Lint/format:** Prettier (es5) + ESLint run via the format-on-edit hook — let it format; don't hand-fight it.
- **Testing reality:** pure helpers get full TDD unit tests (Tasks 1–2). The host components touched in Tasks 3–4 (`CourseEditor`, `LessonForm`, `AppSidebar`, `CourseDetail`, `ChapterRow`) pull in resources/router/EditorJS/headless-ui and are not unit-mounted; verify those by keeping the full Vitest suite green (`cd frontend && npx vitest run`) plus the manual checklist at the end.

---

## Task 1: `isCourseCreator` helper + widen onboarding to course creators

**Files:**
- Create: `frontend/src/utils/roles.ts`
- Test: `frontend/src/tests/roles.test.ts`
- Modify: `frontend/src/components/Sidebar/AppSidebar.vue` (`setUpOnboarding`, ~line 644)
- Modify: `frontend/src/pages/Courses/NewCourseModal.vue` (onboarding gate, ~line 326)
- Modify: `frontend/src/components/Modals/ChapterModal.vue` (~line 141)
- Modify: `frontend/src/pages/LessonForm.vue` (~line 596)
- Modify: `frontend/src/components/Modals/Question.vue` (~line 233)

**Interfaces:**
- Produces: `isCourseCreator(user): boolean` from `@/utils/roles`. `user` is a user-data object (or null/undefined). True iff `is_instructor || is_moderator || is_system_manager`.

- [ ] **Step 1: Write the failing helper test**

Create `frontend/src/tests/roles.test.ts`:

```ts
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
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `cd frontend && npx vitest run src/tests/roles.test.ts`
Expected: FAIL — `@/utils/roles` does not exist yet.

- [ ] **Step 3: Create the helper**

Create `frontend/src/utils/roles.ts`:

```ts
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
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `cd frontend && npx vitest run src/tests/roles.test.ts`
Expected: PASS.

- [ ] **Step 5: Widen the onboarding setup gate in `AppSidebar.vue`**

Add the import near the other `@/utils` imports at the top of `<script setup>`:

```js
import { isCourseCreator } from '@/utils/roles'
```

In `setUpOnboarding()` (~line 644) change the guard:

```js
const setUpOnboarding = () => {
	if (isCourseCreator(userResource.data)) {
		onboardingDetails = useOnboarding('learning')
		onboardingDetails.setUp(steps)
		isOnboardingStepsCompleted = onboardingDetails.isOnboardingStepsCompleted
		showOnboarding.value = true
	}
}
```

- [ ] **Step 6: Widen the four step-completion gates**

In each file, add `import { isCourseCreator } from '@/utils/roles'` (next to existing imports) and change the `if (user.data?.is_system_manager)` guard that wraps `updateOnboardingStep(...)` to `if (isCourseCreator(user.data))`.

`frontend/src/pages/Courses/NewCourseModal.vue` (~line 326), inside `onSuccess`:

```ts
if (isCourseCreator(user.data)) {
	updateOnboardingStep('create_first_course', true, false, () => {
		localStorage.setItem('firstCourse', data.name)
	})
}
```

`frontend/src/components/Modals/ChapterModal.vue` (~line 141):

```js
if (isCourseCreator(user.data)) updateOnboardingStep('create_first_chapter')
```

`frontend/src/pages/LessonForm.vue` (~line 596):

```js
if (isCourseCreator(user.data)) updateOnboardingStep('create_first_lesson')
```

`frontend/src/components/Modals/Question.vue` (~line 233):

```js
if (isCourseCreator(user.data)) updateOnboardingStep('create_first_quiz')
```

- [ ] **Step 7: Run the full suite to confirm nothing broke**

Run: `cd frontend && npx vitest run`
Expected: PASS (all files), including the new `roles.test.ts`.

- [ ] **Step 8: Commit**

```bash
git add frontend/src/utils/roles.ts frontend/src/tests/roles.test.ts \
  frontend/src/components/Sidebar/AppSidebar.vue \
  frontend/src/pages/Courses/NewCourseModal.vue \
  frontend/src/components/Modals/ChapterModal.vue \
  frontend/src/pages/LessonForm.vue \
  frontend/src/components/Modals/Question.vue
git commit -m "feat(authoring): show onboarding to all course creators"
```

---

## Task 2: Stable editor-tab key + land deep-links on the Course editor

**Files:**
- Create: `frontend/src/utils/courseTabs.ts`
- Test: `frontend/src/tests/courseTabs.test.ts`
- Modify: `frontend/src/pages/Courses/CourseDetail.vue` (tabs array ~305-326; `updateTabIndex` ~273-282; `watch(tabIndex)` ~284-290)
- Modify: `frontend/src/components/Sidebar/AppSidebar.vue` (`create_first_chapter` + `create_first_lesson` step `onClick`)
- Modify: `frontend/src/pages/Courses/NewCourseModal.vue` (post-create `router.push` hash)
- Modify: `frontend/src/pages/Courses/CourseEditor.vue` (three `'#course editor'` fallbacks)

**Interfaces:**
- Consumes: nothing from Task 1 (independent), though it re-touches `AppSidebar.vue`/`NewCourseModal.vue` — keep the Task 1 edits intact, only add the hash changes described here.
- Produces: `resolveTabIndex(tabs, hash): number` from `@/utils/courseTabs`. Tabs gain a stable `key`: `'overview' | 'dashboard' | 'editor' | 'settings'`. The editor tab's canonical hash is `#editor`.

- [ ] **Step 1: Write the failing resolver test**

Create `frontend/src/tests/courseTabs.test.ts`:

```ts
import { describe, it, expect } from 'vitest'
import { resolveTabIndex } from '@/utils/courseTabs'

const tabs = [
	{ key: 'overview', label: 'Overview' },
	{ key: 'dashboard', label: 'Dashboard' },
	{ key: 'editor', label: 'Course editor' },
	{ key: 'settings', label: 'Settings' },
]

describe('resolveTabIndex', () => {
	it('matches by stable key', () => {
		expect(resolveTabIndex(tabs, '#editor')).toBe(2)
		expect(resolveTabIndex(tabs, '#settings')).toBe(3)
	})
	it('falls back to the lowercased label for legacy hashes', () => {
		expect(resolveTabIndex(tabs, '#course editor')).toBe(2)
		expect(resolveTabIndex(tabs, '#overview')).toBe(0)
	})
	it('returns 0 for an unknown or empty hash', () => {
		expect(resolveTabIndex(tabs, '')).toBe(0)
		expect(resolveTabIndex(tabs, '#nope')).toBe(0)
	})
})
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `cd frontend && npx vitest run src/tests/courseTabs.test.ts`
Expected: FAIL — `@/utils/courseTabs` does not exist yet.

- [ ] **Step 3: Create the resolver**

Create `frontend/src/utils/courseTabs.ts`:

```ts
export interface TabLike {
	key?: string
	label?: string
}

/** Resolve a route hash (e.g. '#editor', or a legacy '#course editor') to a tab
 *  index. Match by stable key first, then fall back to the lowercased label so
 *  bookmarked label-based hashes keep working. Returns 0 when unmatched. */
export function resolveTabIndex(tabs: TabLike[], hash: string): number {
	const target = (hash || '').replace(/^#/, '').toLowerCase()
	if (!target) return 0
	const byKey = tabs.findIndex((t) => t.key === target)
	if (byKey !== -1) return byKey
	const byLabel = tabs.findIndex((t) => (t.label || '').toLowerCase() === target)
	return byLabel === -1 ? 0 : byLabel
}
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `cd frontend && npx vitest run src/tests/courseTabs.test.ts`
Expected: PASS.

- [ ] **Step 5: Add stable keys + use the resolver in `CourseDetail.vue`**

Add the import near the other `@/` imports:

```ts
import { resolveTabIndex } from '@/utils/courseTabs'
```

Give each tab a `key` (add a local type so TS accepts the extra field). Replace the `tabs` definition (~305-326):

```ts
type EditorTab = TabDef & { key: string }
const tabs = ref<EditorTab[]>([
	{
		key: 'overview',
		label: __('Overview'),
		component: markRaw(CourseOverview),
		icon: 'lucide-list',
	},
	{
		key: 'dashboard',
		label: __('Dashboard'),
		component: markRaw(CourseDashboard),
		icon: 'lucide-trending-up',
	},
	{
		key: 'editor',
		label: __('Course editor'),
		component: markRaw(CourseEditor),
		icon: 'lucide-book-open',
	},
	{
		key: 'settings',
		label: __('Settings'),
		component: markRaw(CourseForm),
		icon: 'lucide-settings-2',
	},
])
```

Replace `updateTabIndex` (~273-282) so it resolves by key (with label fallback), preserving "no hash → leave the current tab":

```ts
const updateTabIndex = () => {
	if (!route.hash) return
	tabIndex.value = resolveTabIndex(tabs.value, route.hash)
}
```

Replace the `watch(tabIndex, …)` writeback (~284-290) so it writes the stable key and treats a legacy label hash as already-correct (no redundant push):

```ts
watch(tabIndex, () => {
	const tab = tabs.value[tabIndex.value]
	const current = route.hash.replace('#', '')
	if (tab.key !== current && tab.label?.toLowerCase() !== current) {
		router.push({ ...route, hash: `#${tab.key}` })
	}
})
```

- [ ] **Step 6: Point the onboarding chapter/lesson steps at the editor tab**

In `frontend/src/components/Sidebar/AppSidebar.vue`, in BOTH the `create_first_chapter` and `create_first_lesson` step objects' `onClick`, change the course branch's `hash: '#settings'` to `hash: '#editor'`. (These are the only two `hash: '#settings'` occurrences in this file.) Each block reads:

```js
router.push({
	name: 'CourseDetail',
	params: { courseName: course },
	hash: '#editor',
})
```

- [ ] **Step 7: Land on the editor tab after creating a course**

In `frontend/src/pages/Courses/NewCourseModal.vue`, in the create `onSuccess` (~line 319), change the post-create push hash from `'#settings'` to `'#editor'`:

```ts
router.push({
	name: 'CourseDetail',
	params: { courseName: data.name },
	hash: '#editor',
})
```

- [ ] **Step 8: Make editor-internal route writes use the stable key**

In `frontend/src/pages/Courses/CourseEditor.vue`, replace all three `'#course editor'` fallbacks (in `syncSelectedToUrl` ~131, `syncModeToUrl` ~140, the stale-selection watcher ~292) with `'#editor'`. Each is of the form `hash: route.hash || '#editor'`.

- [ ] **Step 9: Run the full suite**

Run: `cd frontend && npx vitest run`
Expected: PASS (all files), including `courseTabs.test.ts`.

- [ ] **Step 10: Commit**

```bash
git add frontend/src/utils/courseTabs.ts frontend/src/tests/courseTabs.test.ts \
  frontend/src/pages/Courses/CourseDetail.vue \
  frontend/src/components/Sidebar/AppSidebar.vue \
  frontend/src/pages/Courses/NewCourseModal.vue \
  frontend/src/pages/Courses/CourseEditor.vue
git commit -m "feat(authoring): land authoring deep-links on the Course editor tab"
```

---

## Task 3: Empty-state CTAs (course editor pane + empty chapter)

**Files:**
- Modify: `frontend/src/pages/Courses/CourseEditor.vue` (left-pane empty block ~9-17; `Button` import ~82; add `hasChapters` computed)
- Modify: `frontend/src/components/ChapterRow.vue` (after `</Draggable>`, before the Add-Lesson `<div>`)

**Interfaces:**
- Consumes: `openAddChapter()` already exposed by `CourseEditor.vue` (calls `courseOutlineRef.openChapterModal(null)`); `outline.data` is the chapters array. Keep the Task 2 edits to this file intact.
- Produces: nothing for later tasks.

- [ ] **Step 1: Add a `hasChapters` computed in `CourseEditor.vue`**

Near the other computeds in `<script setup>` (e.g. after the `outline` resource block), add:

```js
const hasChapters = computed(() => (outline.data?.length ?? 0) > 0)
```

`computed` is already imported (line 80).

- [ ] **Step 2: Import `Button` in `CourseEditor.vue`**

Change the frappe-ui import (line ~82) from:

```js
import { createResource } from 'frappe-ui'
```

to:

```js
import { createResource, Button } from 'frappe-ui'
```

- [ ] **Step 3: Make the left-pane empty state context-aware**

Replace the `v-else-if="!selected"` block (~9-17) with one that offers a "Create chapter" CTA when the course has no chapters, and the "select a lesson" hint otherwise:

```html
<div
	v-else-if="!selected"
	class="flex flex-col items-center justify-center h-full gap-2 text-ink-gray-5"
>
	<span class="lucide-book-open size-8" />
	<template v-if="hasChapters">
		<div>{{ __('Select a lesson on the right to start editing.') }}</div>
	</template>
	<template v-else>
		<div>{{ __('Add a chapter to begin building your course.') }}</div>
		<Button variant="solid" @click="openAddChapter">
			<template #prefix><span class="lucide-plus size-4" /></template>
			{{ __('Create chapter') }}
		</Button>
	</template>
</div>
```

- [ ] **Step 4: Add an empty-lessons hint in `ChapterRow.vue`**

Between the `</Draggable>` close tag and the `<div v-if="allowEdit" class="flex mt-2 mb-4 ps-8">` Add-Lesson block, insert:

```html
<div
	v-if="allowEdit && !chapter.lessons?.length"
	class="ps-8 pt-2 text-sm text-ink-gray-5"
>
	{{ __('No lessons yet — add your first one below.') }}
</div>
```

- [ ] **Step 5: Run the full suite (no regressions)**

Run: `cd frontend && npx vitest run`
Expected: PASS (all files). No new unit test here — these are template-only changes on resource/headless-ui-heavy components, verified by the suite staying green plus the manual checklist.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/pages/Courses/CourseEditor.vue frontend/src/components/ChapterRow.vue
git commit -m "feat(authoring): clear CTAs for empty course and chapter states"
```

---

## Task 4: Lesson empty-body nudge + discoverable help

**Files:**
- Modify: `frontend/src/pages/LessonForm.vue` (content editor template ~67; add `bodyIsEmpty` computed near `storedContentHasBody` ~485)
- Modify: `frontend/src/pages/Courses/CourseDetail.vue` (lesson-help `Button` ~53)

**Interfaces:**
- Consumes: `storedContentHasBody()` (already defined in `LessonForm.vue` ~477, returns whether the stored lesson body has real content); `showLessonHelp` ref already drives `LessonHelp` in `CourseDetail.vue`. Keep the Task 2 edits to `CourseDetail.vue` intact.

- [ ] **Step 1: Add a `bodyIsEmpty` computed in `LessonForm.vue`**

Immediately after the `storedContentHasBody` definition (~line 485), add:

```js
// Drives the empty-body nudge. Reacts to lesson.content, which updates on load
// and on autosave, so the hint shows for a fresh/empty lesson and clears once
// the body has saved content. The full insert-menu redesign is sub-project 2.
const bodyIsEmpty = computed(() => !storedContentHasBody())
```

`computed` is already imported (line ~230).

- [ ] **Step 2: Show the nudge above the content editor**

In the template, replace the content-editor block (~67-72):

```html
			<!-- Lesson content -->
			<BlockEditor
				ref="editor"
				:uploadContext="contentUploadContext"
				@change="markDirty"
			/>
```

with:

```html
			<!-- Lesson content -->
			<p v-if="bodyIsEmpty" class="mb-2 text-p-sm text-ink-gray-5">
				{{
					__('Start typing, or use the + button to add a video, image, or quiz.')
				}}
			</p>
			<BlockEditor
				ref="editor"
				:uploadContext="contentUploadContext"
				@change="markDirty"
			/>
```

- [ ] **Step 3: Make the "How to edit a lesson" help button visible**

In `frontend/src/pages/Courses/CourseDetail.vue` (~line 53), give the help button a visible label instead of an icon-only ghost button:

```html
					<Button variant="ghost" @click="showLessonHelp = true">
						<template #prefix>
							<span class="lucide-info size-4" />
						</template>
						{{ __('Help') }}
					</Button>
```

(Leave the surrounding `Tooltip` as-is.)

- [ ] **Step 4: Run the full suite (no regressions)**

Run: `cd frontend && npx vitest run`
Expected: PASS (all files). Template-only changes on EditorJS/resource-heavy components — verified by the suite staying green plus the manual checklist.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/pages/LessonForm.vue frontend/src/pages/Courses/CourseDetail.vue
git commit -m "feat(authoring): nudge on empty lesson body + visible lesson help"
```

---

## Manual verification (after all tasks, in the preview)

Sign in as a **Course Creator** (instructor, NOT a system manager):

1. The sidebar onboarding checklist ("Create your first course → … → quiz") is visible.
2. Click "Add your first chapter" → lands on the **Course editor** tab (not Settings).
3. Create a new course → lands on the **Course editor** tab; with no chapters the left pane shows "Add a chapter to begin…" with a working **Create chapter** button.
4. Expand a chapter with no lessons → "No lessons yet — add your first one below." appears above the **Add Lesson** button.
5. Open a fresh lesson → the empty body shows the "Start typing, or use the + button…" nudge, which disappears after content is added and saved; the **Help** button in the editor header is clearly labeled and opens the help modal.
6. Complete each step → the corresponding checklist item ticks (proves the widened completion gates).
7. As a **system manager**, the checklist still appears (no regression). Legacy bookmark `#settings` still opens Settings; `#course editor` still opens the editor (label fallback).
8. RTL/Arabic: the editor-tab deep-link still resolves and the new CTAs/nudges read correctly with logical spacing.

---

## Self-Review

**Spec coverage:**
- §A stable editor-tab key + label fallback → Task 2 (Steps 1–5, 8). ✓
- §B.1 widen onboarding visibility (`isCourseCreator` in `setUpOnboarding`) → Task 1 Step 5. ✓
- §B.2 widen the four step-completion gates → Task 1 Step 6. ✓
- §B.3 fix chapter/lesson step deep-links to `#editor` → Task 2 Step 6. ✓
- §C post-create landing on the editor → Task 2 Step 7. ✓
- §D empty-state CTAs (editor left pane context-aware; empty chapter hint; CourseOutline left as-is) → Task 3. ✓
- §E lesson empty-body nudge + visible help → Task 4. ✓
- `isCourseCreator` single source of truth, `canCreateCourse` untouched → Task 1 (Global Constraints). ✓
- CourseEditor's 3 hardcoded `#course editor` writes updated → Task 2 Step 8. ✓

**Placeholder scan:** none — every code step shows the exact code; every run step shows the command + expected result.

**Type/name consistency:** `isCourseCreator(user)` used identically across all five gates (Task 1). `resolveTabIndex(tabs, hash)` and the tab `key` values (`overview`/`dashboard`/`editor`/`settings`) match between the helper, its test, and `CourseDetail.vue` (Task 2). `hasChapters`/`openAddChapter`/`outline.data` (Task 3) and `bodyIsEmpty`/`storedContentHasBody`/`showLessonHelp` (Task 4) all reference existing or same-task bindings. Shared-file re-touches (`AppSidebar.vue`, `NewCourseModal.vue` in Tasks 1&2; `CourseDetail.vue` in Tasks 2&4; `CourseEditor.vue` in Tasks 2&3) are called out in each task's Interfaces so earlier edits are preserved.
