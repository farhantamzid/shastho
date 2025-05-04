/**
 * Sidebar Component
 *
 * A reusable sidebar navigation component for dashboard layouts.
 *
 * Usage:
 * ```
 * // Basic sidebar
 * Sidebar.render({
 *   logo: '<img src="/images/logo.svg" alt="Logo" class="h-8 w-auto">',
 *   items: [
 *     {
 *       text: 'Dashboard',
 *       href: '/dashboard',
 *       icon: '<i data-lucide="home" class="h-5 w-5"></i>',
 *       active: true
 *     },
 *     {
 *       text: 'Appointments',
 *       href: '/appointments',
 *       icon: '<i data-lucide="calendar" class="h-5 w-5"></i>'
 *     },
 *     {
 *       text: 'Patients',
 *       href: '/patients',
 *       icon: '<i data-lucide="users" class="h-5 w-5"></i>'
 *     }
 *   ],
 *   footerItems: [
 *     {
 *       text: 'Settings',
 *       href: '/settings',
 *       icon: '<i data-lucide="settings" class="h-5 w-5"></i>'
 *     },
 *     {
 *       text: 'Help',
 *       href: '/help',
 *       icon: '<i data-lucide="help-circle" class="h-5 w-5"></i>'
 *     }
 *   ],
 *   userInfo: {
 *     name: 'Dr. Jane Smith',
 *     role: 'Physician',
 *     avatar: '<img src="/images/avatar.jpg" alt="Avatar" class="h-8 w-8 rounded-full">',
 *     href: '/profile'
 *   }
 * });
 * ```
 */

class Sidebar {
  constructor() {
    this.baseClasses = "flex flex-col h-screen";
    this.sidebarClasses = "w-64 bg-white border-r border-gray-200";
    this.mobileSidebarClasses = "fixed inset-0 z-40 flex md:hidden";
    this.mobileOverlayClasses = "fixed inset-0 bg-gray-600 bg-opacity-75";
  }

