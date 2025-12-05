from django import template
import os
from os.path import splitext

register = template.Library()

@register.filter(name='add_class')
def add_class(value, css_class):
    return value.as_widget(attrs={'class': css_class})



@register.filter
def get_language_field(value, lang):
    """
    Appends the language suffix (like _en or _ar) to the field name dynamically.
    Example: {{ news|get_language_field:selected_language }}
    """
    field_name = f"{value}_{lang}"
    return getattr(value, field_name, "")


@register.filter(name='get_filename')
def get_filename(value):
    """Extracts the filename from a path"""
    return value.split('/')[-1]  # Only the file name

@register.filter(name='splitext')
def splitext_filter(value):
    """Split a filename into root and extension"""
    return splitext(value)