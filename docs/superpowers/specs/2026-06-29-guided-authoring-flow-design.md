# Guided Authoring Flow ("Never a Blank Screen") — Design

**Date:** 2026-06-29
**Base branch:** basiret-redesign (question-type initiative complete; secure player config merged, commit ecef7e26)
**Status:** Approved (design); implementation plan to follow

## Context

This is **sub-project 1 of the "dummy-proof authoring UX" initiative**. The
initiative was decomposed (with the user) into ordered slices:

1. **Guided authoring flow — "never a blank screen"** ← THIS SPEC
2. Lesson content editor (the EditorJS insert-menu redesign)
3. In-context quiz creation (kill the new-tab detour)
4. Lighter course creation + creator home

The authoring journey today is **Course → Outline (chapters/lessons) → Lesson
content → Quiz**, wrapped by an onboarding/guidance layer. A creator-journey map
(see commit history / brainstorm) found the friction clusters in this slice:

- **No "what next" / blank screens.** After creating a course the creator lands
  on the *Settings* tab, not the editor; the course editor can show two empty
  panes; the lesson editor is a blank white rectangle.
- **The onboarding checklist is effectively dead here and partly wrong.** Its
  render gate is `is_system_manager && is_fc_site`
  (`frontend/src/components/Sidebar/AppSidebar.vue:148`). `is_fc_site` means a
  Frappe-Cloud-hosted site; this LMS runs on Docker, so the gate is false and
  **the onboarding widget never renders on this deployment**. Two of its steps
  also deep-link to the wrong tab.

## Goal & scope

Make a Course Creator always know the next action and never hit an unguided
blank screen, by fixing the existing onboarding checklist, landing the creator
in the right place after creating a course, and giving every empty authoring
state one obvious primary CTA.

**In scope (frontend-only):** Vue routing, render-gate changes, empty-state
CTAs, and a non-invasive lesson-editor placeholder.

**Out of scope (later sub-projects / explicitly deferred):**
- Redesigning the EditorJS insert menu / block picker (sub-project 2).
- In-context quiz creation (sub-project 3).
- Lighter course-creation form and a creator dashboard/home (sub-project 4).
- Any backend change. Onboarding completion tracking
  (`useOnboarding('learning')`) and its `dependsOn` gating stay as-is.

## Ground truth (current wiring this spec touches)

- **Onboarding widget gate:** `frontend/src/components/Sidebar/AppSidebar.vue`
  — `showOnboarding` is computed at ~line 148 as
  `userResource.data?.is_system_manager && userResource.data?.is_fc_site`.
  The role flags available on `userResource.data` include `is_system_manager`,
  `is_moderator`, `is_instructor` (set at ~lines 644–656).
- **Onboarding steps:** same file, `steps` reactive array (~lines 446–508).
  `create_first_chapter` and `create_first_lesson` push
  `{ name: 'CourseDetail', params: { courseName }, hash: '#settings' }` — the
  wrong tab. `create_first_course` (→ `Courses`) and `create_first_quiz`
  (→ `Quizzes`) are already correct.
