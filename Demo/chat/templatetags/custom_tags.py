from django import template

from chat.views import grab_response_type

register = template.Library()


@register.filter(name="to_img_path")
def to_img_path(tag):
    return "/static/images/%s.png" % tag


@register.filter(name="to_user_type")
def to_user_type(string):
    return grab_response_type(string)

