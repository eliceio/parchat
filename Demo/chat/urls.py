from django.conf.urls import url

from .views import progressive, conservative, echo, echo_user


urlpatterns = [
    url(r'^progressive/$', progressive, name='progressive'),
    url(r'^conservative/$', conservative, name='conservative'),
    url(r'^echo/$', echo, name='echo'),
    url(r'^echo_user/$', echo_user, name='echo_user'),
]