/**
 * PageLayout Component
 *
 * A reusable layout component that provides consistent page structure.
 *
 * Usage:
 * ```
 * // Basic page layout with header and content
 * PageLayout.render({
 *   header: Navbar.render({ ... }),
 *   content: `<div class="p-8">Page content goes here</div>`
 * });
 *
 * // Dashboard layout with sidebar, header, and footer
 * PageLayout.render({
 *   type: 'dashboard',
 *   header: Navbar.render({ ... }),
 *   sidebar: Sidebar.render({ ... }),
 *   content: `<div class="p-8">Dashboard content</div>`,
 *   footer: `<footer class="p-4 bg-gray-50 border-t">Footer content</footer>`
 * });
 * ```
 */

class PageLayout {
  constructor() {
    this.baseClasses = "min-h-screen bg-gray-50";
  }

  /**
   * Renders a page layout with the specified options
   * @param {Object} options - Layout options
   * @param {string} options.type - Layout type (default, dashboard, auth)
   * @param {string} options.header - Header content
   * @param {string} options.sidebar - Sidebar content
   * @param {string} options.content - Main content
   * @param {string} options.footer - Footer content
   * @param {boolean} options.fixedHeader - Whether the header should be fixed at the top
   * @param {string} options.className - Additional classes to apply
   * @returns {string} HTML markup for the layout
   */
  render({
    type = "default",
    header = "",
    sidebar = "",
    content = "",
    footer = "",
    fixedHeader = false,
    className = "",
  }) {
    // Combine layout classes
    const layoutClasses = [this.baseClasses, className]
      .filter(Boolean)
      .join(" ");

    // Based on the layout type, determine the structure
    let layoutHtml = "";

    switch (type) {
      case "dashboard":
        // Dashboard layout with sidebar, fixed header and content area
        layoutHtml = `
          <div class="${layoutClasses}">
            ${
              fixedHeader
                ? `<div class="fixed top-0 left-0 right-0 z-10">${header}</div>`
                : header
            }
            <div class="flex ${fixedHeader ? "pt-16" : ""}">
              ${sidebar ? sidebar : ""}
              <main class="flex-1 overflow-auto ${sidebar ? "md:ml-64" : ""}">
                <div class="py-6">
                  ${content}
                </div>
              </main>
            </div>
            ${footer ? footer : ""}
          </div>
        `;
        break;

      case "auth":
        // Authentication layout with centered content and optional header/footer
        layoutHtml = `
          <div class="${layoutClasses} flex flex-col justify-center py-12 sm:px-6 lg:px-8">
            ${header ? `<div class="mb-8">${header}</div>` : ""}
            <div class="sm:mx-auto sm:w-full sm:max-w-md">
              <div class="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
                ${content}
              </div>
            </div>
            ${footer ? `<div class="mt-8">${footer}</div>` : ""}
          </div>
        `;
        break;

      default:
        // Default layout with optional header, main content and footer
        layoutHtml = `
          <div class="${layoutClasses} flex flex-col">
            ${
              fixedHeader
                ? `<div class="fixed top-0 left-0 right-0 z-10">${header}</div>`
                : header
            }
            <main class="flex-1 ${fixedHeader ? "pt-16" : ""}">
              ${content}
            </main>
            ${footer ? footer : ""}
          </div>
        `;
        break;
    }

    return layoutHtml;
  }

  /**
   * Creates a dashboard layout
   * @param {Object} options - Layout options
   * @returns {string} HTML markup for a dashboard layout
   */
  dashboard(options) {
    return this.render({ type: "dashboard", ...options });
  }

  /**
   * Creates an authentication layout
   * @param {Object} options - Layout options
   * @returns {string} HTML markup for an authentication layout
   */
  auth(options) {
    return this.render({ type: "auth", ...options });
  }
}

// Export the PageLayout class
export default new PageLayout();
