from django.conf.urls import url

from .views import chat_gm, chat_sh, answer_gm, answer_sh, echo_user


urlpatterns = [
    url(r'^gyeongmin/$', chat_gm, name='gyeongmin'),
    url(r'^soonho/$', chat_sh, name='soonho'),
    url(r'^answer/sh/$', answer_sh, name='answer_sh'),
    url(r'^answer/gm/$', answer_gm, name='answer_gm'),
    url(r'^echo_user/$', echo_user, name='echo_user'),
]