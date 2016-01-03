# -*- coding: utf-8 -*-
from __future__ import absolute_import
import re
from os.path import getmtime
from ConfigParser import ConfigParser
from django.conf import settings


fieldRegex = re.compile(r'<([^>]+)>')

defaultScheme = {
    'name': 'Everything',
    'pattern': '<category>',
    'fields': [dict(name='category', label='Category')],
}

defaultUIConfig = {
    'default_graph_width': 400,
    'default_graph_height': 250,
    'refresh_interval':  60,
    'autocomplete_delay': 375,
    'merge_hover_delay': 700,
    'theme': 'default',
}

defaultKeyboardShortcuts = {
    'toggle_toolbar': 'ctrl-z',
    'toggle_metrics_panel': 'ctrl-space',
    'erase_all_graphs': 'alt-x',
    'save_dashboard': 'alt-s',
    'completer_add_metrics': 'alt-enter',
    'completer_del_metrics': 'alt-backspace',
    'give_completer_focus': 'shift-space',
}


ALL_PERMISSIONS = ['change', 'delete']


class DashboardConfig:

    def __init__(self):
        self.last_read = 0
        self.schemes = [defaultScheme]
        self.ui_config = defaultUIConfig.copy()

    def check(self):
        if getmtime(settings.DASHBOARD_CONF) > self.last_read:
            self.load()

    def load(self):
        schemes = [defaultScheme]
        parser = ConfigParser()
        parser.read(settings.DASHBOARD_CONF)

        for option, default_value in defaultUIConfig.items():
            if parser.has_option('ui', option):
                try:
                    self.ui_config[option] = parser.getint('ui', option)
                except ValueError:
                    self.ui_config[option] = parser.get('ui', option)
            else:
                self.ui_config[option] = default_value

        if parser.has_option('ui', 'automatic_variants'):
            self.ui_config['automatic_variants'] = parser.getboolean(
                'ui', 'automatic_variants')
        else:
            self.ui_config['automatic_variants'] = True

        self.ui_config['keyboard_shortcuts'] = defaultKeyboardShortcuts.copy()
        if parser.has_section('keyboard-shortcuts'):
            self.ui_config['keyboard_shortcuts'].update(
                parser.items('keyboard-shortcuts'))

        for section in parser.sections():
            if section in ('ui', 'keyboard-shortcuts'):
                continue

            scheme = parser.get(section, 'scheme')
            fields = []

            for match in fieldRegex.finditer(scheme):
                field = match.group(1)
                if parser.has_option(section, '%s.label' % field):
                    label = parser.get(section, '%s.label' % field)
                else:
                    label = field

                fields.append({
                    'name': field,
                    'label': label
                })

            schemes.append({
                'name': section,
                'pattern': scheme,
                'fields': fields,
            })

        self.schemes = schemes


def get_permissions(user):
    """Return [change, delete] based on authorisation model and user privileges/groups."""
    if user and not user.is_authenticated():
        user = None
    if not settings.DASHBOARD_REQUIRE_AUTHENTICATION:
        return ALL_PERMISSIONS      # don't require login
    if not user:
        return []
    # from here on, we have a user
    permissions = ALL_PERMISSIONS
    if settings.DASHBOARD_REQUIRE_PERMISSIONS:
        permissions = [
            permission for permission in ALL_PERMISSIONS if user.has_perm(
                'dashboard.%s_dashboard' % permission)]
    editGroup = settings.DASHBOARD_REQUIRE_EDIT_GROUP
    if editGroup and len(user.groups.filter(name=editGroup)) == 0:
        permissions = []
    return permissions

config = DashboardConfig()
