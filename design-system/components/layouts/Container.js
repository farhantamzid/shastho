/**
 * Container Component
 *
 * A reusable container component that provides consistent width constraints and padding.
 *
 * Usage:
 * ```
 * // Default container
 * Container.render({
 *   content: `<p>Content here will be constrained to a reasonable max-width with responsive padding.</p>`
 * });
 *
 * // Narrow container
 * Container.render({
 *   size: 'narrow',
 *   content: `<p>Content in a narrow container.</p>`
 * });
 *
 * // Full-width container
 * Container.render({
 *   size: 'full',
 *   content: `<p>Content in a full-width container with padding.</p>`
 * });
 * ```
 */

class Container {
  constructor() {
    this.baseClasses = "mx-auto px-4 sm:px-6 lg:px-8";

    // Define size-specific max-width classes
    this.sizeClasses = {
      xs: "max-w-xs", // 20rem (320px)
      sm: "max-w-sm", // 24rem (384px)
      md: "max-w-md", // 28rem (448px)
      lg: "max-w-lg", // 32rem (512px)
      xl: "max-w-xl", // 36rem (576px)
      "2xl": "max-w-2xl", // 42rem (672px)
      "3xl": "max-w-3xl", // 48rem (768px)
      "4xl": "max-w-4xl", // 56rem (896px)
      "5xl": "max-w-5xl", // 64rem (1024px)
      "6xl": "max-w-6xl", // 72rem (1152px)
      "7xl": "max-w-7xl", // 80rem (1280px)
      narrow: "max-w-3xl", // Alias for max-w-3xl
      default: "max-w-7xl", // Standard size
      wide: "max-w-screen-2xl", // Wider
      full: "", // No max-width constraint
    };
  }

  /**
   * Renders a container with the specified options
   * @param {Object} options - Container options
   * @param {string} options.size - Container size (xs, sm, md, lg, xl, 2xl, 3xl, 4xl, 5xl, 6xl, 7xl, narrow, default, wide, full)
   * @param {string} options.content - Container content
   * @param {string} options.padding - Custom padding classes (overrides defaults)
   * @param {boolean} options.centered - Whether to center the text content
   * @param {string} options.className - Additional classes to apply
   * @returns {string} HTML markup for the container
   */
  render({
    size = "default",
    content = "",
    padding = "",
    centered = false,
    className = "",
  }) {
    // Get the appropriate max-width class based on size
    const sizeClass = this.sizeClasses[size] || this.sizeClasses.default;

    // Combine container classes
    const containerClasses = [
      this.baseClasses,
      sizeClass,
      padding ? padding : "", // Use custom padding if provided
      centered ? "text-center" : "",
      className,
    ]
      .filter(Boolean)
      .join(" ");

    // Build the container HTML
    return `
      <div class="${containerClasses}">
        ${content}
      </div>
    `;
  }

  /**
   * Creates a narrow container
   * @param {Object} options - Container options
   * @returns {string} HTML markup for a narrow container
   */
  narrow(options) {
    return this.render({ size: "narrow", ...options });
  }

  /**
   * Creates a wide container
   * @param {Object} options - Container options
   * @returns {string} HTML markup for a wide container
   */
  wide(options) {
    return this.render({ size: "wide", ...options });
  }

  /**
   * Creates a full-width container (with padding)
   * @param {Object} options - Container options
   * @returns {string} HTML markup for a full-width container
   */
  full(options) {
    return this.render({ size: "full", ...options });
  }

  /**
   * Creates a centered container (centered text)
   * @param {Object} options - Container options
   * @returns {string} HTML markup for a centered container
   */
  centered(options) {
    return this.render({ centered: true, ...options });
  }
}

// Export the Container class
export default new Container();
