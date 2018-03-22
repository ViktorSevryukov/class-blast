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

@register.simple_tag
def call_method(obj, method_name, *args):
    method = getattr(obj, method_name)
    return method(*args)
