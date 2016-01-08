# -*- coding: utf-8 -*-
from __future__ import absolute_import
from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.template import loader
from django.shortcuts import render_to_response
from utils import getProfile


def login_view(request):
    template = loader.get_template('login.html')
    if request.method == 'GET':
        next_page = request.GET.get('nextPage', reverse('browser'))
        context = {'nextPage': next_page}
        return HttpResponse(template.render(context, request))
    elif request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        next_page = request.POST.get('nextPage', reverse('browser'))
        user = authenticate(username=username, password=password)
        if user is None:
            return HttpResponse(template.render({'authenticationFailed': True, 'nextPage': next_page}, request))
        elif not user.is_active:
            return HttpResponse(template.render({'accountDisabled': True, 'nextPage': next_page}, request))
        else:
            login(request, user)
            return HttpResponseRedirect(next_page)


def logoutView(request):
    nextPage = request.GET.get('nextPage', reverse('browser'))
    logout(request)
    return HttpResponseRedirect(nextPage)


def editProfile(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('browser'))
    context = {'profile': getProfile(request)}
    return render_to_response("editProfile.html", context)


def updateProfile(request):
    profile = getProfile(request, allowDefault=False)
    if profile:
        profile.advancedUI = request.POST.get('advancedUI', 'off') == 'on'
        profile.save()
    nextPage = request.POST.get('nextPage', reverse('browser'))
    return HttpResponseRedirect(nextPage)
