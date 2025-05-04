# Frontend Coding Standards

This document outlines coding standards, patterns, and best practices for the HealthBD application frontend.

## Component Structure

### JavaScript/Component Pattern

Our components follow a consistent class-based pattern for better organization and maintainability:

```javascript
/**
 * ComponentName Component
 *
 * Brief description of the component purpose.
 *
 * Usage examples in a code block to show implementation.
 */

class ComponentName {
  constructor() {
    // Define base classes and default values
    this.baseClasses = "...";
  }

  /**
   * Renders a component with the specified options
   * @param {Object} options - Component options with JSDoc for each param
   * @returns {string} HTML markup for the component
   */
  render(options = {}) {
    // Implementation logic
    return `
      <!-- HTML structure -->
    `;
  }

  /**
   * Helper/shortcut methods for common variants
   */
  variantName(options = {}) {
    return this.render({ variant: "name", ...options });
  }
}

// Export the component instance
export default new ComponentName();
```

### File Organization

- Place components in appropriate subdirectories based on their type
- Maintain a flat structure where possible to avoid deep nesting
- Follow a consistent naming convention for all files

```
design-system/
├── components/
│   ├── buttons/
│   │   └── Button.js
│   ├── forms/
│   │   ├── Input.js
│   │   ├── Select.js
│   │   └── Form.js
│   ├── layouts/
│   │   ├── Container.js
│   │   ├── Grid.js
│   │   └── PageLayout.js
│   ├── navigation/
│   │   ├── Navbar.js
│   │   └── Sidebar.js
│   ├── Alert.js
│   ├── Card.js
│   └── Table.js
└── docs/
    ├── design-tokens.md
    ├── layout-patterns.md
    └── coding-standards.md
```

## Naming Conventions

### CSS Class Naming

- Use Tailwind CSS utility classes primarily
- Follow a consistent pattern for custom CSS classes
- Avoid deep CSS nesting

```javascript
// ✅ DO: Compose Tailwind utility classes
const buttonClasses = [
  "inline-flex",
  "items-center",
  "px-4",
  "py-2",
  "border",
  "rounded-lg",
  variant === "primary" ? "bg-cyan-600 text-white" : "bg-white text-gray-700",
  disabled ? "opacity-50 cursor-not-allowed" : "",
  className,
]
  .filter(Boolean)
  .join(" ");

// ❌ DON'T: Create custom classes that replicate Tailwind utilities
const buttonClasses = "custom-button primary-button";
```

### Component Naming

- Use PascalCase for component class names (e.g., `Button`, `NavBar`)
- Use camelCase for methods and properties (e.g., `render()`, `baseClasses`)
- Use descriptive names that clearly indicate the component's purpose

### Method Naming

- Use descriptive method names that clearly indicate the function's purpose
- Prefix boolean methods with verbs like `is`, `has`, or `should`
- Use consistent naming patterns across similar components

## Documentation Standards

### Component Documentation

Every component should include:

1. A class-level JSDoc comment with:

   - Component name
   - Brief description
   - Usage examples

2. Method-level JSDoc comments with:
   - Brief description
   - Parameters with types and descriptions
   - Return value with type and description

````javascript
/**
 * Button Component
 *
 * A reusable button component with multiple variants and sizes.
 *
 * Usage:
 * ```
 * <Button variant="primary" size="md">Click Me</Button>
 * ```
 */

/**
 * Renders a button with the specified options
 * @param {Object} options - Button options
 * @param {string} options.variant - Button variant (primary, secondary, outline, link)
 * @param {string} options.size - Button size (sm, md, lg)
 * @param {boolean} options.disabled - Whether the button is disabled
 * @returns {string} HTML markup for the button
 */
````

### Code Comments

- Use comments to explain "why" not "what"
- Keep comments concise and relevant
- Use JSDoc comments for public methods
- Add comments for complex logic sections

## CSS/Tailwind Patterns

### Layout Approach

- Follow a consistent approach to page layout
- Use the layout components (PageLayout, Container, Grid) for structure
- Apply a mobile-first responsive design approach

### Responsive Design

- Start with mobile styles as the base
- Add responsive styles for larger screens using Tailwind breakpoints
- Use the following breakpoints consistently:
  - `sm`: 640px and up
  - `md`: 768px and up
  - `lg`: 1024px and up
  - `xl`: 1280px and up
  - `2xl`: 1536px and up

```javascript
// Example of responsive classes
const responsiveClasses = [
  "grid", // Base - single column for mobile
  "grid-cols-1", // Mobile (default) - 1 column
  "sm:grid-cols-2", // Small screens - 2 columns
  "md:grid-cols-3", // Medium screens - 3 columns
  "lg:grid-cols-4", // Large screens - 4 columns
].join(" ");
```

### Consistent Spacing

- Use Tailwind's default spacing scale
- Apply consistent spacing within and between components
- Use the same spacing scale across all components

```javascript
// ✅ DO: Use consistent spacing scale
const cardClasses = "p-4 sm:p-6 lg:p-8 space-y-4";

// ❌ DON'T: Use inconsistent or custom spacing
const cardClasses = "p-4 sm:p-7 lg:p-9 space-y-5";
```

## Accessibility Standards

### Base Requirements

All components must meet the following accessibility requirements:

1. **Proper Semantic HTML**: Use correct HTML elements for their intended purpose
2. **Keyboard Navigation**: All interactive elements must be keyboard accessible
3. **ARIA Attributes**: Use appropriate ARIA attributes when necessary
4. **Focus Management**: Ensure proper focus management for interactive components
5. **Color Contrast**: Maintain sufficient color contrast (4.5:1 for normal text)
6. **Screen Reader Support**: Include appropriate screen reader text

