from django import template
register=template.Library()
@register.filter
def getattr(obj,name):
    value=getattr(obj,name,None)
    if hasattr(value,'username'): return value.username
    return value
