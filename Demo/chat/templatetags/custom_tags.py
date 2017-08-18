from django import template

from chat.views import grab_model_name


register = template.Library()

tag_img_path_dict = {
    "user": "user",
    "progressive": "progressive_congressman",
    "conservative": "conservative_congressman",
    "all": "congressman",
    "all_meta": "congressman",
}

model_user_name_dict = {
    "user": "User",
    "progressive": "Progressive Congressman",
    "conservative": "Conservative Congressman",
    "all": "Congressman",
    "all_meta": "Congressman+",
}


@register.filter(name="to_model_name")
def to_model_name(string):
    return grab_model_name(string)


@register.filter(name="to_img_path")
def to_img_path(tag):
    img_name = tag_img_path_dict[tag]
    return "/static/images/%s.png" % img_name


@register.filter(name="to_user_name")
def to_user_name(string):
    for model_name, user_name in model_user_name_dict.items():
        if string in model_name:
            return user_name
    return "Congressman"

