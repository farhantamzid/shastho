/**
 * Button Component
 *
 * A reusable button component with multiple variants and sizes.
 *
 * Usage:
 * ```
 * <Button variant="primary" size="md" onClick={handleClick}>Click Me</Button>
 * <Button variant="secondary" size="sm">Secondary Button</Button>
 * <Button variant="outline" size="lg" disabled>Disabled Button</Button>
 * <Button variant="link">Link Button</Button>
 * ```
 */

class Button {
  constructor() {
    this.baseClasses =
      "flex items-center justify-center font-medium transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-offset-2";
  }

  /**
   * Renders a button with the specified variants and props
   * @param {Object} options - Button options
   * @param {string} options.variant - Button variant (primary, secondary, outline, link)
   * @param {string} options.size - Button size (sm, md, lg)
   * @param {boolean} options.disabled - Whether the button is disabled
   * @param {string} options.className - Additional classes to apply
   * @param {Function} options.onClick - Click handler function
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
    onClick = null,
    type = "button",
    fullWidth = false,
    text = "",
    iconLeft = "",
    iconRight = "",
  }) {
    // Determine variant-specific classes
    let variantClasses = "";
    let disabledClasses = "";

    if (disabled) {
      disabledClasses = "opacity-50 cursor-not-allowed";
    }

    switch (variant) {
      case "primary":
        variantClasses =
          "bg-cyan-600 hover:bg-cyan-700 text-white border border-transparent rounded-lg shadow-sm focus:ring-cyan-500";
        break;
      case "secondary":
        variantClasses =
          "bg-white hover:bg-gray-50 text-gray-700 border border-gray-300 rounded-lg shadow-sm focus:ring-cyan-500";
        break;
      case "outline":
        variantClasses =
          "bg-transparent hover:bg-cyan-50 text-cyan-600 border border-cyan-600 rounded-lg focus:ring-cyan-500";
        break;
      case "link":
        variantClasses =
          "bg-transparent text-cyan-600 hover:text-cyan-500 border-0 shadow-none focus:ring-transparent";
        break;
      default:
        variantClasses =
          "bg-cyan-600 hover:bg-cyan-700 text-white border border-transparent rounded-lg shadow-sm focus:ring-cyan-500";
    }

    // Determine size-specific classes
    let sizeClasses = "";
    switch (size) {
      case "sm":
        sizeClasses = "px-3 py-1.5 text-xs";
        break;
      case "md":
        sizeClasses = "px-4 py-2.5 text-sm";
        break;
      case "lg":
        sizeClasses = "px-5 py-3 text-base";
        break;
      default:
        sizeClasses = "px-4 py-2.5 text-sm";
    }

    // Handle full width
    const widthClass = fullWidth ? "w-full" : "";

    // Combine all classes
    const buttonClasses = [
      this.baseClasses,
      variantClasses,
      sizeClasses,
      widthClass,
      disabledClasses,
      className,
    ]
      .filter(Boolean)
      .join(" ");

    // Create icon elements if needed
    const leftIconHtml = iconLeft
      ? `<span class="mr-2">${iconLeft}</span>`
      : "";
    const rightIconHtml = iconRight
      ? `<span class="ml-2">${iconRight}</span>`
      : "";

    // Build the button HTML
    return `
      <button
        type="${type}"
        class="${buttonClasses}"
        ${disabled ? "disabled" : ""}
        ${onClick ? `onclick="${onClick}"` : ""}
      >
        ${leftIconHtml}
        ${text}
        ${rightIconHtml}
      </button>
    `;
  }

  /**
   * Creates a primary button
   */
  primary(options = {}) {
    return this.render({ variant: "primary", ...options });
  }

  /**
   * Creates a secondary button
   */
  secondary(options = {}) {
    return this.render({ variant: "secondary", ...options });
  }

  /**
   * Creates an outline button
   */
  outline(options = {}) {
    return this.render({ variant: "outline", ...options });
  }

  /**
   * Creates a link button
   */
  link(options = {}) {
    return this.render({ variant: "link", ...options });
  }
}

// Export the Button class
export default new Button();