### Example: Accessible Button

```javascript
// Accessible button example
return `
  <button
    type="${type}"
    class="${buttonClasses}"
    ${disabled ? "disabled" : ""}
    ${ariaLabel ? `aria-label="${ariaLabel}"` : ""}
    ${ariaExpanded ? `aria-expanded="${ariaExpanded}"` : ""}
  >
    ${
      iconLeft ? `<span class="mr-2" aria-hidden="true">${iconLeft}</span>` : ""
    }
    <span>${text}</span>
    ${
      iconRight
        ? `<span class="ml-2" aria-hidden="true">${iconRight}</span>`
        : ""
    }
  </button>
`;
```

## Performance Considerations

### Code Efficiency

- Avoid unnecessary computations or string manipulations
- Use efficient DOM operations
- Filter empty values when joining class arrays

```javascript
// ✅ DO: Filter empty values
const classes = [
  baseClass,
  variant && variantClasses[variant],
  disabled && "opacity-50",
  className,
]
  .filter(Boolean)
  .join(" ");

// ❌ DON'T: Include empty values
const classes = [
  baseClass,
  variantClasses[variant] || "",
  disabled ? "opacity-50" : "",
  className || "",
].join(" ");
```

### Best Practices

1. **Minimize DOM Operations**: Build HTML strings efficiently
2. **Avoid Complex Rendering Logic**: Keep render methods simple and focused
3. **Use Proper Method Abstraction**: Break complex logic into helper methods
4. **Optimize Class Manipulations**: Use efficient class handling techniques

## Testing Considerations

- Design components with testability in mind
- Create pure render functions that rely only on their inputs
- Avoid side effects in component rendering
- Consider adding validation checks for required parameters

## Example: Well-Structured Component

````javascript
/**
 * Button Component
 *
 * A reusable button component with multiple variants and sizes.
 *
 * Usage:
 * ```
 * Button.render({
 *   variant: "primary",
 *   size: "md",
 *   text: "Click Me",
 *   onClick: "handleClick()"
 * });
 * ```
 */

class Button {
  constructor() {
    this.baseClasses =
      "inline-flex items-center justify-center font-medium transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-offset-2";

    this.variantClasses = {
      primary:
        "bg-cyan-600 hover:bg-cyan-700 text-white border border-transparent rounded-lg shadow-sm focus:ring-cyan-500",
      secondary:
        "bg-white hover:bg-gray-50 text-gray-700 border border-gray-300 rounded-lg shadow-sm focus:ring-cyan-500",
      outline:
        "bg-transparent hover:bg-cyan-50 text-cyan-600 border border-cyan-600 rounded-lg focus:ring-cyan-500",
      link: "bg-transparent text-cyan-600 hover:text-cyan-500 border-0 shadow-none focus:ring-transparent",
    };

    this.sizeClasses = {
      sm: "px-3 py-1.5 text-xs",
      md: "px-4 py-2.5 text-sm",
      lg: "px-5 py-3 text-base",
    };
  }

  /**
   * Renders a button with the specified options
   * @param {Object} options - Button options
   * @param {string} options.variant - Button variant (primary, secondary, outline, link)
   * @param {string} options.size - Button size (sm, md, lg)
   * @param {boolean} options.disabled - Whether the button is disabled
   * @param {string} options.className - Additional classes to apply
   * @param {string} options.type - Button type (button, submit, reset)
   * @param {boolean} options.fullWidth - Whether the button should take up full width
   * @param {string} options.text - Button text
   * @param {string} options.iconLeft - Icon to show before text
   * @param {string} options.iconRight - Icon to show after text
   * @returns {string} HTML markup for the button
   */
  render({
    variant = "primary",
    size = "md",
    disabled = false,
    className = "",
    type = "button",
    fullWidth = false,
    text = "",
    iconLeft = "",
    iconRight = "",
  }) {
    // Combine all classes
    const buttonClasses = [
      this.baseClasses,
      this.variantClasses[variant] || this.variantClasses.primary,
      this.sizeClasses[size] || this.sizeClasses.md,
      fullWidth ? "w-full" : "",
      disabled ? "opacity-50 cursor-not-allowed" : "",
      className,
    ]
      .filter(Boolean)
      .join(" ");

    // Create icon elements if needed
    const leftIconHtml = iconLeft
      ? `<span class="mr-2" aria-hidden="true">${iconLeft}</span>`
      : "";
    const rightIconHtml = iconRight
      ? `<span class="ml-2" aria-hidden="true">${iconRight}</span>`
      : "";

    // Build the button HTML
    return `
      <button
        type="${type}"
        class="${buttonClasses}"
        ${disabled ? "disabled" : ""}
      >
        ${leftIconHtml}
        ${text}
        ${rightIconHtml}
      </button>
    `;
  }

  // Helper methods for common variants
  primary(options = {}) {
    return this.render({ variant: "primary", ...options });
  }

  secondary(options = {}) {
    return this.render({ variant: "secondary", ...options });
  }

  outline(options = {}) {
    return this.render({ variant: "outline", ...options });
  }

  link(options = {}) {
    return this.render({ variant: "link", ...options });
  }
}

// Export the Button class
export default new Button();
````

This component demonstrates several best practices:

- Clear documentation with examples
- Well-structured parameter handling with defaults
- Clean organization of CSS class variants
- Proper filtering of class values
- Helper methods for common use cases
- Consistent naming conventions
