from django.conf.urls import url

from .views import chat_gm, chat_sh_pro, chat_sh_con, answer_gm, answer_sh_pro, answer_sh_con, echo_user


urlpatterns = [
    url(r'^gyeongmin/$', chat_gm, name='gyeongmin'),
    url(r'^soonho/pro/$', chat_sh_pro, name='soonho_pro'),
    url(r'^soonho/con/$', chat_sh_con, name='soonho_con'),
    url(r'^answer/sh/pro/$', answer_sh_pro, name='answer_sh_pro'),
    url(r'^answer/sh/con/$', answer_sh_con, name='answer_sh_con'),
    url(r'^answer/gm/$', answer_gm, name='answer_gm'),
    url(r'^echo_user/$', echo_user, name='echo_user'),
]
