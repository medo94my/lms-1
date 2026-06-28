> **Status — target design spec (roadmap), not current-state.** As of 2026-06, the
> app is the upstream Frappe LMS Vue SPA **recolored via frappe-ui token overrides**
> (`frontend/src/styles/basiret-theme.css`, `frontend/tailwind.config.js`). The
> bespoke marketing site, custom components, footer, auth pages, and homepage
> sections described below are largely **not yet built**. Section tags —
> `[IMPLEMENTED]` / `[PARTIAL]` / `[TARGET — not built]` — mark what is live today vs.
> aspirational; `> **Current:**` notes flag where this spec differs from the running
> app. The design vision here is preserved as the roadmap.

# product.md

# Basiret Vakfi LMS

## Product Specification

### UI/UX Modernization for Frappe LMS

Version: 1.0

---

# Objective  [IMPLEMENTED]

Transform the default Frappe LMS interface into a premium modern Islamic educational platform while preserving all existing Frappe functionality.

This project is primarily a **UI/UX redesign**, not a rewrite of the backend.

The objective is to:

* Keep Frappe ERP/LMS architecture
* Keep DocTypes
* Keep Permissions
* Keep APIs
* Keep Workflows

Only modernize:

* UI
* UX
* Navigation
* Layout
* Components
* Theme
* Branding

---

# Design Goals  [TARGET — not built]

The interface should feel like:

* Coursera
* Notion
* Linear
* Frappe CRM
* Apple Education
* Modern SaaS

combined with

* Islamic elegance
* Arabic RTL
* Educational trust
* Clean whitespace
* Premium branding

---

# Design Principles  [PARTIAL]

## Simplicity

Remove unnecessary visual noise.

Never overload pages.

Everything should have breathing space.

---

## Consistency

Every page must use the Design System.

Spacing

Typography

Radius

Buttons

Colors

Cards

Forms

must all come from the design tokens.

---

## Accessibility

Minimum AA contrast.

Keyboard navigation.

Visible focus states.

Responsive.

RTL support.

---

# Technical Constraints  [IMPLEMENTED]

The following MUST NOT be modified:

Database schema

DocTypes

Permissions

Business Logic

Workflows

Server APIs

Role System

Authentication

Instead:

Override templates

Override CSS

Override JS components

Extend Frappe pages

Use hooks

Use custom app

---

# Branding  [PARTIAL]

> **Current:** The green/gold theme is applied globally via tokens. Logo, branded
> emails, certificates, and PDFs are not yet rebranded.

Apply Basiret Vakfi branding globally.

Logo

Typography

Green theme

Gold accents

Icons

Footer

Header

Course cards

Dashboard

Authentication pages

Emails

Certificates

PDFs

Student portal

---

# Theme  [IMPLEMENTED]

Implement a global theme.

Replace default Frappe colors.

Use CSS variables from color-tokens.md.

Every component should inherit tokens.

Do NOT hardcode colors.

---

# Navigation  [PARTIAL]

> **Current:** Navigation is the frappe-ui left sidebar, recolored deep-green; there
> is no rebuilt top navbar or language switcher.

Replace default navigation.

Desktop

---

Logo

Main navigation

Search

Notifications

Profile

Language switcher

Login/Register

---

Mobile

Hamburger

Logo

Search

Profile

Bottom navigation (optional)

---

# Homepage  [TARGET — not built]

> **Current:** No marketing homepage; `/` redirects guests to `/courses` and shows a
> dashboard for logged-in users.

Replace default LMS homepage.

Sections:

Hero

Statistics

Features

Featured Courses

Teachers

Programs

Testimonials

Latest Articles

Donation CTA

Footer

All sections should be CMS editable.

---

# Dashboard  [PARTIAL]

Modernize student dashboard.

Widgets:

Continue Learning

My Courses

Certificates

Upcoming Lessons

Recent Activity

Bookmarks

Progress

Announcements

Calendar

Quick Actions

---

# Course Listing  [PARTIAL]

Replace grid.

Each card contains:

Thumbnail

Category

Difficulty

Duration

Rating

Teacher

Enrollment count

Progress

Bookmark button

Hover animation

---

# Course Detail  [PARTIAL]

Sections

Hero

Instructor

Curriculum

Lessons

Resources

Discussion

Reviews

Certificate

Related Courses

Sticky sidebar

Enroll button

Progress

Estimated completion

---

# Lesson Player  [IMPLEMENTED]

> **Current:** Implemented via native frappe-ui LMS (sidebar, notes, discussion,
> video/PDF/quiz blocks, mark-complete).

Split layout.

Sidebar

Lesson content

Resources

Notes

Discussion

Next lesson

Previous lesson

Progress

Mark complete

Fullscreen

Video support

PDF support

Quiz support

---

# Dashboard Sidebar  [PARTIAL]

Modernize.

Icons

Rounded

Collapsible

Animated

Dark/light ready

---

# Forms  [PARTIAL]

Replace all forms.

