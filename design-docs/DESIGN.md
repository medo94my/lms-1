> **Status — target design spec (roadmap), not current-state.** As of 2026-06, the
> app is the upstream Frappe LMS Vue SPA **recolored via frappe-ui token overrides**
> (`frontend/src/styles/basiret-theme.css`, `frontend/tailwind.config.js`). The
> bespoke marketing site, custom components, footer, auth pages, and homepage
> sections described below are largely **not yet built**. Section tags —
> `[IMPLEMENTED]` / `[PARTIAL]` / `[TARGET — not built]` — mark what is live today vs.
> aspirational; `> **Current:**` notes flag where this spec differs from the running
> app. The design vision here is preserved as the roadmap.

# design.md

## Project  [PARTIAL]

> **Current:** The brand identity (deep-green / gold / cream) is applied via the
> frappe-ui token theme. The standalone bespoke platform described below is aspirational.

Educational Islamic learning platform for **Basiret Vakfi / وقف بصيرة**.

The website should feel trustworthy, calm, elegant, educational, and modern.
It is inspired by Islamic architecture, Quranic learning, Arabic education platforms, and clean SaaS/LMS interfaces.

---

## Brand Direction  [PARTIAL]

> **Current:** Deep-green primary, gold accent, and cream backgrounds are live via
> the token theme; Islamic geometric background patterns are not implemented.

### Brand Personality

* Trustworthy
* Educational
* Spiritual
* Premium but simple
* Calm and welcoming
* Community-focused
* Arabic-first / RTL-friendly

### Visual Style

Use a clean white and cream background with deep green as the main brand color and gold as an accent color.

The design should avoid visual clutter. Islamic geometric patterns may be used lightly as background decoration with very low opacity.

---

## Layout Direction  [PARTIAL]

> **Current:** Courses, Course detail, and the student dashboard exist.
> Teacher-profile, About, Contact, and the marketing Homepage do not; login/register
> is the Frappe backend page, not an SPA page.

### Website Type

Educational platform / LMS website similar to Frappe-style clean interfaces.

### Main Pages

* Homepage
* Courses listing page
* Course detail page
* Teacher profile page
* Student dashboard
* Login / register page
* About page
* Contact page

---

## Homepage Structure  [TARGET — not built]

> **Current:** There is no marketing homepage. `/` redirects guests to `/courses`;
> logged-in users see a dashboard ("Hey {name} 👋"), not this hero/stats/feature layout.

### 1. Header / Navbar

> **Current:** Navigation is the frappe-ui left **sidebar** (deep-green), not a top
> navbar; there is no cart, and the active item uses a gold inline-start border, not
> a nav underline.

The navbar should include:

* Logo on the left or right depending on language direction
* Navigation links:

  * الرئيسية
  * الدورات
  * البرامج
  * المعلمون
  * عن الوقف
  * المدونة
  * تواصل معنا
* Search icon
* Cart icon if needed
* Login button
* Create account button

Style:

* White background
* Subtle bottom border
* Rounded buttons
* Green primary CTA
* Gold active navigation underline

---

### 2. Hero Section

The hero should include:

* Large Arabic headline
* Supporting paragraph
* Two CTA buttons
* Right-side educational image or illustration

Suggested headline:
تعلم لتفهم، واعمل لتؤثر.

Suggested paragraph:
منصة تعليمية تقدم دورات علمية موثوقة في مختلف العلوم الشرعية واللغة العربية والمهارات، لبناء جيل واعٍ نافع لمجتمعه.

Primary CTA:
استكشف الدورات

Secondary CTA:
تصفح البرامج

Hero visual:

* Quran
* Books
* Laptop showing learning dashboard
* Islamic geometric light pattern
* Curved gold divider inspired by the logo

---

### 3. Stats Section

Display key metrics:

* 25K+ طالب وطالبة
* 150+ دورة تعليمية
* 30+ شهادة معتمدة
* 10+ دول حول العالم

Style:

* Icons with green outline
* Small gold accents
* Clean horizontal layout

---

### 4. Feature Strip

Show platform benefits:

* تعلم مرن
* محتوى موثوق
* شهادات معتمدة
* تفاعل ودعم

Each feature should have:

* Icon
* Title
* Short description

---

### 5. Featured Courses

Course cards should include:

* Course image
* Category badge
* Course title
* Teacher name
* Rating
* Number of students
* Level

Example course cards:

* العقيدة الوسطية
* تفسير سورة البقرة
* أصول الفقه
* النحو الميسر

