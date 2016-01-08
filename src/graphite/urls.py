# -*- coding: utf-8 -*-
"""graphite URL Configuration.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin

import url_shortener.views
import browser.views
import browser.urls
import graphite.views
import composer.urls
import dashboard.urls
import events.urls
import render.urls
import account.urls
# import metrics.urls

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^render/', include(render.urls)),
    url(r'^composer/', include(composer.urls)),
    # url(r'^metrics/', include(metrics.urls),
    url(r'^browser/', include(browser.urls)),
    url(r'^account/', include(account.urls)),
    url(r'^dashboard/', include(dashboard.urls)),
    # url(r'^whitelist/', include(whitelist.urls),
    # url(r'^version/', include(version.urls),
    url(r'^events/', include(events.urls)),
    url(r'^s/(?P<path>.*)', url_shortener.views.shorten, name='shorten'),
    url(r'^S/(?P<link_id>[a-zA-Z0-9]+)/?$', url_shortener.views.follow, name='follow'),
    url(r'^$', browser.views.browser, name='browser'),

]

handler500 = graphite.views.server_error
