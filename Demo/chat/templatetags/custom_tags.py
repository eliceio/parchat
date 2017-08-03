from django import template

from chat.views import grab_response_type

register = template.Library()


@register.filter(name="to_img_path")
def to_img_path(tag):
    tag_img_path_dict = {
        "user": "user",
        "Gyeongmin": "gyeongmin",
        "Soonho - Progressive": "soonho_pro",
        "Soonho - Conservative": "soonho_con",
    }
    img_name = tag_img_path_dict[tag]
    return "/static/images/%s.png" % img_name


@register.filter(name="to_user_type")
def to_user_type(string):
    return grab_response_type(string)

