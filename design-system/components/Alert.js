/**
 * Alert Component
 *
 * A reusable alert component for displaying status messages, notifications, or important information.
 *
 * Usage:
 * ```
 * // Success alert
 * Alert.success('Your profile has been updated successfully');
 *
 * // Error alert with title and dismissible option
 * Alert.error({
 *   title: 'Error',
 *   message: 'There was a problem updating your profile',
 *   dismissible: true
 * });
 *
 * // Info alert with custom icon
 * Alert.info({
 *   message: 'Your appointment is scheduled for tomorrow',
 *   icon: '<i data-lucide="calendar" class="h-5 w-5"></i>'
 * });
 * ```
 */

class Alert {
  constructor() {
    this.baseClasses = "rounded-lg p-4 my-3";
  }

  /**
   * Renders an alert with the specified options
   * @param {Object|string} options - Alert options or message string
   * @param {string} options.type - Alert type (success, error, warning, info)
   * @param {string} options.title - Alert title
   * @param {string} options.message - Alert message
   * @param {string} options.icon - Custom icon HTML
   * @param {boolean} options.dismissible - Whether the alert can be dismissed
   * @param {string} options.className - Additional classes to apply
   * @returns {string} HTML markup for the alert
   */
  render(options) {
    // Handle case where only message is provided as a string
    if (typeof options === "string") {
      options = { message: options };
    }

    const {
      type = "info",
      title = "",
      message = "",
      icon = "",
      dismissible = false,
      className = "",
    } = options;

    if (!message) {
      throw new Error("Alert message is required");
    }

    // Configure type-specific properties
    let typeClasses = "";
    let defaultIcon = "";

    switch (type) {
      case "success":
        typeClasses = "bg-green-50 text-green-800 border border-green-200";
        defaultIcon =
          '<i data-lucide="check-circle" class="h-5 w-5 text-green-500"></i>';
        break;
      case "error":
        typeClasses = "bg-red-50 text-red-800 border border-red-200";
        defaultIcon =
          '<i data-lucide="alert-circle" class="h-5 w-5 text-red-500"></i>';
        break;
      case "warning":
        typeClasses = "bg-amber-50 text-amber-800 border border-amber-200";
        defaultIcon =
          '<i data-lucide="alert-triangle" class="h-5 w-5 text-amber-500"></i>';
        break;
      case "info":
      default:
        typeClasses = "bg-blue-50 text-blue-800 border border-blue-200";
        defaultIcon =
          '<i data-lucide="info" class="h-5 w-5 text-blue-500"></i>';
        break;
    }

    // Use provided icon or default for the alert type
    const alertIcon = icon || defaultIcon;

    // Combine all classes
    const alertClasses = [this.baseClasses, typeClasses, className]
      .filter(Boolean)
      .join(" ");

    // Create the dismiss button if dismissible
    const dismissButton = dismissible
      ? `
        <button type="button" class="ml-auto -mx-1.5 -my-1.5 rounded-lg p-1.5 inline-flex focus:outline-none focus:ring-2 focus:ring-offset-2" data-dismiss-alert>
          <span class="sr-only">Dismiss</span>
          <i data-lucide="x" class="h-4 w-4"></i>
        </button>
      `
      : "";

    // Build the complete alert HTML with optional title
    const alertHTML = `
      <div class="${alertClasses}" role="alert">
        <div class="flex items-start">
          <div class="flex-shrink-0 mt-0.5">
            ${alertIcon}
          </div>
          <div class="ml-3 flex-1">
            ${title ? `<h3 class="text-sm font-medium">${title}</h3>` : ""}
            <div class="text-sm ${title ? "mt-1" : ""}">
              ${message}
            </div>
          </div>
          ${dismissButton}
        </div>
      </div>
    `;

    // Add JavaScript for dismissible alerts if needed
    if (dismissible) {
      // In a real implementation, you'd want to attach event handlers
      // or use a library to handle dismissing alerts
      console.warn(
        "Dismissible alerts require JavaScript to handle the dismiss action."
      );
    }

    return alertHTML;
  }

  /**
   * Creates a success alert
   * @param {Object|string} options - Alert options or message string
   * @returns {string} HTML markup for a success alert
   */
  success(options) {
    if (typeof options === "string") {
      options = { message: options };
    }
    return this.render({ ...options, type: "success" });
  }

  /**
   * Creates an error alert
   * @param {Object|string} options - Alert options or message string
   * @returns {string} HTML markup for an error alert
   */
  error(options) {
    if (typeof options === "string") {
      options = { message: options };
    }
    return this.render({ ...options, type: "error" });
  }

  /**
   * Creates a warning alert
   * @param {Object|string} options - Alert options or message string
   * @returns {string} HTML markup for a warning alert
   */
  warning(options) {
    if (typeof options === "string") {
      options = { message: options };
    }
    return this.render({ ...options, type: "warning" });
  }

  /**
   * Creates an info alert
   * @param {Object|string} options - Alert options or message string
   * @returns {string} HTML markup for an info alert
   */
  info(options) {
    if (typeof options === "string") {
      options = { message: options };
    }
    return this.render({ ...options, type: "info" });
  }
}

// Export the Alert class
export default new Alert();
