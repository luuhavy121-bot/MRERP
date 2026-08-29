---
name: "MRERP — The Yellow Thread"
description: "A carbon, mineral, and signal-yellow operating system for the MR ECOM workspace."
colors:
  thread-yellow: "#ffc400"
  thread-yellow-hover: "#e8b200"
  carbon: "#090909"
  ledger-ink: "#11110f"
  ledger-white: "#ffffff"
  paper: "#fbfbf8"
  mineral: "#f5f5f1"
  ledger-line: "#deded7"
  muted: "#686863"
  warm-ochre-text: "#816100"
  status-success: "#28a745"
  status-warning: "#f08a22"
  danger: "#a83b32"
typography:
  display:
    fontFamily: "Barlow Condensed, sans-serif"
    fontSize: "68px"
    fontWeight: 800
    lineHeight: 0.84
    letterSpacing: "-0.025em"
  headline:
    fontFamily: "Barlow Condensed, sans-serif"
    fontSize: "48px"
    fontWeight: 800
    lineHeight: 1
    letterSpacing: "-0.025em"
  title:
    fontFamily: "Barlow Condensed, sans-serif"
    fontSize: "34px"
    fontWeight: 700
    lineHeight: 0.95
    letterSpacing: "-0.02em"
  body:
    fontFamily: "DM Sans, sans-serif"
    fontSize: "13px"
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: "normal"
  label:
    fontFamily: "DM Sans, sans-serif"
    fontSize: "12px"
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: "0.02em"
rounded:
  none: "0"
  micro: "2px"
  sm: "5px"
  md: "6px"
  full: "999px"
spacing:
  1: "4px"
  2: "8px"
  3: "12px"
  4: "16px"
  6: "24px"
  7: "28px"
  10: "40px"
  12: "48px"
components:
  button-primary:
    backgroundColor: "{colors.thread-yellow}"
    textColor: "{colors.carbon}"
    typography: "{typography.label}"
    rounded: "{rounded.sm}"
    padding: "12px 19px"
    height: "48px"
  button-primary-hover:
    backgroundColor: "{colors.thread-yellow-hover}"
    textColor: "{colors.carbon}"
    typography: "{typography.label}"
    rounded: "{rounded.sm}"
    padding: "12px 19px"
    height: "48px"
  button-secondary:
    backgroundColor: "{colors.mineral}"
    textColor: "{colors.ledger-ink}"
    typography: "{typography.label}"
    rounded: "{rounded.sm}"
    padding: "9px 11px"
  field:
    backgroundColor: "{colors.ledger-white}"
    textColor: "{colors.ledger-ink}"
    typography: "{typography.body}"
    rounded: "{rounded.md}"
    padding: "0 14px"
    height: "48px"
  navigation-active:
    backgroundColor: "{colors.mineral}"
    textColor: "{colors.carbon}"
    typography: "{typography.label}"
    rounded: "{rounded.sm}"
    padding: "13px 12px"
  ledger-row-selected:
    backgroundColor: "{colors.carbon}"
    textColor: "{colors.thread-yellow}"
    typography: "{typography.body}"
    rounded: "{rounded.none}"
    padding: "12px 16px"
    height: "68px"
  drawer-identity:
    backgroundColor: "{colors.thread-yellow}"
    textColor: "{colors.carbon}"
    typography: "{typography.title}"
    rounded: "{rounded.none}"
    padding: "30px 24px 22px"
---

# Design System: MRERP — The Yellow Thread

## Overview

**Creative North Star: "The Yellow Thread"**

MRERP is an operational workspace, not a collection of decorative admin cards. Its visual language behaves like a precise company ledger: carbon product chrome establishes the ecosystem, while white and warm mineral surfaces keep dense records calm, legible, and easy to scan. The supplied circular MR ECOM logo remains the authoritative brand asset; do not redraw or reinterpret it.

The yellow thread is the memorable connective device. It begins at product context, marks the active rail and tab, passes through a selected ledger row, and terminates in the contextual detail drawer. It is intentionally scarce: yellow communicates focus, continuity, and primary action rather than filling passive surfaces. Vietnamese copy stays concise and direct, while capability-driven visibility, server authorization, field redaction, and real loading, empty, forbidden, and error states remain product constraints rather than visual decoration.

**Key Characteristics:**

- Carbon `#090909` product bar, white navigation rail, and hairline mineral ledger.
- Thread yellow `#ffc400` used for active continuity, selection, focus, and primary actions.
- Compressed Barlow Condensed display hierarchy paired with DM Sans operational text.
- Flat-by-default surfaces, square-to-6 px controls, and minimal contextual elevation.
- Dense, responsive records that preserve the available action and status context.

## Colors

The palette is high-contrast and material: carbon and ink provide authority, white/mineral create the ledger, and one saturated yellow carries focus across the interface.

