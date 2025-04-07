import sys

from django.contrib import admin
from django.conf import settings
from django.shortcuts import get_object_or_404, render
from django.urls import include, path, re_path
from django.utils.translation import gettext as _
from rest_framework.urlpatterns import format_suffix_patterns

import debug_toolbar

import ufo
from ufo import api
from ufo import views

# Mobile api v4
import ufo.mobile_api_v4.country.get_regions
import ufo.mobile_api_v4.country.get_questions
import ufo.mobile_api_v4.region.get_elections
import ufo.mobile_api_v4.region.get_organizations
import ufo.mobile_api_v4.answers

# Ninja html views
import ufo.views.answers.history
import ufo.views.answers.stream
import ufo.views.auth.login
import ufo.views.auth.logout
import ufo.views.auth.google
import ufo.views.organizations.id.show_form
import ufo.views.organizations.id.contacts.show_form
import ufo.views.organizations.id.contacts.id.post
import ufo.views.organizations.id.contacts.id.delete
import ufo.views.organizations.id.post_form
import ufo.views.organizations.id.branches.show_form
import ufo.views.organizations.id.branches.post_form
import ufo.views.organizations.id.join_applications
import ufo.views.organizations.list
import ufo.views.account
import ufo.views.home

from ufo import mobile_api_v3 as apiv3


def handler403(request, exception):
    return render(request, 'views/http_error.html', {
        'error': _("Page is not accessible")
    }, status=403)

def handler404(request, exception):
    if getattr(settings, 'RAISE_404', False):
        raise exception
    return render(request, 'views/http_error.html', {
        'error': _("Page with given address does not exist")
    }, status=404)


urlpatterns = [
    path('admin/', admin.site.urls),

    # HTML web pages
    path('', ufo.api.html.urls),

    # Moblie API v4
    path('api/v4/', ufo.api.v4.urls),

    # Mobile API v3
    path('api/v3/', include([path(*x) for x in (
        # GET
        ('<str:country>/regions/', apiv3.get_regions),
        ('<str:region>/elections/', apiv3.get_elections),
        ('<str:country>/questions/', apiv3.get_questions),
        ('<str:country>/questions/<str:id>/', apiv3.get_question),  # Not used
        
        # POST/PATCH
        ('userprofile/', apiv3.post_userprofile),
        ('position/', apiv3.post_position),
        ('answers/', apiv3.post_answer),
        ('answers/<str:answerid>/', apiv3.patch_answer),
        ('answers/<str:answerid>/images/', apiv3.post_image_metadata),
        ('answers/<str:answerid>/images/<str:md5>', apiv3.patch_image_metadata),
        ('upload_slot/', apiv3.upload_slot),
        
        # debug POST
        ('errors/', apiv3.post_errors),
    )])),

    path('', include('django_prometheus.urls')),
]

if 'test' not in sys.argv:
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
