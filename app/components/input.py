"""
Input component that adheres to the shastho design system.
"""

def text(name, label=None, placeholder="", value="", required=False, error=None, helper_text=None,
         disabled=False, additional_classes=""):
    """
    Generate HTML for a text input field.

    Args:
        name (str): Input name/id
        label (str): Input label text
        placeholder (str): Placeholder text
        value (str): Current value
        required (bool): Whether the field is required
        error (str): Error message if validation failed
        helper_text (str): Additional helper text
        disabled (bool): Whether the input is disabled
        additional_classes (str): Additional CSS classes

    Returns:
        str: HTML for the text input
    """
    # Generate a unique ID if name contains spaces or special characters
    input_id = name.replace(" ", "_").lower()

    # Base container
    html = f'<div class="mb-4">'

    # Add label if provided
    if label:
        html += f'<label for="{input_id}" class="block text-sm font-medium text-gray-700 mb-1">{label}'
        if required:
            html += ' <span class="text-error">*</span>'
        html += '</label>'

    # Input classes
    input_classes = "w-full rounded-lg border px-3 py-2 text-gray-700 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"

    # Add error classes if there's an error
    if error:
        input_classes += " border-error focus:ring-error"
    else:
        input_classes += " border-gray-300"

    # Add disabled classes
    if disabled:
        input_classes += " bg-gray-100 cursor-not-allowed"

    # Add any additional classes
    if additional_classes:
        input_classes += f" {additional_classes}"

    # Build the input element
    required_attr = 'required' if required else ''
    disabled_attr = 'disabled' if disabled else ''

    html += f'<input type="text" id="{input_id}" name="{name}" placeholder="{placeholder}" '
    html += f'value="{value}" class="{input_classes}" {required_attr} {disabled_attr}>'

    # Add helper text or error message
    if error:
        html += f'<p class="mt-1 text-sm text-error">{error}</p>'
    elif helper_text:
        html += f'<p class="mt-1 text-sm text-gray-500">{helper_text}</p>'

    html += '</div>'

    return html

def password(name, label=None, placeholder="", required=False, error=None, helper_text=None,
             disabled=False, additional_classes=""):
    """
    Generate HTML for a password input field.

    Args:
        name (str): Input name/id
        label (str): Input label text
        placeholder (str): Placeholder text
        required (bool): Whether the field is required
        error (str): Error message if validation failed
        helper_text (str): Additional helper text
        disabled (bool): Whether the input is disabled
        additional_classes (str): Additional CSS classes

    Returns:
        str: HTML for the password input
    """
    # Generate a unique ID from the name if needed
    input_id = name.lower().replace(' ', '_')

    # Start building the HTML
    html = '<div class="mb-4">'

    # Add label if provided
    if label:
        html += f'<label for="{input_id}" class="block text-sm font-medium text-gray-700 mb-1">{label}'
        if required:
            html += ' <span class="text-error">*</span>'
        html += '</label>'

    # Base input classes
    input_classes = "w-full px-3 py-2 border rounded-lg text-gray-700 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"

    # Add error or disabled styles
    if error:
        input_classes += " border-error focus:border-error focus:ring-error/20"
    elif disabled:
        input_classes += " bg-gray-100 border-gray-300 text-gray-500 cursor-not-allowed"
    else:
        input_classes += " border-gray-300"

    # Add user's additional classes
    if additional_classes:
        input_classes += f" {additional_classes}"

    # Required attribute
    required_attr = 'required' if required else ''

    # Disabled attribute
    disabled_attr = 'disabled' if disabled else ''

    # Build the input tag
    html += f'<input type="password" id="{input_id}" name="{name}" placeholder="{placeholder}" '
    html += f'class="{input_classes}" {required_attr} {disabled_attr}>'

    # Add error message if provided
    if error:
        html += f'<p class="mt-1 text-sm text-error">{error}</p>'

    # Add helper text if provided
    if helper_text and not error:
        html += f'<p class="mt-1 text-sm text-gray-500">{helper_text}</p>'

    html += '</div>'

    return html

