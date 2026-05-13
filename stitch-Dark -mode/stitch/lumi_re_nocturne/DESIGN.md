# Design System: Sanctuary at Night

## 1. Overview & Creative North Star: "The Digital Aesthetician"
This design system moves away from the aggressive, high-energy interfaces typical of digital platforms. Instead, it adopts the persona of **The Digital Aesthetician**—an experience defined by composure, clinical precision, and nocturnal serenity. 

The "Sanctuary at Night" ethos is achieved through **Tonal Atmospheric Depth**. We reject the flat, "card-on-canvas" look of standard web templates. Instead, we utilize a hierarchy of darkness, where elements emerge from the `surface` like objects in a dimly lit, premium spa. We prioritize breathing room (negative space) and intentional asymmetry to create an editorial flow that guides the eye rather than forcing it.

---

## 2. Color & Atmospheric Layering
Our palette is a study in shadows and light. We use "Midnight Slate" as our bedrock, allowing our emerald accents to glow with medicinal efficacy.

### The "No-Line" Rule
**Explicit Instruction:** Designers are prohibited from using 1px solid borders to define sections. Layout boundaries must be defined strictly through background color shifts or tonal transitions. Use `surface-container-low` against `surface` to create natural containment.

### Surface Hierarchy & Nesting
Treat the UI as a series of physical layers. Each deeper interaction level should move "closer" to the light source:
*   **Base Layer:** `surface` (#0b1326) – The deep foundation.
*   **Section Layer:** `surface-container-low` (#131b2e) – Subtle grouping.
*   **Interaction Layer:** `surface-container` (#171f33) – Cards and primary modules.
*   **Elevated Layer:** `surface-container-highest` (#2d3449) – Pop-overs and active states.

### The "Glass & Gradient" Rule
To evoke a sense of premium "clinical" glass:
*   **Hero Elements:** Use a subtle linear gradient for primary backgrounds, transitioning from `primary` (#4edea3) to `primary-container` (#10b981) at a 135° angle.
*   **Floating Elements:** Apply a 20px backdrop-blur to containers using a semi-transparent `surface-variant` (#2d3449 at 60% opacity) to create a sophisticated "Sanctuary" feel.

---

## 3. Typography: Editorial Authority
We utilize **Manrope** for its balance of geometric modernism and organic warmth. It feels both clinical and human.

*   **Display (lg/md/sm):** Used for "Hero" moments. Use `display-lg` (3.5rem) with tighter letter-spacing (-0.02em) to create an authoritative, editorial statement.
*   **Headlines:** Reserved for section starts. Ensure `headline-md` (1.75rem) always has ample `padding-bottom` (at least 24px) to respect the "Sanctuary" breathing room.
*   **Body (lg/md/sm):** Our primary carrier of information. High contrast is non-negotiable; use `on-surface` (#dae2fd) to ensure the text "glows" against the dark background without causing eye strain.
*   **Labels:** Use `label-md` (0.75rem) in all-caps with 0.05em tracking for a "Scientific/Clinical" annotation look.

---

## 4. Elevation & Depth
In this system, elevation is a feeling, not a drop-shadow.

*   **The Layering Principle:** Avoid the "floating box" look. To highlight a card, place a `surface-container-lowest` (#060e20) card inside a `surface-container-low` (#131b2e) section. This "recessed" look conveys depth more elegantly than a shadow.
*   **Ambient Shadows:** When a true lift is required (e.g., a floating navigation bar), use a multi-layered shadow: `0px 10px 40px rgba(0, 0, 0, 0.4)`. The shadow color must never be pure black; it should be a deep, tinted variant of the background.
*   **The Ghost Border:** If a border is required for accessibility in input fields, use `outline-variant` (#3c4a42) at **20% opacity**. It should be felt, not seen.

---

## 5. Components

### Buttons
*   **Primary:** Solid `primary` (#4edea3) with `on-primary` (#003824) text. Use `xl` (1.5rem) rounded corners.
*   **Secondary:** Ghost style. No background, `outline` (#86948a) "Ghost Border" (20% opacity), and `primary` text.
*   **Tertiary:** Text-only with an underline that appears on hover, utilizing the `primary-fixed` (#6ffbbe) color for visibility.

### Cards & Modules
*   **Forbid Dividers:** Never use a horizontal line to separate content within a card. Use a 16px or 24px vertical gap from the spacing scale.
*   **Rounding:** Strictly use the `lg` (1rem) or `xl` (1.5rem) tokens for cards to maintain the "soft sanctuary" feel.

### Input Fields
*   **Surface:** Use `surface-container-highest` (#2d3449) for the input bed. 
*   **Focus State:** Transition the "Ghost Border" to 100% opacity using `primary` (#4edea3). 

### Chips & Tags
*   **Style:** Small, pill-shaped (`full` rounding). Use `secondary-container` (#334d38) with `on-secondary-container` (#9fbca3) text to signify botanical/clinical categories without overwhelming the primary CTA.

---

## 6. Do’s and Don’ts

### Do:
*   **Do** use asymmetrical layouts (e.g., a headline on the left, and a body text block shifted slightly to the right) to mimic high-end magazine layouts.
*   **Do** allow for massive white space. If a section feels "full," increase the vertical padding by one scale unit.
*   **Do** use `primary` sparingly. It should be the "Clinical Glow" in the dark, not the dominant color.

### Don’t:
*   **Don’t** use pure white (#FFFFFF). All "white" text should use `on-surface` (#dae2fd) to maintain the nocturnal tone.
*   **Don’t** use standard 4px or 8px corners. Anything less than 12px (`md`) breaks the organic, calming aesthetic.
*   **Don’t** use 1px dividers. If you need to separate content, change the surface tone or increase the margin.