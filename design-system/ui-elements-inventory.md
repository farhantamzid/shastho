# UI Elements Inventory

This document catalogs all UI elements found in the frontendExamples folder, categorized by type.

## Basic Elements

### Buttons

- Primary Button: `bg-cyan-600 hover:bg-cyan-700 text-white rounded-lg shadow-sm`
- Secondary Button (Link style): `text-cyan-600 hover:text-cyan-500 font-medium`
- Icon Button: Varies based on context

### Form Elements

- Text Input: `appearance-none w-full pl-10 pr-3 py-2.5 border border-gray-300 rounded-lg shadow-sm focus:ring-cyan-500 focus:border-cyan-500`
- Select/Dropdown: `appearance-none w-full pl-10 pr-3 py-2.5 border border-gray-300 rounded-lg shadow-sm focus:ring-cyan-500 focus:border-cyan-500`
- Checkbox: `h-4 w-4 text-cyan-600 focus:ring-cyan-500 border-gray-300 rounded`
- Radio Button: Similar to checkbox but with different border-radius
- Form Label: `block text-sm font-medium text-gray-700 mb-1`
- Input Icon (Left): `absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none`
- Input Validation: Text hints below inputs with varying colors based on validation state

### Typography

- Headings: Various sizes using Tailwind's text-{size} classes
- Body Text: Default and text-gray-600 for secondary text
- Links: text-cyan-600 hover:text-cyan-500
- Small/Helper Text: text-xs or text-sm with text-gray-500

### Icons

- Using Lucide icons with standard sizes (h-4 w-4, h-5 w-5, h-6 w-6)
- Icon colors typically match text colors or are slightly muted (text-gray-400, text-gray-500)

## Components

### Navigation

- Sidebar (Desktop): `flex flex-col w-64 bg-white border-r`
- Sidebar Nav Item: `flex items-center px-4 py-3 text-sm font-medium rounded-md`
- Active Nav Item: `bg-cyan-50 text-cyan-700`
- Mobile Menu: Sliding panel with overlay
- Header/Navbar: `flex h-16 flex-shrink-0 bg-white shadow md:border-b md:shadow-none`

### Cards

- Basic Card: `bg-white rounded-xl shadow-lg p-8 space-y-8`
- Interactive Card: Various hover effects
- Info Card: Used for statistics and metrics

### Modals

- Modal Container: `bg-white rounded-xl shadow-lg p-8`
- Modal Overlay: `fixed inset-0 bg-gray-600 bg-opacity-75`

### Tables

- Table Container: Various styles including striped and bordered variations
- Table Header: `bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider`
- Table Row: Often with hover effects `hover:bg-gray-50`
- Table Cell: Padding and alignment variations

### Forms

- Form Container: `space-y-6` or `space-y-8`
- Form Section: `space-y-5`
- Form Actions: Typically at the bottom with flex layout

### Alerts/Notifications

- Success: Green-themed
- Error: Red-themed
- Warning: Yellow-themed
- Info: Blue-themed

## Layout Patterns

### Page Layouts

- Authentication Pages: Centered card on gradient background
- Dashboard Layout: Sidebar with main content area
- Multi-Column Layouts: Using Tailwind's grid system

### Responsive Patterns

- Mobile Menu Toggle: Shows/hides on small screens
- Responsive Grid: Changes columns based on screen size
- Visibility Classes: `hidden md:block` and similar combinations

## Design Tokens

### Colors

- Primary: Cyan (cyan-600, cyan-700)
- Text: Gray scale (gray-900 for headings, gray-700 for body, gray-500/600 for secondary)
- Background: White for cards/content, gray-50 for page backgrounds
- Accents: Various based on context (success, error, warning, info)

### Spacing

- Using Tailwind's default spacing scale
- Common values: p-4, p-8, my-2, my-4, space-y-6, etc.

### Typography

- Font Families: System fonts (Tailwind defaults)
- Font Sizes: text-xs through text-3xl most common
- Font Weights: font-medium, font-semibold, font-bold

### Borders & Shadows

- Rounded corners: rounded-lg, rounded-xl, rounded-full
- Shadows: shadow-sm, shadow, shadow-lg
- Borders: border, border-gray-300, border-t, border-b, etc.

## Patterns & Interactions

### Form Validation

- Input states (default, focus, error, success)
- Validation messages

### Loading States

- Button loading states
- Page/section loading indicators

### Responsive Behavior

- Mobile-first approach
- Breakpoint system aligns with Tailwind defaults
