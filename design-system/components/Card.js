/**
 * Card Component
 *
 * A reusable card component for displaying content in a contained, elevated container.
 *
 * Usage:
 * ```
 * // Basic card
 * Card.render({
 *   title: 'Card Title',
 *   content: '<p>This is the card content.</p>'
 * });
 *
 * // Card with header and footer
 * Card.render({
 *   header: '<div class="flex justify-between"><h2>Card Title</h2><button>⋮</button></div>',
 *   content: '<p>This is the card content.</p>',
 *   footer: '<button class="btn-primary">Submit</button>'
 * });
 *
 * // Card with custom padding and styles
 * Card.render({
 *   content: '<p>Custom card with different padding and no shadow.</p>',
 *   padding: 'p-4',
 *   shadow: false,
 *   className: 'border-dashed'
 * });
 * ```
 */

class Card {
  constructor() {
    this.baseClasses = "bg-white rounded-xl border border-gray-200";
    this.defaultPadding = "p-8";
  }

  /**
   * Renders a card with the specified options
   * @param {Object} options - Card options
   * @param {string} options.title - Card title (shorthand for simple header)
   * @param {string} options.header - Custom header HTML
   * @param {string} options.content - Card content HTML
   * @param {string} options.footer - Card footer HTML
   * @param {boolean} options.shadow - Whether to apply shadow (default: true)
   * @param {string} options.padding - Padding to apply to content (default: 'p-8')
   * @param {boolean} options.hover - Whether to apply hover effect
   * @param {string} options.className - Additional classes to apply
   * @returns {string} HTML markup for the card
   */
  render({
    title = "",
    header = "",
    content = "",
    footer = "",
    shadow = true,
    padding = this.defaultPadding,
    hover = false,
    className = "",
  }) {
    // If title is provided but no header, create a simple header with the title
    if (title && !header) {
      header = `<h3 class="text-lg font-medium text-gray-900">${title}</h3>`;
    }

    // Combine all classes
    const cardClasses = [
      this.baseClasses,
      shadow ? "shadow-lg" : "",
      hover ? "hover:shadow-xl transition-shadow duration-300" : "",
      className,
    ]
      .filter(Boolean)
      .join(" ");

    // Create HTML for the header if provided
    const headerHtml = header
      ? `<div class="border-b border-gray-200 pb-4 ${padding}">${header}</div>`
      : "";

    // Create HTML for the content
    const contentHtml = content
      ? `<div class="${padding} ${header ? "pt-5" : ""} ${
          footer ? "pb-4" : ""
        }">${content}</div>`
      : "";

    // Create HTML for the footer if provided
    const footerHtml = footer
      ? `<div class="border-t border-gray-200 pt-4 ${padding}">${footer}</div>`
      : "";

    // Build the complete card HTML
    return `
      <div class="${cardClasses}">
        ${headerHtml}
        ${contentHtml}
        ${footerHtml}
      </div>
    `;
  }

  /**
   * Creates a basic card with title and content
   * @param {string} title - Card title
   * @param {string} content - Card content
   * @returns {string} HTML markup for a basic card
   */
  basic(title, content) {
    return this.render({ title, content });
  }

  /**
   * Creates an interactive hover card
   * @param {Object} options - Card options
   * @returns {string} HTML markup for an interactive card
   */
  interactive(options) {
    return this.render({ hover: true, ...options });
  }

  /**
   * Creates a compact card with smaller padding
   * @param {Object} options - Card options
   * @returns {string} HTML markup for a compact card
   */
  compact(options) {
    return this.render({
      padding: "p-4",
      ...options,
    });
  }

  /**
   * Creates a borderless card with only shadow
   * @param {Object} options - Card options
   * @returns {string} HTML markup for a borderless card
   */
  borderless(options) {
    const borderlessClasses = options.className
      ? `${options.className} border-0`
      : "border-0";

    return this.render({
      shadow: true,
      className: borderlessClasses,
      ...options,
    });
  }
}

// Export the Card class
export default new Card();
