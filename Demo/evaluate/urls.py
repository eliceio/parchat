from django.conf.urls import url

from .views import evaluate, evaluate_models

urlpatterns = [
    url(r'^$', evaluate, name='evaluate'),
    url(r'^models/$', evaluate_models, name='evaluate_models'),
]
