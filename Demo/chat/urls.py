from django.conf.urls import url

from .views import chat_all, chat_all_meta, chat_progressive, chat_conservative
from .views import response, echo_user


urlpatterns = [
    url(r'^all/$', chat_all, name='chat_all'),
    url(r'^all_meta/$', chat_all_meta, name='chat_all_meta'),
    url(r'^progressive/$', chat_progressive, name='chat_progressive'),
    url(r'^conservative/$', chat_conservative, name='chat_conservative'),
    url(r'^response/$', response, name='response'),
    url(r'^echo_user/$', echo_user, name='echo_user'),
]