### Primary

- **Thread Yellow** (`#ffc400`): the single product signal for primary buttons, active product/tab rules, focus rings, selected-row continuity, and drawer identity bands. Hover darkens to `#e8b200`.
- **Carbon** (`#090909`): fixed product chrome and the selected ledger-row ground. Pair it with white for general chrome and Thread Yellow for the focused record.

### Neutral

- **Ledger White** (`#ffffff`): main workspace, rail, fields, and record rows.
- **Paper** (`#fbfbf8`): warm off-white background where a slight surface distinction is required.
- **Mineral** (`#f5f5f1`): quiet hover, secondary controls, and active rail-item fill.
- **Ledger Ink** (`#11110f`): default text and icon color.
- **Muted** (`#686863`): secondary copy and metadata; never use it for essential state without a label.
- **Ledger Line** (`#deded7`): 1 px dividers, field borders, rail borders, and table rules.
- **Warm Ochre Text** (`#816100`): low-emphasis yellow-family text when full Thread Yellow would not meet contrast on white.

### Tertiary

- **Status Success** (`#28a745`): confirms an active or healthy state alongside a readable label.
- **Status Warning** (`#f08a22`): marks probation or another attention state alongside a readable label.
- **Danger** (`#a83b32`): reserved for errors and destructive actions with explicit copy.

### Named Rules

**The One Thread Rule.** Yellow is a directional signal, not a background theme. Preserve enough white and carbon around it that the active path remains unmistakable.

**The Ledger Rule.** Use white/mineral tonal changes and 1 px rules before inventing another surface color.

## Typography

**Display Font:** Barlow Condensed (with `sans-serif` fallback)

**Body Font:** DM Sans (with `sans-serif` fallback)

**Character:** Barlow Condensed gives product names, page titles, counts, and drawer identities a compressed operational confidence. DM Sans carries Vietnamese navigation, controls, labels, metadata, and record content with a neutral, human rhythm. Do not restore Manrope as the design-system default; existing legacy declarations are migration evidence, not the Yellow Thread direction.

### Hierarchy

- **Display** (800, 68 px, 0.84): the uppercase People command-stage title; reduce to 64 px below 980 px and 54 px below 640 px.
- **Headline** (800, 48 px, 1): non-People workspace page titles and large section statements.
- **Title** (700, 34 px, 0.95): selected-person identity and strong contextual headings.
- **Body** (400, 13 px, 1.5): record content, supporting copy, and form text. Keep long explanatory copy narrow enough to scan.
- **Label** (700, 12 px, 1.2, subtle positive tracking): navigation, tabs, table labels, and controls. Uppercase is reserved for structural labels, not full paragraphs.

**The Compressed Signal Rule.** Barlow Condensed identifies hierarchy and key quantities; DM Sans performs the work. Do not set dense body records in the display face.

## Layout

Desktop uses a fixed 78 px carbon product bar and a fixed 196 px white navigation rail. Standard workspaces begin below the bar with a capped 1600 px content area; People deliberately runs full-width so its command stage, ledger, and contextual drawer can form one continuous horizontal system. The People command stage uses a two-column layout, 40 px side insets, a 238 px minimum height, and a 3 px vertical plus 2 px horizontal yellow thread.

The ledger is structured by alignment and rules rather than card islands. Desktop employee rows use five columns and a 68 px minimum height. Opening a record reserves a 350 px contextual column; the selected row extends its yellow line to that drawer. Use the implemented 4 px rhythm, with 8, 12, 16, 24, 28, 40, and 48 px as the recurring working intervals.

Responsive behavior is structural, not a uniform shrink:

- Below 1280 px, reduce product-switcher/action detail and stack the People command-stage tools beneath its identity block.
- Below 980 px, the bar and rail become 68 px, navigation becomes icon-only, People gutters reduce to 24 px, and the 350 px drawer becomes an overlay up to 420 px wide.
- Below 640 px, use 16 px People gutters, stack search/filter/create controls, wrap tabs, hide secondary CSV actions and the debug persona switcher, reduce display/count type, and collapse the ledger to identity, status, and view action. The drawer occupies the viewport width remaining beside the rail.

## Elevation & Depth

The system is flat by default. Product chrome, navigation, command stages, ledgers, and controls are separated with tone, borders, and the yellow thread—not ambient card shadows. Elevation appears only when a contextual layer must sit above the ledger.

### Shadow Vocabulary

- **Context Drawer** (`-16px 0 46px rgba(0,0,0,.06)`): a restrained left-edge lift for the People detail drawer.
- **Selected Record** (`inset 0 0 0 1px #ffc400`): a structural inset edge, not a floating shadow.

