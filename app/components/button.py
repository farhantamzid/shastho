"""
Button component that adheres to the shastho design system.
"""

def primary(text, type="button", size="md", full_width=False, icon=None, additional_classes=""):
    """
    Generate HTML for a primary button.

    Args:
        text (str): Button text
        type (str): Button type (button, submit, reset)
        size (str): Button size (sm, md, lg)
        full_width (bool): Whether the button should take full width
        icon (str): Optional HTML for an icon
        additional_classes (str): Additional CSS classes

    Returns:
        str: HTML for the button
    """
    # Base classes
    classes = "bg-primary hover:bg-primary-hover text-white rounded-lg font-medium transition-colors"

    # Size classes
    size_classes = {
        "sm": "px-3 py-1.5 text-sm",
        "md": "px-4 py-2.5",
        "lg": "px-6 py-3 text-lg"
    }

    classes += f" {size_classes.get(size, size_classes['md'])}"

    # Width class
    if full_width:
        classes += " w-full"

    # Add any additional classes
    if additional_classes:
        classes += f" {additional_classes}"

    # Add icon if provided
    icon_html = f"{icon} " if icon else ""

    return f'<button type="{type}" class="{classes}">{icon_html}{text}</button>'

def secondary(text, type="button", size="md", full_width=False, icon=None, additional_classes=""):
    """
    Generate HTML for a secondary button.

    Args:
        text (str): Button text
        type (str): Button type (button, submit, reset)
        size (str): Button size (sm, md, lg)
        full_width (bool): Whether the button should take full width
        icon (str): Optional HTML for an icon
        additional_classes (str): Additional CSS classes

    Returns:
        str: HTML for the button
    """
    # Base classes
    classes = "bg-white border border-gray-300 text-gray-700 hover:bg-gray-50 rounded-lg font-medium transition-colors"

    # Size classes
    size_classes = {
        "sm": "px-3 py-1.5 text-sm",
        "md": "px-4 py-2.5",
        "lg": "px-6 py-3 text-lg"
    }

    classes += f" {size_classes.get(size, size_classes['md'])}"

    # Width class
    if full_width:
        classes += " w-full"

    # Add any additional classes
    if additional_classes:
        classes += f" {additional_classes}"

    # Add icon if provided
    icon_html = f"{icon} " if icon else ""

    return f'<button type="{type}" class="{classes}">{icon_html}{text}</button>'

def link(text, href="#", size="md", icon=None, additional_classes=""):
    """
    Generate HTML for a link styled as a button.

    Args:
        text (str): Button text
        href (str): Link destination
        size (str): Button size (sm, md, lg)
        icon (str): Optional HTML for an icon
        additional_classes (str): Additional CSS classes

    Returns:
        str: HTML for the link button
    """
    # Base classes
    classes = "text-primary hover:text-primary-hover font-medium transition-colors"

    # Size classes
    size_classes = {
        "sm": "text-sm",
        "md": "",
        "lg": "text-lg"
    }

    classes += f" {size_classes.get(size, size_classes['md'])}"

    # Add any additional classes
    if additional_classes:
        classes += f" {additional_classes}"

    # Add icon if provided
    icon_html = f"{icon} " if icon else ""

    return f'<a href="{href}" class="{classes}">{icon_html}{text}</a>'