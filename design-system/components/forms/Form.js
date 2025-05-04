/**
 * Form Component
 *
 * A reusable form component that can compose multiple form elements.
 *
 * Usage:
 * ```
 * // Basic form
 * Form.render({
 *   id: 'login-form',
 *   action: '/api/login',
 *   content: `
 *     ${Input.text({ name: 'email', label: 'Email Address', required: true })}
 *     ${Input.password({ name: 'password', label: 'Password', required: true })}
 *     ${Button.primary({ text: 'Sign In', type: 'submit', fullWidth: true })}
 *   `
 * });
 *
 * // Form with sections
 * Form.render({
 *   id: 'registration-form',
 *   method: 'POST',
 *   sections: [
 *     {
 *       title: 'Personal Information',
 *       content: `
 *         ${Input.text({ name: 'first_name', label: 'First Name', required: true })}
 *         ${Input.text({ name: 'last_name', label: 'Last Name', required: true })}
 *       `
 *     },
 *     {
 *       title: 'Account Details',
 *       content: `
 *         ${Input.email({ name: 'email', label: 'Email', required: true })}
 *         ${Input.password({ name: 'password', label: 'Password', required: true })}
 *       `
 *     }
 *   ],
 *   footer: `
 *     ${Button.primary({ text: 'Register', type: 'submit' })}
 *     ${Button.secondary({ text: 'Cancel', type: 'button' })}
 *   `
 * });
 * ```
 */

class Form {
  constructor() {
    this.baseClasses = "space-y-6";
  }

  /**
   * Renders a form with the specified options
   * @param {Object} options - Form options
   * @param {string} options.id - Form ID
   * @param {string} options.name - Form name
   * @param {string} options.action - Form action URL
   * @param {string} options.method - Form method (GET, POST)
   * @param {string} options.content - Form content HTML
   * @param {Array} options.sections - Form sections (title, content)
   * @param {string} options.footer - Form footer HTML (typically contains submit buttons)
   * @param {string} options.className - Additional classes to apply
   * @param {boolean} options.validateOnSubmit - Whether to add client-side validation
   * @returns {string} HTML markup for the form
   */
  render({
    id = "",
    name = "",
    action = "",
    method = "POST",
    content = "",
    sections = [],
    footer = "",
    className = "",
    validateOnSubmit = true,
  }) {
    // Combine form classes
    const formClasses = [this.baseClasses, className].filter(Boolean).join(" ");

    // Create form attributes
    const formAttributes = [
      id ? `id="${id}"` : "",
      name ? `name="${name}"` : "",
      action ? `action="${action}"` : "",
      `method="${method}"`,
      validateOnSubmit ? "" : "novalidate",
    ]
      .filter(Boolean)
      .join(" ");

    // Create HTML for sections if provided
    let sectionsHtml = "";
    if (sections && sections.length > 0) {
      sectionsHtml = sections
        .map(
          (section) => `
            <div class="space-y-5">
              ${
                section.title
                  ? `<h3 class="text-lg font-medium text-gray-900">${section.title}</h3>`
                  : ""
              }
              ${section.content || ""}
            </div>
          `
        )
        .join(`<div class="border-t border-gray-200 my-6"></div>`);
    }

    // Build the complete form HTML
    return `
      <form ${formAttributes} class="${formClasses}">
        ${content}
        ${sectionsHtml}
        ${
          footer
            ? `<div class="flex items-center justify-end space-x-4 pt-4">${footer}</div>`
            : ""
        }
      </form>
    `;
  }

