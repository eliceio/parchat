from django.conf.urls import url

from .views import chat_all, chat_all_meta, chat_progressive, chat_conservative
from .views import response_all, response_all_meta, response_progressive, response_conservative, echo_user


urlpatterns = [
    url(r'^all/$', chat_all, name='chat_all'),
    url(r'^all_meta/$', chat_all_meta, name='chat_all_meta'),
    url(r'^progressive/$', chat_progressive, name='chat_progressive'),
    url(r'^conservative/$', chat_conservative, name='chat_conservative'),
    url(r'^response/all/$', response_all, name='response_all'),
    url(r'^response/all_meta/$', response_all_meta, name='response_all_meta'),
    url(r'^response/progressive/$', response_progressive, name='response_progressive'),
    url(r'^response/conservative/$', response_conservative, name='response_conservative'),
    url(r'^echo_user/$', echo_user, name='echo_user'),
]