**The Flat-by-Default Rule.** A surface earns elevation only when it changes interaction depth. Use ledger rules and tonal separation everywhere else.

## Shapes

Yellow Thread geometry is mostly square with just enough softening for touch controls. Buttons use 5 px corners; fields and compound filters use 6 px; active tab indicators, ledger rules, drawer bands, and status markers stay square. Circular geometry is reserved for the supplied logo, avatars, search glyph, and other identity-sized marks. Avoid the former system’s 12–24 px rounded card language and decorative pill saturation; pills are appropriate only for identity/status tokens whose silhouette carries meaning.

## Components

### Product Bar

- **Structure:** fixed 78 px carbon bar, with a 196 px brand cell, product switcher, then account actions.
- **Active product:** Thread Yellow text plus a 3 px bottom rule; inactive products use muted mineral text and 1 px carbon dividers.
- **Brand:** use `/brand/mr-ecom-logo.png` at 40 px and retain the `MR ECOM` wordmark. The logo image has an empty `alt` only when the adjacent wordmark supplies the accessible name.

### Navigation Rail

- **Style:** white, 196 px wide, 1 px right rule, compact line icons and DM Sans labels.
- **Active state:** mineral fill plus a 4 px Thread Yellow rule at the outer edge. Hover uses mineral without adding shadow.
- **Responsive:** icon-only at 68 px below 980 px; keep each navigation button’s accessible name even when its visible label is hidden.

### Buttons

- **Primary:** Thread Yellow on Carbon, 48 px high for command-stage actions, 5 px corners, no shadow.
- **Secondary:** mineral on Ledger Ink with the same compact geometry.
- **Hover / Focus:** primary darkens to `#e8b200`; all interactive elements receive a 3 px `rgba(255,196,0,.36)` focus-visible outline with 2 px offset.
- **Destructive:** use Danger with explicit destructive copy; never encode risk through color alone.

### Inputs / Fields

- **Style:** 48 px high, Ledger White, 1 px `#d5d5ce` or Ledger Line border, 6 px corners, and direct labels or accessible names.
- **Focus:** retain the global yellow focus-visible outline; do not rely only on a subtle border shift.
- **State:** disabled controls remain legible and non-interactive; errors use a message plus Danger treatment and preserve the correlation/reference information provided by the product.

### Tabs

- **Style:** flat on the ledger, with no segmented-control container. Use compact DM Sans labels and generous horizontal spacing.
- **Active state:** Ledger Ink plus a 3 px Thread Yellow bottom rule. Tabs remain real `role="tab"` controls with `aria-selected`.

### Ledger / Selected Row

- **Default:** white 68 px rows separated by 1 px mineral rules; hover uses a pale yellow wash (`#fff9df`).
- **Selected:** Carbon fill, Thread Yellow text and 1 px inset edge. A 3 px yellow line extends left and right to connect navigation context with the drawer.
- **Status:** a square semantic marker always accompanies a readable status label. Use tabular numerals for counts.

### Context Drawer

- **Desktop:** fixed to the right below the product bar, 350 px wide, with a minimal left shadow and no darkened backdrop.
- **Identity band:** Thread Yellow with Carbon avatar, title, metadata rules, and status label.
- **Responsive:** becomes an overlay below 980 px, with a subtle backdrop and width capped at 420 px. Its 220 ms reveal uses `cubic-bezier(.16,1,.3,1)` and must be disabled under reduced motion.

### Data and Feedback States

- Loading, empty, forbidden, and error states occupy the same ledger or panel region they replace so layout does not jump unpredictably.
- State meaning always includes text; icons and colors reinforce rather than carry the message alone.
- Capability-gated actions may be absent, but the frontend never claims to be the authorization barrier.

## Do's and Don'ts

### Do:

- **Do** carry one visible Thread Yellow path through active product, navigation/tab context, selected record, and contextual detail when those elements coexist.
- **Do** use white/mineral ledger surfaces, 1 px rules, aligned columns, and restrained density before introducing cards.
- **Do** use Barlow Condensed for display signals and DM Sans for operational content.
- **Do** preserve Vietnamese labels, server-driven scope, field redaction, accessible names, keyboard focus, and explicit loading/empty/forbidden/error states.
- **Do** disable the drawer animation and button/row transitions when `prefers-reduced-motion: reduce` is active.

### Don't:

- **Don't** restore the stale forest-green/lime visual system or use green as the general action/focus color; green is semantic only.
- **Don't** flood passive surfaces with yellow, add ornamental gradients, or use shadows to make every container float.
- **Don't** rebuild the old 12–24 px rounded-card language inside Yellow Thread surfaces.
- **Don't** use color alone for employment state, selection, warning, error, or destructive intent.
- **Don't** redraw the MR ECOM logo, infer backend policy from a prototype, or expose actions the current capability set does not allow.
