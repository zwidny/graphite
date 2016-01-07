# -*- coding: utf-8 -*-
from __future__ import absolute_import

import datetime
import json

import pytz
from django.contrib.sites.models import RequestSite
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.utils.timezone import now, make_aware

from render.utils.attime import parseATTime
from .models import Event


def fetch(request):
    if request.GET.get("from") is not None:
        time_from = parseATTime(request.GET["from"])
    else:
        time_from = datetime.datetime.fromtimestamp(0)

    if request.GET.get("until") is not None:
        time_until = parseATTime(request.GET["until"])
    else:
        time_until = now()

    tags = request.GET.get("tags")
    if tags is not None:
        tags = request.GET.get("tags").split(" ")

    return [x.as_dict() for x in
            Event.find_events(time_from, time_until, tags=tags)]


def post_event(request):
    if request.method == 'POST':
        event = json.loads(request.body)
        assert isinstance(event, dict)

        if 'when' in event:
            when = make_aware(
                datetime.datetime.utcfromtimestamp(event['when']),
                pytz.utc)
        else:
            when = now()
        Event.objects.create(
            what=event['what'],
            tags=event.get("tags"),
            when=when,
            data=event.get("data", ""),
        )
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=405)


def view_events(request):
    if request.method == "GET":
        context = {'events': fetch(request),
                   'site': RequestSite(request),
                   'protocol': 'https' if request.is_secure() else 'http'}
        return render_to_response("events.html", context)
    else:
        return post_event(request)
