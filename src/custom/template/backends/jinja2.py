# -*- coding: utf-8 -*-
from __future__ import absolute_import
from django.template.backends.jinja2 import Jinja2 as JinJa2


class Jinja2(JinJa2):
    app_dirname = 'templates'
