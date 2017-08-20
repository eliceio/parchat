from django import template

from chat.views import grab_model_name


register = template.Library()

tag_img_path_dict = {
    "user": "user",
    "progressive": "progressive_congressperson",
    "conservative": "conservative_congressperson",
    "neutral1": "neutral_congressperson",
    "neutral2": "neutral_congressperson",
    "neutral2_meta": "neutral_congressperson",
    "congressperson": "congressperson",
}

model_user_name_dict = {
    "user": "User",
    "progressive": "Progressive Congressperson",
    "conservative": "Conservative Congressperson",
    "neutral1": "Neutral Congressperson(1)",
    "neutral2": "Neutral Congressperson(2)",
    "neutral2_meta": "Neutral+META Congressperson",
    "congressperson": "Congressperson",
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
    return "Congressperson"

