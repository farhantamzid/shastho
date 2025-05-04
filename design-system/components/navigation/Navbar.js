/**
 * Navbar Component
 *
 * A reusable navigation bar component with responsive behavior.
 *
 * Usage:
 * ```
 * // Basic navbar
 * Navbar.render({
 *   logo: '<img src="/images/logo.svg" alt="Logo" class="h-8 w-auto">',
 *   items: [
 *     { text: 'Home', href: '/', active: true },
 *     { text: 'About', href: '/about' },
 *     { text: 'Services', href: '/services' },
 *     { text: 'Contact', href: '/contact' }
 *   ]
 * });
 *
 * // Navbar with right-aligned items and user dropdown
 * Navbar.render({
 *   logo: '<img src="/images/logo.svg" alt="Logo" class="h-8 w-auto">',
 *   items: [
 *     { text: 'Home', href: '/', active: true },
 *     { text: 'Dashboard', href: '/dashboard' }
 *   ],
 *   rightItems: [
 *     {
 *       type: 'dropdown',
 *       text: 'John Doe',
 *       icon: '<img src="/images/avatar.jpg" alt="Avatar" class="h-8 w-8 rounded-full">',
 *       items: [
 *         { text: 'Your Profile', href: '/profile' },
 *         { text: 'Settings', href: '/settings' },
 *         { text: 'Sign out', href: '/logout' }
 *       ]
 *     }
 *   ]
 * });
 * ```
 */

class Navbar {
  constructor() {
    this.baseClasses = "bg-white shadow";
    this.containerClasses = "px-4 sm:px-6 lg:px-8";
    this.flexClasses = "flex justify-between h-16";
    this.mobileMenuClasses = "sm:hidden";
    this.desktopMenuClasses = "hidden sm:ml-6 sm:flex sm:space-x-8";
  }

