# Design Tokens

This document defines the design tokens (colors, typography, spacing, etc.) used in the HealthBD application.

## Color Palette

### Primary Colors

| Name          | Tailwind Class | Hex Value | Usage                                 |
| ------------- | -------------- | --------- | ------------------------------------- |
| Primary       | cyan-600       | #0891b2   | Primary buttons, links, active states |
| Primary Hover | cyan-700       | #0e7490   | Button hover states                   |
| Primary Light | cyan-50        | #ecfeff   | Active nav items, highlights          |

### Neutral Colors

| Name          | Tailwind Class | Hex Value | Usage                                      |
| ------------- | -------------- | --------- | ------------------------------------------ |
| Black         | gray-900       | #111827   | Headings, text                             |
| Dark Gray     | gray-700       | #374151   | Body text                                  |
| Medium Gray   | gray-500       | #6b7280   | Secondary text, icons                      |
| Light Gray    | gray-300       | #d1d5db   | Borders                                    |
| Lighter Gray  | gray-100       | #f3f4f6   | Dividers                                   |
| Lightest Gray | gray-50        | #f9fafb   | Backgrounds, table headers                 |
| White         | white          | #ffffff   | Card backgrounds, text on dark backgrounds |

### Semantic Colors

| Name    | Tailwind Class | Hex Value | Usage                                    |
| ------- | -------------- | --------- | ---------------------------------------- |
| Success | green-500      | #10b981   | Success messages, positive indicators    |
| Warning | amber-500      | #f59e0b   | Warning messages, caution indicators     |
| Error   | red-500        | #ef4444   | Error messages, destructive actions      |
| Info    | blue-500       | #3b82f6   | Information messages, neutral indicators |

## Typography

### Font Family

The application uses Tailwind's default font stack:

```css
font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI",
  Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif, "Apple Color Emoji",
  "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji";
```

### Font Sizes

| Name | Tailwind Class | Size     | Usage                       |
| ---- | -------------- | -------- | --------------------------- |
| XS   | text-xs        | 0.75rem  | Helper text, footnotes      |
| SM   | text-sm        | 0.875rem | Form labels, secondary text |
| Base | text-base      | 1rem     | Body text, buttons          |
| LG   | text-lg        | 1.125rem | Subheadings                 |
| XL   | text-xl        | 1.25rem  | Section headings            |
| 2XL  | text-2xl       | 1.5rem   | Page headings               |
| 3XL  | text-3xl       | 1.875rem | Major headings, logos       |

### Font Weights

| Name     | Tailwind Class | Weight | Usage                        |
| -------- | -------------- | ------ | ---------------------------- |
| Regular  | font-normal    | 400    | Body text                    |
| Medium   | font-medium    | 500    | Emphasized text, buttons     |
| Semibold | font-semibold  | 600    | Subheadings                  |
| Bold     | font-bold      | 700    | Headings, important elements |

## Spacing

The application follows Tailwind's default spacing scale, with the following common values:

### Common Spacing Values

| Name | Tailwind Class | Value          | Usage               |
| ---- | -------------- | -------------- | ------------------- |
| 0    | p-0, m-0       | 0              | No spacing          |
| 1    | p-1, m-1       | 0.25rem (4px)  | Minimal spacing     |
| 2    | p-2, m-2       | 0.5rem (8px)   | Tight spacing       |
| 3    | p-3, m-3       | 0.75rem (12px) | Compact elements    |
| 4    | p-4, m-4       | 1rem (16px)    | Standard spacing    |
| 5    | p-5, m-5       | 1.25rem (20px) | Medium spacing      |
| 6    | p-6, m-6       | 1.5rem (24px)  | Comfortable spacing |
| 8    | p-8, m-8       | 2rem (32px)    | Section spacing     |
| 10   | p-10, m-10     | 2.5rem (40px)  | Large spacing       |
| 12   | p-12, m-12     | 3rem (48px)    | Extra large spacing |

### Specific Component Spacing

| Component     | Spacing Pattern                |
| ------------- | ------------------------------ |
| Buttons       | px-4 py-2.5                    |
| Form Inputs   | px-3 py-2.5                    |
| Cards         | p-8 space-y-6 or p-8 space-y-8 |
| Modal         | p-8                            |
| Nav Items     | px-4 py-3                      |
| Page Sections | p-4 md:p-8                     |

## Borders & Rounded Corners

### Border Widths

| Name   | Tailwind Class | Width | Usage              |
| ------ | -------------- | ----- | ------------------ |
| Thin   | border         | 1px   | Standard borders   |
| Medium | border-2       | 2px   | Emphasized borders |
| None   | border-0       | 0px   | No border          |

### Border Radii

| Name   | Tailwind Class | Radius         | Usage                              |
| ------ | -------------- | -------------- | ---------------------------------- |
| Small  | rounded        | 0.25rem (4px)  | Minimal rounding                   |
| Medium | rounded-md     | 0.375rem (6px) | Subtle rounding                    |
| Large  | rounded-lg     | 0.5rem (8px)   | Standard elements (forms, buttons) |
| XL     | rounded-xl     | 0.75rem (12px) | Cards, modals                      |
| Full   | rounded-full   | 9999px         | Avatars, circular elements         |

## Shadows

| Name   | Tailwind Class | Description       | Usage                  |
| ------ | -------------- | ----------------- | ---------------------- |
| Small  | shadow-sm      | Subtle shadow     | Buttons, form elements |
| Medium | shadow         | Standard shadow   | Cards, dropdowns       |
| Large  | shadow-lg      | Pronounced shadow | Modals, popovers       |
| None   | shadow-none    | No shadow         | Flat elements          |

## Responsive Breakpoints

The application follows Tailwind's default breakpoint system:

| Name        | Tailwind Prefix | Min Width | Description                        |
| ----------- | --------------- | --------- | ---------------------------------- |
| Small       | sm:             | 640px     | Small devices like portrait phones |
| Medium      | md:             | 768px     | Tablets and landscape phones       |
| Large       | lg:             | 1024px    | Desktops and large tablets         |
| Extra Large | xl:             | 1280px    | Large desktop screens              |
| 2X Large    | 2xl:            | 1536px    | Extra large screens                |

### Responsive Patterns

- Mobile-first approach: Default styles are for mobile, with responsive modifiers for larger screens
- Navigation: Sidebar hidden on mobile, visible on md: and larger
- Layouts: Single column on mobile, multiple columns on larger screens
- Typography: Adjusts size at certain breakpoints (text-base md:text-lg)
- Spacing: Often increases at larger breakpoints (p-4 md:p-8)

## Z-Index Scale

| Name    | Z-Index Value | Usage                                |
| ------- | ------------- | ------------------------------------ |
| Base    | 0             | Default elements                     |
| Low     | 10            | Sticky elements, subtle overlays     |
| Medium  | 20            | Dropdowns, tooltips                  |
| High    | 30            | Modals, sidebars                     |
| Top     | 40            | Notifications, alerts                |
| Overlay | 50            | Modal overlays, full-screen overlays |

These design tokens should be consistently applied across all components to maintain a cohesive visual language throughout the application.