- **Course detail tabs:** `frontend/src/pages/Courses/CourseDetail.vue` — `tabs`
  array (~lines 305–326) in order: `Overview` (0), `Dashboard` (1),
  `Course editor` (2), `Settings` (3). The hash↔tab sync (~lines 274–292)
  matches `tab.label.toLowerCase()` against `route.hash` (so the Course-editor
  tab's hash is `#course editor`). Labels are passed through `__()`, so the hash
  is locale-dependent — see "Deep-link mechanism" below.
- **Post-create routing:** `frontend/src/pages/Courses/NewCourseModal.vue`
  (~lines 319–322) pushes `{ name: 'CourseDetail', params: { courseName },
  hash: '#settings' }` after a successful create.
- **Course editor panes:** `frontend/src/pages/Courses/CourseEditor.vue` — left
  pane shows "Select a lesson on the right to start editing" when nothing is
  selected; right pane is `frontend/src/components/CourseOutline.vue`, which
  already has a centered "Create chapter" empty state when there are no
  chapters.
- **Lesson editor:** `frontend/src/pages/LessonForm.vue` + the main
  `frontend/src/components/BlockEditor.vue`. The lesson body opens blank.

## Design

### A. Deep-link mechanism (shared decision)

The existing tab deep-linking matches a `#hash` against the **translated**
lowercased tab label, which is fragile (the hash for the editor tab is
`#course editor`, and would differ under RTL/Arabic). Rather than hard-code a
translated hash string in multiple places, add a **single stable tab key** the
deep-links can target.

**Approach:** in `CourseDetail.vue`, give each tab a locale-independent `key`
(e.g. `'overview' | 'dashboard' | 'editor' | 'settings'`) and resolve the
incoming `route.hash` against `tab.key` (falling back to the existing
label-match for backward compatibility with any bookmarked `#settings` links).
Deep-links elsewhere then push `hash: '#editor'`. This keeps one source of truth
for the editor tab's hash and removes the locale fragility for the new links.

*(If, during planning, the existing label-based hash proves load-bearing for
other links, the fallback match preserves them — no existing deep-link breaks.)*

### B. Sidebar onboarding checklist — visibility + correctness

`AppSidebar.vue`:

1. **Widen the gate.** Replace `showOnboarding`'s
   `is_system_manager && is_fc_site` condition with
   `is_instructor || is_moderator || is_system_manager` (a Course Creator is
   `is_instructor`; `is_moderator`/`is_system_manager` are kept so the original
   audience never regresses). Drop the `is_fc_site` restriction so the checklist
   renders on this (Docker) deployment. The existing `!isOnboardingStepsCompleted`
   condition still hides it once the creator finishes, so it does not nag forever.
2. **Fix the deep-links.** Change `create_first_chapter` and
   `create_first_lesson` `onClick` to push the **Course editor** tab
   (`hash: '#editor'` per §A) instead of `#settings`. Keep their `getFirstCourse`
   lookup and the `dependsOn` ordering unchanged.

No change to step definitions, completion tracking, or the help modal.

### C. Post-create landing

`NewCourseModal.vue`: after a successful create, route to the **Course editor**
tab (`hash: '#editor'`) instead of `#settings`, so the creator immediately sees
the outline and its "Create chapter" CTA rather than a settings form.

### D. Empty-state CTAs (one obvious next action each)

The principle: every authoring screen that can be empty shows exactly one
**primary** CTA plus a one-line "what this is," using existing brand button/
empty-state styles.

1. **Course editor, no chapter selected / none exist.** `CourseEditor.vue` left
   pane currently says "Select a lesson on the right to start editing" even when
   there are zero chapters (so the right pane is also empty — two empty panes).
   Make the left-pane empty message context-aware: when the course has **no
   chapters**, show "Add a chapter to begin" pointing at the outline's existing
   "Create chapter" CTA; when chapters exist but no lesson is selected, keep
   "Select a lesson…". The right-pane `CourseOutline` "Create chapter" empty
   state stays as the single primary action.
2. **Chapter with no lessons.** The existing per-chapter "Add Lesson" button is
   the primary affordance; ensure an empty chapter makes it obviously the next
   step (e.g. a short "No lessons yet — add one" line above it) rather than an
   empty expanded row.
3. **Audit pass.** Review the course/chapter/lesson-list empty states for a
   single clear primary CTA + one-line description; align wording and ensure no
   screen in the chapter→lesson path is blank with no action. Quiz empty states
   are already good ("No questions added yet…") and are out of this slice's
   editing path — leave them.

### E. Lesson-editor light nudge (non-invasive)

When the lesson body is empty, show a placeholder hint **around** the editor
(not inside EditorJS) — e.g. *"Start typing, or use **+** to add a video, image,
or quiz."* Implementation stays non-invasive: a conditional element in
`LessonForm.vue` keyed off "body has no real content" (the file already computes
whether the stored body has real content — reuse that), shown until the creator
adds anything. Also surface the existing "How to edit a lesson" help control
more visibly (it lives in the lesson header today and is easy to miss). The real
insert-menu redesign remains sub-project 2; this is only a placeholder + help
affordance.

## Components / units

| Unit | File | Responsibility / change |
|---|---|---|
| Onboarding gate + steps | `AppSidebar.vue` | widen `showOnboarding`; fix two step deep-links to `#editor` |
| Tab key + hash resolve | `CourseDetail.vue` | add stable `key` per tab; resolve hash by key with label fallback |
| Post-create landing | `NewCourseModal.vue` | route to `#editor` after create |
| Editor empty pane | `CourseEditor.vue` | context-aware left-pane empty message |
| Outline / chapter empty states | `CourseOutline.vue`, `ChapterRow.vue` | one clear primary CTA per empty state |
| Lesson empty nudge | `LessonForm.vue` | non-invasive empty-body placeholder + visible help |

Each unit is independently testable and has a single responsibility; none
depends on a new abstraction.

## Data flow

No new data or backend calls. The flow is navigational: role flags on
`userResource.data` decide whether the checklist renders; the checklist and
`NewCourseModal` push routes that land the creator on the Course-editor tab;
empty-state components render CTAs based on already-loaded resource data
(chapters/lessons/body content). Onboarding completion continues to be marked by
the existing `useOnboarding('learning')` calls at create-course / create-chapter
/ create-lesson / create-quiz time (unchanged).

## Testing / success criteria

- **Vitest (unit, where logic is isolable):**
  - The onboarding `showOnboarding` predicate returns true for an instructor,
    a moderator, and a system manager, and false for a plain student —
    independent of `is_fc_site`.
  - `create_first_chapter` / `create_first_lesson` step targets resolve to the
    Course-editor tab key (`'editor'`/`#editor`), not `#settings`.
  - `CourseDetail` hash↔tab resolution maps `#editor` to the Course-editor tab,
    and still maps a legacy `#settings` to Settings (fallback).
  - Empty-state components render their primary CTA under the empty condition
    and hide it when populated.
- **Manual preview (preview deploy):** as a Course Creator (instructor, not
  system manager) — the sidebar checklist appears; clicking "Add your first
  chapter" lands on the Course editor; creating a course lands on the Course
  editor; an empty course/chapter/lesson each shows one clear next action; an
  empty lesson body shows the placeholder nudge. RTL/Arabic: layout and the
  editor-tab deep-link still work.

## Constraints

- **Frontend-only**; no backend or DocType changes.
- **i18n/RTL:** wrap all new user-facing strings in `__()`; use logical spacing
  (no hardcoded left/right) so RTL holds — per project rules.
- **Brand styling:** reuse existing brand button/empty-state components and
  theme tokens; no new color literals.
- **Surgical:** touch only the files in the units table; do not redesign the
  editor, the course form, or the quiz builder. Preserve existing onboarding
  completion tracking and any currently-working deep-links (label-match
  fallback).
- **Lint/format:** Prettier (es5) + ESLint via the format-on-edit hook; Vitest
  for unit tests.

## Non-goals / deferred

- EditorJS insert-menu / block-picker redesign → sub-project 2.
- In-context quiz creation → sub-project 3.
- Lighter course-creation form, creator dashboard/home → sub-project 4.
- Self-service "become a creator" flow and the `LessonForm` "redirect to
  /login when logged-in-but-not-instructor" papercut → out of scope (note for a
  later cleanup).
- Transient "step complete → next step" toasts — not needed; the landing fixes +
  always-on empty-state CTAs + the sidebar checklist cover the guidance.