  /**
   * Renders a navbar with the specified options
   * @param {Object} options - Navbar options
   * @param {string} options.logo - Logo HTML content
   * @param {Array} options.items - Navigation items for the left side
   * @param {Array} options.rightItems - Navigation items for the right side
   * @param {boolean} options.sticky - Whether the navbar should be sticky
   * @param {string} options.className - Additional classes to apply
   * @returns {string} HTML markup for the navbar
   */
  render({
    logo = "",
    items = [],
    rightItems = [],
    sticky = false,
    className = "",
  }) {
    // Combine navbar classes
    const navbarClasses = [
      this.baseClasses,
      sticky ? "sticky top-0 z-30" : "",
      className,
    ]
      .filter(Boolean)
      .join(" ");

    // Generate desktop menu items
    const desktopItemsHtml = items
      .map(
        (item) => `
        <a
          href="${item.href || "#"}"
          class="${
            item.active
              ? "border-cyan-500 text-gray-900 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
              : "border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
          }"
        >
          ${item.text}
        </a>
      `
      )
      .join("");

    // Generate desktop right-aligned items
    const desktopRightItemsHtml = rightItems
      .map((item) => {
        if (item.type === "dropdown") {
          const dropdownItemsHtml = item.items
            .map(
              (dropdownItem) => `
              <a
                href="${dropdownItem.href || "#"}"
                class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                role="menuitem"
              >
                ${dropdownItem.text}
              </a>
            `
            )
            .join("");

          return `
            <div class="ml-3 relative">
              <div>
                <button
                  type="button"
                  class="flex text-sm rounded-full focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-cyan-500"
                  id="user-menu-button"
                  aria-expanded="false"
                  aria-haspopup="true"
                  onclick="document.getElementById('user-dropdown').classList.toggle('hidden')"
                >
                  <span class="sr-only">Open user menu</span>
                  ${item.icon || ""}
                </button>
              </div>
              <div
                id="user-dropdown"
                class="hidden origin-top-right absolute right-0 mt-2 w-48 rounded-md shadow-lg py-1 bg-white ring-1 ring-black ring-opacity-5 focus:outline-none"
                role="menu"
                aria-orientation="vertical"
                aria-labelledby="user-menu-button"
                tabindex="-1"
              >
                ${dropdownItemsHtml}
              </div>
            </div>
          `;
        } else {
          return `
            <a
              href="${item.href || "#"}"
              class="${
                item.active
                  ? "bg-cyan-50 text-cyan-700"
                  : "text-gray-500 hover:text-gray-700"
              } px-3 py-2 rounded-md text-sm font-medium"
            >
              ${item.text}
            </a>
          `;
        }
      })
      .join("");

    // Generate mobile menu items
    const mobileItemsHtml = items
      .map(
        (item) => `
        <a
          href="${item.href || "#"}"
          class="${
            item.active
              ? "bg-cyan-50 border-cyan-500 text-cyan-700 block pl-3 pr-4 py-2 border-l-4 text-base font-medium"
              : "border-transparent text-gray-500 hover:bg-gray-50 hover:border-gray-300 hover:text-gray-700 block pl-3 pr-4 py-2 border-l-4 text-base font-medium"
          }"
        >
          ${item.text}
        </a>
      `
      )
      .join("");

    // Generate mobile right-aligned items (excluding dropdowns)
    const mobileRightItemsHtml = rightItems
      .filter((item) => item.type !== "dropdown")
      .map(
        (item) => `
        <a
          href="${item.href || "#"}"
          class="${
            item.active
              ? "bg-cyan-50 border-cyan-500 text-cyan-700 block pl-3 pr-4 py-2 border-l-4 text-base font-medium"
              : "border-transparent text-gray-500 hover:bg-gray-50 hover:border-gray-300 hover:text-gray-700 block pl-3 pr-4 py-2 border-l-4 text-base font-medium"
          }"
        >
          ${item.text}
        </a>
      `
      )
      .join("");

    // Add dropdown items to mobile menu
    const mobileDropdownItemsHtml = rightItems
      .filter((item) => item.type === "dropdown")
      .flatMap((item) =>
        item.items.map(
          (dropdownItem) => `
          <a
            href="${dropdownItem.href || "#"}"
            class="border-transparent text-gray-500 hover:bg-gray-50 hover:border-gray-300 hover:text-gray-700 block pl-3 pr-4 py-2 border-l-4 text-base font-medium"
          >
            ${dropdownItem.text}
          </a>
        `
        )
      )
      .join("");

    // Build the complete navbar HTML
    return `
      <nav class="${navbarClasses}">
        <div class="${this.containerClasses}">
          <div class="${this.flexClasses}">
            <!-- Left side: Logo and navigation -->
            <div class="flex">
              <!-- Logo -->
              <div class="flex-shrink-0 flex items-center">
                ${logo}
              </div>

              <!-- Desktop Navigation Items (Left) -->
              <div class="${this.desktopMenuClasses}">
                ${desktopItemsHtml}
              </div>
            </div>

            <!-- Right side: Additional items -->
            <div class="flex items-center">
              ${desktopRightItemsHtml}

              <!-- Mobile menu button -->
              <div class="flex items-center sm:hidden ml-4">
                <button
                  type="button"
                  class="inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-cyan-500"
                  aria-controls="mobile-menu"
                  aria-expanded="false"
                  onclick="document.getElementById('mobile-menu').classList.toggle('hidden')"
                >
                  <span class="sr-only">Open main menu</span>
                  <i data-lucide="menu" class="h-6 w-6 block"></i>
                  <i data-lucide="x" class="h-6 w-6 hidden"></i>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Mobile menu -->
        <div class="${this.mobileMenuClasses} hidden" id="mobile-menu">
          <div class="pt-2 pb-3 space-y-1">
            ${mobileItemsHtml}
          </div>
          <div class="pt-4 pb-3 border-t border-gray-200">
            <div class="space-y-1">
              ${mobileRightItemsHtml}
              ${mobileDropdownItemsHtml}
            </div>
          </div>
        </div>
      </nav>
    `;
  }
}

// Export the Navbar class
export default new Navbar();
