# presidencyclub/templatetags/permission_tags.py
from django import template

register = template.Library()

@register.filter(name='has_permission')
def has_permission(user, permission_name):
    return user.has_permission(permission_name)