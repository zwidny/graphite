# -*- coding: utf-8 -*-
from __future__ import absolute_import
import json

from django.utils.safestring import mark_safe
from django.contrib.staticfiles import finders
from django.shortcuts import render_to_response

from .utils import config, get_permissions
from .models import Dashboard


def dashboard(request, name=None):
    dashboard_conf_missing = False

    try:
        config.check()
    except OSError as e:
        if e.errno == errno.ENOENT:
            dashboard_conf_missing = True
        else:
            raise

    initialError = None
    debug = request.GET.get('debug', False)
    theme = request.GET.get('theme', config.ui_config['theme'])
    css_file = finders.find('css/dashboard-%s.css' % theme)
    if css_file is None:
        initialError = "Invalid theme '%s'" % theme
        theme = config.ui_config['theme']

    context = {
        'schemes_json': mark_safe(json.dumps(config.schemes)),
        'ui_config_json': mark_safe(json.dumps(config.ui_config)),
        'jsdebug': debug or settings.JAVASCRIPT_DEBUG,
        'debug': debug,
        'theme': theme,
        'initialError': initialError,
        'querystring': mark_safe(json.dumps(dict(request.GET.items()))),
        'dashboard_conf_missing': dashboard_conf_missing,
        'userName': '',
        'permissions': mark_safe(json.dumps(get_permissions(request.user))),
        'permissionsUnauthenticated': mark_safe(json.dumps(get_permissions(None)))
    }
    user = request.user
    if user:
        context['userName'] = user.username

    if name is not None:
        try:
            dashboard = Dashboard.objects.get(name=name)
        except Dashboard.DoesNotExist:
            context['initialError'] = "Dashboard '%s' does not exist." % name
        else:
            context['initialState'] = dashboard.state

    return render_to_response("dashboard.html", context)
