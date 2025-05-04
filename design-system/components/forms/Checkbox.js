/**
 * Checkbox Component
 *
 * A reusable checkbox component with label support.
 *
 * Usage:
 * ```
 * // Basic checkbox
 * Checkbox.render({
 *   name: 'terms',
 *   label: 'I agree to the terms and conditions'
 * });
 *
 * // Checkbox with custom state
 * Checkbox.render({
 *   name: 'newsletter',
 *   label: 'Subscribe to newsletter',
 *   checked: true,
 *   required: true
 * });
 * ```
 */

class Checkbox {
  constructor() {
    this.baseCheckboxClasses =
      "h-4 w-4 text-cyan-600 focus:ring-cyan-500 border-gray-300 rounded";
    this.baseLabelClasses = "ml-2 block text-sm text-gray-700";
  }

  /**
   * Renders a checkbox with the specified options
   * @param {Object} options - Checkbox options
   * @param {string} options.name - Checkbox name
   * @param {string} options.id - Checkbox id (defaults to name if not provided)
   * @param {string} options.label - Checkbox label
   * @param {boolean} options.checked - Whether the checkbox is checked
   * @param {boolean} options.required - Whether the checkbox is required
   * @param {boolean} options.disabled - Whether the checkbox is disabled
   * @param {string} options.value - Checkbox value (defaults to "1")
   * @param {string} options.className - Additional classes to apply to the checkbox
   * @param {string} options.labelClassName - Additional classes to apply to the label
   * @returns {string} HTML markup for the checkbox
   */
  render({
    name,
    id = "",
    label = "",
    checked = false,
    required = false,
    disabled = false,
    value = "1",
    className = "",
    labelClassName = "",
  }) {
    if (!name) {
      throw new Error("Checkbox name is required");
    }

    // Set id to name if not provided
    id = id || name;

    // Combine checkbox classes
    const checkboxClasses = [
      this.baseCheckboxClasses,
      disabled ? "opacity-50 cursor-not-allowed" : "",
      className,
    ]
      .filter(Boolean)
      .join(" ");

    // Combine label classes
    const labelClasses = [
      this.baseLabelClasses,
      disabled ? "opacity-50 cursor-not-allowed" : "",
      labelClassName,
    ]
      .filter(Boolean)
      .join(" ");

    // Create HTML for the checkbox with label
    return `
      <div class="flex items-center">
        <input
          type="checkbox"
          id="${id}"
          name="${name}"
          value="${value}"
          ${checked ? "checked" : ""}
          ${required ? "required" : ""}
          ${disabled ? "disabled" : ""}
          class="${checkboxClasses}"
        />
        ${
          label
            ? `<label for="${id}" class="${labelClasses}">${label}${
                required ? ' <span class="text-red-500">*</span>' : ""
              }</label>`
            : ""
        }
      </div>
    `;
  }

  /**
   * Renders a checkbox group with the specified options
   * @param {Object} options - Checkbox group options
   * @param {string} options.name - Base name for the checkboxes
   * @param {string} options.legend - Group legend/title
   * @param {Array} options.items - Array of checkbox items { id, label, value, checked, disabled }
   * @param {boolean} options.required - Whether selection is required
   * @param {string} options.className - Additional classes for the group
   * @returns {string} HTML markup for the checkbox group
   */
  group({ name, legend = "", items = [], required = false, className = "" }) {
    if (!name) {
      throw new Error("Checkbox group name is required");
    }

    if (!items || !items.length) {
      throw new Error("Checkbox group items are required");
    }

    // Create HTML for each checkbox in the group
    const checkboxesHtml = items
      .map((item, index) => {
        return this.render({
          name: `${name}[${index}]`,
          id: item.id || `${name}_${index}`,
          label: item.label,
          value: item.value || item.label,
          checked: item.checked || false,
          disabled: item.disabled || false,
          required: false, // Individual checkboxes in a group aren't required
        });
      })
      .join("\n");

    // Build the complete checkbox group HTML
    return `
      <fieldset class="space-y-3 ${className}">
        ${
          legend
            ? `<legend class="text-sm font-medium text-gray-700 mb-2">${legend}${
                required ? ' <span class="text-red-500">*</span>' : ""
              }</legend>`
            : ""
        }
        ${checkboxesHtml}
      </fieldset>
    `;
  }
}

// Export the Checkbox class
export default new Checkbox();