  /**
   * Renders a sidebar with the specified options
   * @param {Object} options - Sidebar options
   * @param {string} options.logo - Logo HTML content
   * @param {Array} options.items - Navigation items for the main section
   * @param {Array} options.footerItems - Navigation items for the footer section
   * @param {Object} options.userInfo - User information for the user profile section
   * @param {boolean} options.collapsible - Whether the sidebar can be collapsed
   * @param {string} options.className - Additional classes to apply
   * @returns {string} HTML markup for the sidebar
   */
  render({
    logo = "",
    items = [],
    footerItems = [],
    userInfo = null,
    collapsible = true,
    className = "",
  }) {
    // Combine sidebar classes
    const sidebarClasses = [this.sidebarClasses, className]
      .filter(Boolean)
      .join(" ");

    // Generate main navigation items
    const navigationItemsHtml = items
      .map(
        (item) => `
        <a
          href="${item.href || "#"}"
          class="${
            item.active
              ? "bg-cyan-50 text-cyan-700"
              : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
          } group flex items-center px-4 py-3 text-sm font-medium rounded-md"
        >
          ${
            item.icon
              ? `<span class="${
                  item.active
                    ? "text-cyan-600"
                    : "text-gray-400 group-hover:text-gray-500"
                } mr-3">${item.icon}</span>`
              : ""
          }
          ${item.text}
        </a>
      `
      )
      .join("");

    // Generate footer navigation items
    const footerItemsHtml = footerItems
      .map(
        (item) => `
        <a
          href="${item.href || "#"}"
          class="${
            item.active
              ? "bg-cyan-50 text-cyan-700"
              : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
          } group flex items-center px-4 py-3 text-sm font-medium rounded-md"
        >
          ${
            item.icon
              ? `<span class="${
                  item.active
                    ? "text-cyan-600"
                    : "text-gray-400 group-hover:text-gray-500"
                } mr-3">${item.icon}</span>`
              : ""
          }
          ${item.text}
        </a>
      `
      )
      .join("");

    // Generate user profile section
    const userInfoHtml = userInfo
      ? `
        <a href="${
          userInfo.href || "#"
        }" class="flex items-center px-4 py-3 border-t border-gray-200">
          <div class="flex-shrink-0">
            ${userInfo.avatar || ""}
          </div>
          <div class="ml-3">
            <p class="text-sm font-medium text-gray-900">${
              userInfo.name || ""
            }</p>
            <p class="text-xs font-medium text-gray-500">${
              userInfo.role || ""
            }</p>
          </div>
        </a>
      `
      : "";

    // Generate toggle button for collapsible sidebar
    const toggleButtonHtml = collapsible
      ? `
        <button
          type="button"
          class="md:hidden absolute top-4 right-4 text-gray-500 hover:text-gray-600"
          id="sidebar-toggle"
          onclick="document.getElementById('sidebar').classList.toggle('-translate-x-full'); document.getElementById('sidebar-overlay').classList.toggle('hidden');"
        >
          <span class="sr-only">Toggle sidebar</span>
          <i data-lucide="x" class="h-6 w-6"></i>
        </button>
      `
      : "";

    // Build the complete sidebar HTML
    return `
      <!-- Desktop Sidebar -->
      <div class="${sidebarClasses} hidden md:flex md:flex-col">
        <!-- Logo -->
        <div class="flex-shrink-0 flex items-center h-16 px-4">
          ${logo}
        </div>

        <!-- Main Navigation -->
        <div class="flex-grow flex flex-col overflow-y-auto">
          <nav class="flex-1 px-2 py-4 space-y-1">
            ${navigationItemsHtml}
          </nav>

          <!-- Footer Navigation -->
          ${
            footerItems.length
              ? `
                <div class="px-2 py-4 space-y-1">
                  ${footerItemsHtml}
                </div>
              `
              : ""
          }

          <!-- User Info -->
          ${userInfoHtml}
        </div>
      </div>

      <!-- Mobile Sidebar -->
      <div class="${this.mobileSidebarClasses}" aria-modal="true">
        <!-- Overlay -->
        <div
          id="sidebar-overlay"
          class="${this.mobileOverlayClasses} hidden"
          aria-hidden="true"
          onclick="document.getElementById('sidebar').classList.add('-translate-x-full'); document.getElementById('sidebar-overlay').classList.add('hidden');"
        ></div>

        <!-- Sidebar Panel -->
        <div
          id="sidebar"
          class="${sidebarClasses} -translate-x-full transition-transform ease-in-out duration-300"
        >
          ${toggleButtonHtml}

          <!-- Logo -->
          <div class="flex-shrink-0 flex items-center h-16 px-4">
            ${logo}
          </div>

          <!-- Main Navigation -->
          <div class="flex-grow flex flex-col overflow-y-auto">
            <nav class="flex-1 px-2 py-4 space-y-1">
              ${navigationItemsHtml}
            </nav>

            <!-- Footer Navigation -->
            ${
              footerItems.length
                ? `
                  <div class="px-2 py-4 space-y-1">
                    ${footerItemsHtml}
                  </div>
                `
                : ""
            }

            <!-- User Info -->
            ${userInfoHtml}
          </div>
        </div>
      </div>

      <!-- Mobile Toggle Button (Only visible on mobile) -->
      <div class="md:hidden fixed bottom-4 right-4 z-30">
        <button
          type="button"
          class="bg-cyan-600 text-white rounded-full p-3 shadow-lg hover:bg-cyan-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-cyan-500"
          onclick="document.getElementById('sidebar').classList.remove('-translate-x-full'); document.getElementById('sidebar-overlay').classList.remove('hidden');"
        >
          <i data-lucide="menu" class="h-6 w-6"></i>
        </button>
      </div>
    `;
  }
}

// Export the Sidebar class
export default new Sidebar();
