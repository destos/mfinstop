from django.conf.urls import patterns, include, url

from . import views

urlpatterns = patterns(
    '',
    url(r'^$', views.MotiveListView.as_view(), name="motives_list"),
    url(r'^create/$', views.MotiveCreateView.as_view(), name="create_motive"),
    url(r'^incident/$', views.MotiveIncidentView.as_view(), name="motive_incident"),
    url(r'^(?P<motive_pk>[\d]+)/$', views.MotiveIncidentView.as_view(), name="motive_detail"),
)
