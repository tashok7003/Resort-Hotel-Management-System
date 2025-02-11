from django import template
import json

register = template.Library()

@register.filter
def divide(value, arg):
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError):
        return 0

@register.filter
def map_attr(value, arg):
    """Extract a list of values for a given attribute from a list of dictionaries"""
    try:
        return json.dumps([item[arg] for item in value])
    except (KeyError, TypeError):
        return '[]' 