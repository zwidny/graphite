# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.conf.urls import url

from . import views

urlpatterns = [
    url('^login$', views.login_view, name='account_login'),
    url('^logout$', views.logoutView, name='account_logout'),
    url('^edit$', views.editProfile, name='account_edit'),
    url('^update$', views.updateProfile, name='account_update'),
]
