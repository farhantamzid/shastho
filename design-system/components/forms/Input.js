/**
 * Input Component
 *
 * A reusable input component with multiple variants and states.
 *
 * Usage:
 * ```
 * // Basic input
 * Input.text({ name: 'username', placeholder: 'Enter username' });
 *
 * // Input with label and icon
 * Input.text({
 *   name: 'email',
 *   label: 'Email Address',
 *   iconLeft: '<i data-lucide="mail" class="h-4 w-4 text-gray-400"></i>',
 *   placeholder: 'user@example.com'
 * });
 *
 * // Input with validation state
 * Input.text({
 *   name: 'password',
 *   type: 'password',
 *   label: 'Password',
 *   validationState: 'error',
 *   validationMessage: 'Password must be at least 8 characters'
 * });
 * ```
 */

class Input {
  constructor() {
    this.baseInputClasses =
      "appearance-none block w-full border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-cyan-500 focus:border-cyan-500 sm:text-sm";
    this.baseLabelClasses = "block text-sm font-medium text-gray-700 mb-1";
    this.baseIconClasses =
      "absolute inset-y-0 flex items-center pointer-events-none";
  }

  /**
   * Renders an input with the specified options
   * @param {Object} options - Input options
   * @param {string} options.type - Input type (text, password, email, etc.)
   * @param {string} options.name - Input name
   * @param {string} options.id - Input id (defaults to name if not provided)
   * @param {string} options.label - Input label
   * @param {string} options.placeholder - Input placeholder
   * @param {string} options.value - Input value
   * @param {boolean} options.required - Whether the input is required
   * @param {string} options.validationState - Validation state (success, error)
   * @param {string} options.validationMessage - Validation message
   * @param {string} options.iconLeft - Icon to show at the left
   * @param {string} options.iconRight - Icon to show at the right
   * @param {boolean} options.disabled - Whether the input is disabled
   * @param {string} options.className - Additional classes to apply
   * @returns {string} HTML markup for the input
   */
  render({
    type = "text",
    name,
    id = "",
    label = "",
    placeholder = "",
    value = "",
    required = false,
    validationState = "",
    validationMessage = "",
    iconLeft = "",
    iconRight = "",
    disabled = false,
    className = "",
  }) {
    if (!name) {
      throw new Error("Input name is required");
    }

    // Set id to name if not provided
    id = id || name;

    // Determine validation-specific classes
    let validationClasses = "";
    let validationColor = "";

    switch (validationState) {
      case "success":
        validationClasses =
          "border-green-500 focus:border-green-500 focus:ring-green-500";
        validationColor = "text-green-600";
        break;
      case "error":
        validationClasses =
          "border-red-500 focus:border-red-500 focus:ring-red-500";
        validationColor = "text-red-600";
        break;
      default:
        validationClasses = "";
        validationColor = "";
    }

    // Determine padding based on icons
    let paddingClasses = "";
    if (iconLeft && iconRight) {
      paddingClasses = "pl-10 pr-10";
    } else if (iconLeft) {
      paddingClasses = "pl-10 pr-3";
    } else if (iconRight) {
      paddingClasses = "pl-3 pr-10";
    } else {
      paddingClasses = "px-3";
    }

    // Combine all input classes
    const inputClasses = [
      this.baseInputClasses,
      paddingClasses,
      validationClasses,
      disabled ? "bg-gray-100 cursor-not-allowed" : "",
      className,
    ]
      .filter(Boolean)
      .join(" ");

    // Create HTML for the label if provided
    const labelHtml = label
      ? `<label for="${id}" class="${this.baseLabelClasses}">${label}${
          required ? ' <span class="text-red-500">*</span>' : ""
        }</label>`
      : "";

    // Create HTML for icons if provided
    const leftIconHtml = iconLeft
      ? `<div class="${this.baseIconClasses} left-0 pl-3">${iconLeft}</div>`
      : "";

    const rightIconHtml = iconRight
      ? `<div class="${this.baseIconClasses} right-0 pr-3">${iconRight}</div>`
      : "";

    // Create HTML for validation message if provided
    const validationHtml = validationMessage
      ? `<p class="mt-1 text-xs ${validationColor}">${validationMessage}</p>`
      : "";

    // Build the complete input HTML
    return `
      <div class="w-full">
        ${labelHtml}
        <div class="relative">
          ${leftIconHtml}
          <input
            type="${type}"
            id="${id}"
            name="${name}"
            ${placeholder ? `placeholder="${placeholder}"` : ""}
            ${value ? `value="${value}"` : ""}
            ${required ? "required" : ""}
            ${disabled ? "disabled" : ""}
            class="${inputClasses}"
          />
          ${rightIconHtml}
        </div>
        ${validationHtml}
      </div>
    `;
  }

  /**
   * Creates a text input
   */
  text(options = {}) {
    return this.render({ type: "text", ...options });
  }

  /**
   * Creates a password input
   */
  password(options = {}) {
    // Default icon for password fields if none provided
    const defaultRightIcon =
      '<button type="button" class="text-gray-400 hover:text-gray-500 focus:outline-none">' +
      '<i data-lucide="eye" class="h-4 w-4"></i>' +
      "</button>";

    return this.render({
      type: "password",
      iconRight: options.iconRight || defaultRightIcon,
      ...options,
    });
  }

  /**
   * Creates an email input
   */
  email(options = {}) {
    return this.render({ type: "email", ...options });
  }

  /**
   * Creates a number input
   */
  number(options = {}) {
    return this.render({ type: "number", ...options });
  }

  /**
   * Creates a search input
   */
  search(options = {}) {
    const defaultLeftIcon =
      '<i data-lucide="search" class="h-4 w-4 text-gray-400"></i>';

    return this.render({
      type: "search",
      iconLeft: options.iconLeft || defaultLeftIcon,
      ...options,
    });
  }
}

// Export the Input class
export default new Input();
