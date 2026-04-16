from django import template
from website.models import WaffleMenu

register = template.Library()

@register.simple_tag
def get_waffle_menu():
    return WaffleMenu.objects.first()
