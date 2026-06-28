# color-tokens.md

## Brand Color Tokens

Use these tokens as the single source of truth for the website theme.

```css
:root {
  /* =========================
     PRIMARY GREEN
  ========================== */

  --color-primary-50: #EAF5EF;
  --color-primary-100: #D5EADF;
  --color-primary-200: #ABD5BF;
  --color-primary-300: #80BF9E;
  --color-primary-400: #56AA7E;
  --color-primary-500: #0E8F58;
  --color-primary-600: #0A7448;
  --color-primary-700: #075536;
  --color-primary-800: #063F2B;
  --color-primary-900: #03291C;

  /* =========================
     BRAND GOLD
  ========================== */

  --color-gold-50: #FBF7E8;
  --color-gold-100: #F5EECF;
  --color-gold-200: #EADDA0;
  --color-gold-300: #DECB70;
  --color-gold-400: #D4B64A;
  --color-gold-500: #C6A63A;
  --color-gold-600: #B89A2E;
  --color-gold-700: #9A7D1D;
  --color-gold-800: #7A6417;
  --color-gold-900: #4F3F0D;

  /* =========================
     CREAM / BACKGROUND
  ========================== */

  --color-cream-50: #FFFDF8;
  --color-cream-100: #FBF8F0;
  --color-cream-200: #F5EFE2;
  --color-cream-300: #EDE3D1;
  --color-cream-400: #E2D3BB;

  /* =========================
     NEUTRAL
  ========================== */

  --color-neutral-50: #FAFAF9;
  --color-neutral-100: #F3F3F1;
  --color-neutral-200: #E6E2DA;
  --color-neutral-300: #D2CCC1;
  --color-neutral-400: #AFA89B;
  --color-neutral-500: #8A857C;
  --color-neutral-600: #77736B;
  --color-neutral-700: #3B3935;
  --color-neutral-800: #242321;
  --color-neutral-900: #181818;

  /* =========================
     SEMANTIC
  ========================== */

  --color-success-50: #EAF5EF;
  --color-success-500: #0A8B54;
  --color-success-700: #075536;

  --color-warning-50: #FBF7E8;
  --color-warning-500: #C6A63A;
  --color-warning-700: #9A7D1D;

  --color-error-50: #FDEDEC;
  --color-error-500: #D6453D;
  --color-error-700: #B3261E;

  --color-info-50: #EAF3FA;
  --color-info-500: #2F6F9F;
  --color-info-700: #1F5278;

  /* =========================
     BACKGROUNDS
  ========================== */

  --bg-page: #FFFFFF;
  --bg-soft: #FBF8F0;
  --bg-card: #FFFFFF;
  --bg-muted: #F3F3F1;
  --bg-green-soft: #EAF5EF;
  --bg-gold-soft: #FBF7E8;
  --bg-footer: #063F2B;

  /* =========================
     TEXT
  ========================== */

  --text-primary: #181818;
  --text-secondary: #5F5B54;
  --text-muted: #8A857C;
  --text-inverse: #FFFFFF;
  --text-brand: #075536;
  --text-gold: #B89A2E;
  --text-error: #B3261E;
  --text-success: #075536;

  /* =========================
     BORDER
  ========================== */

  --border-light: #E8E3D8;
  --border-muted: #D2CCC1;
  --border-brand: #075536;
  --border-brand-soft: #ABD5BF;
  --border-gold: #C6A63A;
  --border-gold-soft: #EADDA0;
  --border-error: #D6453D;

  /* =========================
     BUTTONS
  ========================== */

  --button-primary-bg: #075536;
  --button-primary-bg-hover: #063F2B;
  --button-primary-text: #FFFFFF;

  --button-secondary-bg: #FFFFFF;
  --button-secondary-border: #C6A63A;
  --button-secondary-text: #075536;
  --button-secondary-bg-hover: #FBF7E8;

  --button-ghost-bg: transparent;
  --button-ghost-text: #075536;
  --button-ghost-bg-hover: #EAF5EF;

  /* =========================
     INPUTS
  ========================== */

  --input-bg: #FFFFFF;
  --input-border: #E6E2DA;
  --input-border-focus: #075536;
  --input-border-error: #D6453D;
  --input-placeholder: #AFA89B;
  --input-text: #181818;

  /* =========================
     CARDS
  ========================== */

  --card-bg: #FFFFFF;
  --card-border: #E8E3D8;
  --card-shadow: 0 8px 24px rgba(0, 0, 0, 0.06);
  --card-shadow-hover: 0 14px 36px rgba(0, 0, 0, 0.10);

  /* =========================
     SHADOWS
  ========================== */

  --shadow-xs: 0 2px 6px rgba(0, 0, 0, 0.04);
  --shadow-sm: 0 4px 12px rgba(0, 0, 0, 0.06);
  --shadow-md: 0 10px 30px rgba(0, 0, 0, 0.10);
  --shadow-lg: 0 18px 50px rgba(0, 0, 0, 0.14);

  /* =========================
     RADIUS
  ========================== */

  --radius-xs: 4px;
  --radius-sm: 8px;
  --radius-md: 14px;
  --radius-lg: 24px;
  --radius-xl: 36px;
  --radius-pill: 999px;

  /* =========================
     SPACING
  ========================== */

  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 24px;
  --space-6: 32px;
  --space-7: 48px;
  --space-8: 64px;
  --space-9: 96px;
  --space-10: 128px;

  /* =========================
     TYPOGRAPHY
  ========================== */

  --font-arabic: "Tajawal", "Cairo", sans-serif;
  --font-latin: "Inter", "Poppins", sans-serif;

  --font-weight-regular: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;

  --text-xs: 12px;
  --text-sm: 14px;
  --text-base: 16px;
  --text-lg: 20px;
  --text-xl: 28px;
  --text-2xl: 40px;
  --text-hero: 56px;

  --line-tight: 1.2;
  --line-normal: 1.6;
  --line-loose: 1.9;
}
```