Rounded inputs.

Modern validation.

Floating labels optional.

Better spacing.

Icons.

Consistent errors.

---

# Buttons  [PARTIAL]

Replace all button styles.

Primary

Secondary

Ghost

Danger

Success

Icon buttons

FAB (optional)

---

# Cards  [PARTIAL]

Replace every card.

Rounded

Soft shadows

Hover

Consistent spacing

Responsive

---

# Tables  [TARGET — not built]

Modernize DataTables.

Sticky header

Rounded rows

Search

Filters

Pagination

Better empty state

---

# Dialogs  [PARTIAL]

Replace dialogs.

Rounded

Soft shadow

Modern buttons

Animated opening

Better spacing

---

# Notifications  [PARTIAL]

Modern toast notifications.

Success

Warning

Error

Info

Bottom-right placement.

---

# Search  [PARTIAL]

Modern global search.

Recent searches.

Suggestions.

Keyboard navigation.

Search courses.

Search teachers.

Search lessons.

---

# Authentication  [TARGET — not built]

> **Current:** Auth uses the stock Frappe backend `/login`; there are no SPA
> login/register/OTP pages.

Redesign:

Login

Register

Forgot Password

Reset Password

OTP

Email Verification

Use branded illustrations.

---

# User Profile  [PARTIAL]

Sections

Personal Info

Achievements

Certificates

Completed Courses

Bookmarks

Settings

Avatar

Activity Timeline

---

# Teacher Profile  [TARGET — not built]

Photo

Bio

Courses

Students

Reviews

Social Links

Achievements

---

# Certificates  [PARTIAL]

> **Current:** Certificates exist in the upstream LMS; the custom branded
> certificate (logo, signature, QR, verification URL) is not yet built.

Modern branded certificates.

Logo

Signature

QR code

Verification URL

Download PDF

---

# Blog  [TARGET — not built]

Modern cards.

Categories.

Reading time.

Author.

Related posts.

Search.

---

# Footer  [TARGET — not built]

> **Current:** No footer component exists in the SPA.

Four columns.

About

Programs

Support

Contact

Social icons

Newsletter

Copyright

---

# Mobile Experience  [PARTIAL]

Fully responsive.

Touch friendly.

Bottom spacing.

Large tap targets.

Drawer navigation.

Responsive tables.

Responsive lesson player.

---

# Dark Mode  [PARTIAL]

> **Current:** frappe-ui ships dark-mode tokens and the theme handles
> `[data-theme='dark']` partially; full brand dark mode is not finished.

Architecture must support future dark mode.

Never hardcode colors.

Everything must use tokens.

---

# Animation  [PARTIAL]

Small animations only.

Hover

Buttons

Cards

Dialogs

Dropdowns

Loading

Page transitions

Avoid excessive motion.

---

# Performance  [PARTIAL]

Lazy loading.

Responsive images.

SVG icons.

Minimal bundle size.

Avoid unnecessary JS.

---

# Component Mapping  [TARGET — not built]

> **Current:** Most components are recolored in place via tokens, not replaced with
> bespoke equivalents.

Replace these Frappe components:

Navbar

Sidebar

Buttons

Cards

Inputs

Dialogs

Alerts

Badges

Tables

Pagination

Breadcrumbs

Tabs

Dropdowns

Tooltips

Forms

Calendar styling

Charts styling

Course cards

Dashboard widgets

Student portal

Teacher portal

Login pages

Portal pages

Website pages

---

# Components NOT to Rewrite  [IMPLEMENTED]

Do NOT rebuild:

Authentication

Permissions

API

Database

DocTypes

Workflow Engine

Assignments

Notifications backend

Reports

Only redesign the presentation layer.

---

# Implementation Strategy  [PARTIAL]

Phase 1

Theme

Tokens

Typography

Icons

Navbar

Footer

Global Layout

---

Phase 2

Homepage

Course Pages

Course Cards

Teacher Pages

Authentication

---

Phase 3

Dashboard

Lesson Player

Profile

Certificates

Blog

---

Phase 4

Polish

Animations

Accessibility

Performance

Dark Mode Preparation

Responsive Improvements

---

# Deliverables  [TARGET — not built]

The AI agent should produce:

* Global Design System
* Token-based theme
* Reusable UI component library
* Responsive layouts
* RTL support
* Homepage redesign
* Dashboard redesign
* Course experience redesign
* Authentication redesign
* Student portal redesign
* Teacher portal redesign
* Mobile responsive experience
* Frappe-compatible implementation
* Zero backend regressions

---

# Success Criteria  [TARGET — not built]

✓ Looks like a premium SaaS platform

✓ Preserves all Frappe functionality

✓ Fully token-based

✓ Fully responsive

✓ RTL-first

✓ WCAG compliant

✓ Reusable component architecture

✓ Ready for future dark mode

✓ Easy to maintain and extend

The result should feel like **"Frappe LMS Enterprise Edition"** rather than a themed Frappe instance.
