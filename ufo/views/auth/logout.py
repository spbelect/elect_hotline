import django

from django.conf import settings
from django.contrib import auth
from django.shortcuts import redirect, render, get_object_or_404
from django.utils.translation import gettext_lazy as _

from ufo import api

@api.html.get('/auth/logout')
def logout(request):
    if not request.user.is_authenticated:
        return redirect('/')

    django.contrib.auth.logout(request)
    return redirect(request.META.get('HTTP_REFERER') or '/')