---

### 6. About / Mission Card

Include a side card explaining the foundation mission.

Suggested copy:
نسعى إلى نشر العلم الشرعي الصحيح وبناء الإنسان الواعي الملتزم، عبر برامج تعليمية نوعية ومجتمع معرفي ملهم.

CTA:
تعرف على الوقف

---

## Components  [PARTIAL]

> **Current:** Components are stock frappe-ui, recolored by token overrides — not
> bespoke builds.

### Buttons

#### Primary Button

> **Current:** Buttons are the frappe-ui `Button` (rounded-md), recolored brand-green
> via token overrides — no pill radius and no gold-border secondary variant.

Use for main actions:

* استكشف الدورات
* إنشاء حساب
* التسجيل الآن

Style:

* Deep green background
* White text
* Fully rounded pill
* Optional arrow icon
* Soft shadow

#### Secondary Button

Use for less important actions:

* تصفح البرامج
* معرفة المزيد

Style:

* White or transparent background
* Green text
* Gold border
* Rounded pill

#### Ghost Button

Use in navigation or light areas:

* Transparent background
* Green text
* No border or very subtle border

---

### Cards

#### Course Card

Should include:

* Rounded image
* White background
* Soft border
* Subtle shadow
* Category badge on image
* Rating row
* Level indicator

#### Info Card

Used for vision, mission, features, and benefits.

Style:

* White background
* Rounded corners
* Green circular icon background
* Short text

---

### Forms

Inputs should be:

* Rounded
* Light border
* White background
* Clear focus state using green border
* Error state using red border

Fields:

* Full name
* Email
* Password
* Search
* Select dropdown

---

### Tabs

> **Current:** The real course-detail tabs are Overview / Dashboard / Course editor /
> Settings (instructor-facing); the student view renders curriculum and reviews inline,
> not these five Arabic tabs.

Used on course detail pages.

Tabs:

* نظرة عامة
* الدروس
* المحتوى
* المناقشات
* التقييمات

Active tab:

* Green text
* Green underline

---

### Badges

Use badges for:

* جديد
* الأكثر مبيعاً
* مجاني
* مبتدئ
* متوسط
* متقدم

Style:

* Soft background
* Rounded pill
* Small text

---

### Alerts

Success:
تم حفظ البيانات بنجاح

Warning:
يرجى مراجعة البيانات قبل المتابعة

Error:
حدث خطأ ما، يرجى المحاولة مرة أخرى

Info:
هذه رسالة معلومات للتوضيح فقط

---

### Modal

Use clean centered modal with:

* Rounded container
* Close icon
* Success icon
* Title
* Short message
* CTA button

Example:
تم التسجيل بنجاح
مرحباً بك في وقف بصيرة

---

### Footer  [TARGET — not built]

> **Current:** No footer component exists in the SPA.

Footer should use deep green background.

Include:

* Logo
* Short mission text
* Quick links
* Support links
* Contact information
* Social icons

---

## Icon Style  [PARTIAL]

Use thin line icons.

Recommended icon themes:

* Book
* Graduation cap
* Certificate
* Shield
* Heart
* Users
* Globe
* Clock
* Search
* Cart
* Bell
* Profile

Icon style:

* Stroke icons
* Rounded edges
* Green as default
* Gold for highlights

---

## Typography  [PARTIAL]

> **Current:** Tajawal, Cairo, and Inter are loaded and wired (`--font-arabic` /
> `--font-latin`); **Poppins is not loaded**.

Arabic:
Use `Tajawal` or `Cairo`.

English / Latin:
Use `Inter` or `Poppins`.

Recommended usage:

* Headings: Tajawal Bold
* Body: Tajawal Regular
* Buttons: Tajawal Medium
* Numbers: Inter Medium

---

## Design Rules  [PARTIAL]

1. Use green for trust, education, and primary actions.
2. Use gold only as an accent, not as the main background.
3. Keep layouts spacious.
4. Use cream backgrounds for soft sections.
5. Keep Islamic patterns subtle, around 5% to 10% opacity.
6. Use rounded corners consistently.
7. Avoid heavy shadows.
8. Support RTL layout properly.
9. Make the interface mobile-friendly.
10. Keep the LMS experience simple and clear.

---

## UI Feel  [TARGET — not built]

The final website should feel like:

* A premium Islamic education platform
* A clean Frappe-style web app
* A trustworthy foundation website
* A modern Arabic LMS