def select(name, options, label=None, selected="", required=False, error=None, helper_text=None,
           disabled=False, additional_classes=""):
    """
    Generate HTML for a select dropdown.

    Args:
        name (str): Select name/id
        options (list): List of options as dicts with 'value' and 'text' keys
        label (str): Select label text
        selected (str): Currently selected value
        required (bool): Whether the field is required
        error (str): Error message if validation failed
        helper_text (str): Additional helper text
        disabled (bool): Whether the select is disabled
        additional_classes (str): Additional CSS classes

    Returns:
        str: HTML for the select dropdown
    """
    # Generate a unique ID from the name if needed
    select_id = name.lower().replace(' ', '_')

    # Start building the HTML
    html = '<div class="mb-4">'

    # Add label if provided
    if label:
        html += f'<label for="{select_id}" class="block text-sm font-medium text-gray-700 mb-1">{label}'
        if required:
            html += ' <span class="text-error">*</span>'
        html += '</label>'

    # Base select classes
    select_classes = "w-full px-3 py-2 border rounded-lg text-gray-700 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"

    # Add error or disabled styles
    if error:
        select_classes += " border-error focus:border-error focus:ring-error/20"
    elif disabled:
        select_classes += " bg-gray-100 border-gray-300 text-gray-500 cursor-not-allowed"
    else:
        select_classes += " border-gray-300"

    # Add user's additional classes
    if additional_classes:
        select_classes += f" {additional_classes}"

    # Required attribute
    required_attr = 'required' if required else ''

    # Disabled attribute
    disabled_attr = 'disabled' if disabled else ''

    # Build the select tag and options
    html += f'<select id="{select_id}" name="{name}" class="{select_classes}" {required_attr} {disabled_attr}>'

    for option in options:
        is_selected = 'selected' if option['value'] == selected else ''
        html += f'<option value="{option["value"]}" {is_selected}>{option["text"]}</option>'

    html += '</select>'

    # Add error message if provided
    if error:
        html += f'<p class="mt-1 text-sm text-error">{error}</p>'

    # Add helper text if provided
    if helper_text and not error:
        html += f'<p class="mt-1 text-sm text-gray-500">{helper_text}</p>'

    html += '</div>'

    return html

def textarea(name, label=None, placeholder="", value="", rows=4, required=False,
             error=None, helper_text=None, disabled=False, additional_classes=""):
    """
    Generate HTML for a textarea field.

    Args:
        name (str): Input name/id
        label (str): Input label text
        placeholder (str): Placeholder text
        value (str): Current value
        rows (int): Number of rows to display
        required (bool): Whether the field is required
        error (str): Error message if validation failed
        helper_text (str): Additional helper text
        disabled (bool): Whether the textarea is disabled
        additional_classes (str): Additional CSS classes

    Returns:
        str: HTML for the textarea
    """
    # Generate a unique ID if name contains spaces or special characters
    input_id = name.replace(" ", "_").lower()

    # Base container
    html = f'<div class="mb-4">'

    # Add label if provided
    if label:
        html += f'<label for="{input_id}" class="block text-sm font-medium text-gray-700 mb-1">{label}'
        if required:
            html += ' <span class="text-error">*</span>'
        html += '</label>'

    # Textarea classes
    textarea_classes = "w-full rounded-lg border px-3 py-2 text-gray-700 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"

    # Add error classes if there's an error
    if error:
        textarea_classes += " border-error focus:ring-error"
    else:
        textarea_classes += " border-gray-300"

    # Add disabled classes
    if disabled:
        textarea_classes += " bg-gray-100 cursor-not-allowed"

    # Add any additional classes
    if additional_classes:
        textarea_classes += f" {additional_classes}"

    # Build the textarea element
    required_attr = 'required' if required else ''
    disabled_attr = 'disabled' if disabled else ''

    html += f'<textarea id="{input_id}" name="{name}" placeholder="{placeholder}" '
    html += f'rows="{rows}" class="{textarea_classes}" {required_attr} {disabled_attr}>{value}</textarea>'

    # Add helper text or error message
    if error:
        html += f'<p class="mt-1 text-sm text-error">{error}</p>'
    elif helper_text:
        html += f'<p class="mt-1 text-sm text-gray-500">{helper_text}</p>'

    html += '</div>'

    return html