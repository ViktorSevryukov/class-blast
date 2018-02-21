from django.template.defaultfilters import register
from django import template
import ast

register = template.Library()

@register.filter
def get_text(dictionary):
    parsed_dict = ast.literal_eval(dictionary)
    return parsed_dict.get('text')

@register.filter
def get_value(dictionary):
    parsed_dict = ast.literal_eval(dictionary)
    return parsed_dict.get('value')
