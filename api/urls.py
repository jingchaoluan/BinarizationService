from rest_framework.urlpatterns import format_suffix_patterns
from django.conf.urls import url
from api import views

urlpatterns = [
    url(r'^$', views.binarizationView, name='binarizationView'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
