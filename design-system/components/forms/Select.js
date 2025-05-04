/**
 * Select Component
 *
 * A reusable select component for dropdown selections.
 *
 * Usage:
 * ```
 * // Basic select
 * Select.render({
 *   name: 'country',
 *   label: 'Country',
 *   options: [
 *     { value: '', text: 'Select a country', disabled: true, selected: true },
 *     { value: 'us', text: 'United States' },
 *     { value: 'bd', text: 'Bangladesh' }
 *   ]
 * });
 *
 * // Select with icon
 * Select.render({
 *   name: 'role',
 *   label: 'Register as',
 *   iconLeft: '<i data-lucide="user" class="h-4 w-4 text-gray-400"></i>',
 *   options: [
 *     { value: 'patient', text: 'Patient' },
 *     { value: 'doctor', text: 'Doctor' }
 *   ]
 * });
 * ```
 */

class Select {
  constructor() {
    this.baseSelectClasses =
      "appearance-none block w-full border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-cyan-500 focus:border-cyan-500 sm:text-sm";
    this.baseLabelClasses = "block text-sm font-medium text-gray-700 mb-1";
    this.baseIconClasses =
      "absolute inset-y-0 flex items-center pointer-events-none";
  }

  /**
   * Renders a select with the specified options
   * @param {Object} config - Select configuration
   * @param {string} config.name - Select name
   * @param {string} config.id - Select id (defaults to name if not provided)
   * @param {string} config.label - Select label
   * @param {Array} config.options - Array of option objects { value, text, disabled, selected }
   * @param {boolean} config.required - Whether the select is required
   * @param {string} config.validationState - Validation state (success, error)
   * @param {string} config.validationMessage - Validation message
   * @param {string} config.iconLeft - Icon to show at the left
   * @param {boolean} config.disabled - Whether the select is disabled
   * @param {string} config.className - Additional classes to apply
   * @returns {string} HTML markup for the select
   */
  render({
    name,
    id = "",
    label = "",
    options = [],
    required = false,
    validationState = "",
    validationMessage = "",
    iconLeft = "",
    disabled = false,
    className = "",
  }) {
    if (!name) {
      throw new Error("Select name is required");
    }

    if (!options || !options.length) {
      throw new Error("Select options are required");
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

    // Determine padding based on icon
    const paddingClasses = iconLeft ? "pl-10 pr-3" : "px-3";

    // Combine all select classes
    const selectClasses = [
      this.baseSelectClasses,
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

    // Create HTML for icon if provided
    const leftIconHtml = iconLeft
      ? `<div class="${this.baseIconClasses} left-0 pl-3">${iconLeft}</div>`
      : "";

    // Create the right arrow icon for the select
    const rightArrowHtml = `
      <div class="${this.baseIconClasses} right-0 pr-3 pointer-events-none">
        <i data-lucide="chevron-down" class="h-4 w-4 text-gray-400"></i>
      </div>
    `;

    // Create HTML for options
    const optionsHtml = options
      .map((option) => {
        const optionAttrs = [
          option.value !== undefined ? `value="${option.value}"` : "",
          option.disabled ? "disabled" : "",
          option.selected ? "selected" : "",
        ]
          .filter(Boolean)
          .join(" ");

        return `<option ${optionAttrs}>${option.text}</option>`;
      })
      .join("");

    // Create HTML for validation message if provided
    const validationHtml = validationMessage
      ? `<p class="mt-1 text-xs ${validationColor}">${validationMessage}</p>`
      : "";

    // Build the complete select HTML
    return `
      <div class="w-full">
        ${labelHtml}
        <div class="relative">
          ${leftIconHtml}
          <select
            id="${id}"
            name="${name}"
            ${required ? "required" : ""}
            ${disabled ? "disabled" : ""}
            class="${selectClasses}"
          >
            ${optionsHtml}
          </select>
          ${rightArrowHtml}
        </div>
        ${validationHtml}
      </div>
    `;
  }
}

// Export the Select class
export default new Select();
