from django.conf.urls import url

from .views import chat, response, echo_user


urlpatterns = [
    url(r'^progressive/$', chat, name='chat_progressive'),
    url(r'^conservative/$', chat, name='chat_conservative'),
    url(r'^neutral1/$', chat, name='chat_neutral1'),
    url(r'^neutral2/$', chat, name='chat_neutral2'),
    url(r'^neutral2_meta/$', chat, name='chat_neutral2_meta'),
    url(r'^response/$', response, name='response'),
    url(r'^echo_user/$', echo_user, name='echo_user'),
]
