# product.md

# Basiret Vakfi LMS

## Product Specification

### UI/UX Modernization for Frappe LMS

Version: 1.0

---

# Objective

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

# Design Goals

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

# Design Principles

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

# Technical Constraints

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

# Branding

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

# Theme

Implement a global theme.

Replace default Frappe colors.

Use CSS variables from color-tokens.md.

Every component should inherit tokens.

Do NOT hardcode colors.

---

# Navigation

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

# Homepage

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

# Dashboard

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

# Course Listing

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

# Course Detail

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

# Lesson Player

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

# Dashboard Sidebar

Modernize.

Icons

Rounded

Collapsible

Animated

Dark/light ready

---

# Forms

Replace all forms.

Rounded inputs.

Modern validation.

Floating labels optional.

Better spacing.

Icons.

Consistent errors.

---

# Buttons

Replace all button styles.

Primary

Secondary

Ghost

Danger

Success

Icon buttons

FAB (optional)

---

# Cards

Replace every card.

Rounded

Soft shadows

Hover

Consistent spacing

Responsive

---

# Tables

Modernize DataTables.

Sticky header

Rounded rows

Search

Filters

Pagination

Better empty state

---

# Dialogs

Replace dialogs.

Rounded

Soft shadow

Modern buttons

Animated opening

Better spacing

---

# Notifications

Modern toast notifications.

Success

Warning

Error

Info

Bottom-right placement.

---

# Search

Modern global search.

Recent searches.

Suggestions.

Keyboard navigation.

Search courses.

Search teachers.

Search lessons.

---

# Authentication

Redesign:

Login

Register

Forgot Password

Reset Password

OTP

Email Verification

Use branded illustrations.

---

# User Profile

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

# Teacher Profile

Photo

Bio

Courses

Students

Reviews

Social Links

Achievements

---

# Certificates

Modern branded certificates.

Logo

Signature

QR code

Verification URL

Download PDF

---

# Blog

Modern cards.

Categories.

Reading time.

Author.

Related posts.

Search.

---

# Footer

Four columns.

About

Programs

Support

Contact

Social icons

Newsletter

Copyright

---

# Mobile Experience

Fully responsive.

Touch friendly.

Bottom spacing.

Large tap targets.

Drawer navigation.

Responsive tables.

Responsive lesson player.

---

# Dark Mode

Architecture must support future dark mode.

Never hardcode colors.

Everything must use tokens.

---

# Animation

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

# Performance

Lazy loading.

Responsive images.

SVG icons.

Minimal bundle size.

Avoid unnecessary JS.

---

# Component Mapping

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

# Components NOT to Rewrite

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

# Implementation Strategy

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

# Deliverables

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

# Success Criteria

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