  /**
   * Creates a login form with email/password fields
   * @param {Object} options - Additional options for the form
   * @returns {string} HTML markup for a login form
   */
  login(options = {}) {
    // Import dependencies - in a real implementation these would be actual imports
    const inputPlaceholder = `// This is a placeholder - in a real implementation, Input and Button would be imported`;

    return this.render({
      id: "login-form",
      action: options.action || "/api/login",
      content: `
        <!-- This is a template, in real usage you would use the actual components -->
        <div class="space-y-4">
          <!-- Email Input -->
          <div>
            <label for="email" class="block text-sm font-medium text-gray-700 mb-1">Email Address</label>
            <div class="relative">
              <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <i data-lucide="mail" class="h-4 w-4 text-gray-400"></i>
              </div>
              <input type="email" id="email" name="email" required class="appearance-none block w-full pl-10 pr-3 py-2.5 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-cyan-500 focus:border-cyan-500 sm:text-sm" placeholder="you@example.com">
            </div>
          </div>

          <!-- Password Input -->
          <div>
            <label for="password" class="block text-sm font-medium text-gray-700 mb-1">Password</label>
            <div class="relative">
              <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <i data-lucide="lock" class="h-4 w-4 text-gray-400"></i>
              </div>
              <input type="password" id="password" name="password" required class="appearance-none block w-full pl-10 pr-3 py-2.5 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-cyan-500 focus:border-cyan-500 sm:text-sm">
            </div>
          </div>

          <!-- Remember Me Checkbox -->
          <div class="flex items-center">
            <input id="remember_me" name="remember_me" type="checkbox" class="h-4 w-4 text-cyan-600 focus:ring-cyan-500 border-gray-300 rounded">
            <label for="remember_me" class="ml-2 block text-sm text-gray-700">Remember me</label>
          </div>
        </div>

        <!-- Submit Button -->
        <div class="mt-6">
          <button type="submit" class="w-full flex justify-center py-2.5 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-cyan-600 hover:bg-cyan-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-cyan-500">
            Sign in
          </button>
        </div>
      `,
      ...options,
    });
  }

  /**
   * Creates a registration form with common fields
   * @param {Object} options - Additional options for the form
   * @returns {string} HTML markup for a registration form
   */
  register(options = {}) {
    return this.render({
      id: "register-form",
      action: options.action || "/api/register",
      sections: [
        {
          title: "Personal Information",
          content: `
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <!-- First Name Input -->
              <div>
                <label for="first_name" class="block text-sm font-medium text-gray-700 mb-1">First Name</label>
                <input type="text" id="first_name" name="first_name" required class="appearance-none block w-full px-3 py-2.5 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-cyan-500 focus:border-cyan-500 sm:text-sm">
              </div>

              <!-- Last Name Input -->
              <div>
                <label for="last_name" class="block text-sm font-medium text-gray-700 mb-1">Last Name</label>
                <input type="text" id="last_name" name="last_name" required class="appearance-none block w-full px-3 py-2.5 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-cyan-500 focus:border-cyan-500 sm:text-sm">
              </div>
            </div>
          `,
        },
        {
          title: "Account Details",
          content: `
            <div class="space-y-6">
              <!-- Email Input -->
              <div>
                <label for="email" class="block text-sm font-medium text-gray-700 mb-1">Email Address</label>
                <div class="relative">
                  <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <i data-lucide="mail" class="h-4 w-4 text-gray-400"></i>
                  </div>
                  <input type="email" id="email" name="email" required class="appearance-none block w-full pl-10 pr-3 py-2.5 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-cyan-500 focus:border-cyan-500 sm:text-sm">
                </div>
              </div>

              <!-- Password Input -->
              <div>
                <label for="password" class="block text-sm font-medium text-gray-700 mb-1">Password</label>
                <div class="relative">
                  <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <i data-lucide="lock" class="h-4 w-4 text-gray-400"></i>
                  </div>
                  <input type="password" id="password" name="password" required class="appearance-none block w-full pl-10 pr-3 py-2.5 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-cyan-500 focus:border-cyan-500 sm:text-sm">
                </div>
              </div>

              <!-- Confirm Password Input -->
              <div>
                <label for="password_confirmation" class="block text-sm font-medium text-gray-700 mb-1">Confirm Password</label>
                <div class="relative">
                  <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <i data-lucide="lock" class="h-4 w-4 text-gray-400"></i>
                  </div>
                  <input type="password" id="password_confirmation" name="password_confirmation" required class="appearance-none block w-full pl-10 pr-3 py-2.5 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-cyan-500 focus:border-cyan-500 sm:text-sm">
                </div>
              </div>
            </div>
          `,
        },
      ],
      footer: `
        <button type="button" class="bg-white hover:bg-gray-50 text-gray-700 border border-gray-300 rounded-lg shadow-sm px-4 py-2.5 text-sm font-medium">Cancel</button>
        <button type="submit" class="bg-cyan-600 hover:bg-cyan-700 text-white rounded-lg shadow-sm px-4 py-2.5 text-sm font-medium">Register</button>
      `,
      ...options,
    });
  }
}

// Export the Form class
export default new Form();
