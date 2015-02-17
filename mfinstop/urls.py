# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin

from pages.views import HomePageView, AboutPageView, ContactPageView, FAQPageView


admin.autodiscover()


urlpatterns = patterns(
    '',
    url(r'^$', HomePageView.as_view(), name="home"),
    url(r'^about/$', AboutPageView.as_view(), name="about"),
    url(r'^contact/$', ContactPageView.as_view(), name="contact"),
    url(r'^faq/$', FAQPageView.as_view(), name="faq"),

    url(r'^admin/', include(admin.site.urls)),

    # User management
    url(r'^users/', include('users.urls', namespace='users')),
    url(r'^accounts/', include('allauth.urls')),
    # Avatars
    url(r'^avatar/', include('avatar.urls')),

    # Manage Things
    url(r'^things/', include('things.urls', namespace='things')),

    # Hijack urls
    url(r'^hijack/', include('hijack.urls')),

    # feature test switches
    url(r'^', include('waffle.urls')),

) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