## Frappe / LMS Theme Override (frappe-ui Vue SPA)

> **Mechanism note (corrected).** The LMS app the user sees is the **frappe-ui
> Vue SPA**, not the legacy Frappe **desk** (Bootstrap) UI. Bootstrap-style
> variables — `--primary`, `--body-bg`, `--card-bg`, `--navbar-bg`,
> `--btn-primary-bg`, `--footer-bg`, etc. — are **inert** in the SPA: no
> frappe-ui component reads them. Recoloring the SPA means overriding the
> frappe-ui **semantic tokens** (`--surface-*`, `--ink-*`, `--outline-*`) in
> `frontend/src/styles/basiret-theme.css`. The Tailwind utilities
> `bg-surface-*` / `text-ink-*` / `border-outline-*` resolve to these CSS
> variables, so overriding the variable recolors every component that uses it.
> Adding brand colors to `tailwind.config.js` (`primary`/`gold`/`cream`) only
> exposes `bg-primary-700` etc. for **new** custom markup — it does not recolor
> existing frappe-ui chrome.

```css
/* Override THESE in basiret-theme.css (NOT --body-bg/--navbar-bg/--primary). */
:root,
:root[data-theme='light'] {
  /* Primary (solid) buttons use the dark gray surface scale. */
  --surface-gray-7: #0A7448;  /* primary-600 */
  --surface-gray-8: #075536;  /* primary-700 */
  --surface-gray-9: #063F2B;  /* primary-800 */
  --surface-gray-10: #075536; /* primary-700 — button resting bg */

  /* Links / active / info / selected use the BLUE accent family — remap to green. */
  --surface-blue-6: #0E8F58;
  --outline-blue-6: #0E8F58;
  --ink-blue-5: #0E8F58;
  /* (full 1–10 ramps live in basiret-theme.css) */
}

/* Deep-green side nav: remap its token, then invert inks on the subtree.
   The top header stays WHITE (DESIGN.md) — do not touch --surface-base. */
.bg-surface-sidebar {
  --surface-sidebar: #063F2B;  /* primary-800 */
  --ink-gray-7: #E3F1EA;
  --ink-gray-8: #FFFFFF;
  --ink-gray-9: #FFFFFF;
}
```

**Surfaces stay white / get cream by token, not by `--card-bg`:**

* Cards: frappe-ui `Card` uses literal `bg-white`; modals use `--surface-elevation-1`;
  dropdowns use `--surface-elevation-2` — all stay **white** automatically.
* Page (content panel): made **cream** at the layout wrapper
  (`DesktopLayout.vue` → `bg-[#fbf8f0]`), NOT by tinting `--surface-base`
  (which also backs white cards/header/inputs).
* Gold (`#C6A63A`): accents/active states (e.g. sidebar active item
  `border-s-2 border-[#c6a63a] text-[#c6a63a]`).

## Usage Rules

* Primary actions use `--color-primary-700`.
* Hover states use `--color-primary-800`.
* Gold should be used for accents, borders, dividers, badges, and decorative elements.
* Do not use gold as the main button background except for special premium highlights.
* Page backgrounds should usually be white or cream.
* Cards should remain white with soft borders.
* Islamic patterns should use gold or green at very low opacity.
* Error states should always use red, not gold.

