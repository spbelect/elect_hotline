import sys

from django.contrib import admin
from django.shortcuts import get_object_or_404, render
from django.urls import include, path, re_path
from django.utils.translation import gettext as _
from rest_framework.urlpatterns import format_suffix_patterns

import debug_toolbar

import ufo
from ufo import api
from ufo import views

# Ninja html views
import ufo.views.account
import ufo.views.auth.login
import ufo.views.auth.logout
import ufo.views.auth.google
import ufo.views.home
import ufo.views.history
import ufo.views.organizations.id.show_form
import ufo.views.organizations.id.post_form
import ufo.views.organizations.id.join_applications
import ufo.views.organizations.list

from ufo.views import organizations_view

from ufo import mobile_api_v3 as apiv3
from ufo import old_internal_api


def handler403(request, exception):
    return render(request, '403.html')

def handler404(request, exception):
    return render(request, 'views/http_error.html', {
        'error': _("Page with given address does not exist")
    })


urlpatterns = [
    path('admin/', admin.site.urls),

    path('', ufo.api.html.urls),

    
    # API для мобильного приложения.
    path('api/v3/', include([path(*x) for x in (
        # GET
        ('<str:country>/regions/', apiv3.get_regions),
        ('<str:region>/elections/', apiv3.get_elections),
        ('<str:country>/questions/', apiv3.get_questions),
        ('<str:country>/questions/<str:id>/', apiv3.get_question),  # Не используется
        
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
    

    # DEPRECATED html views
    path('old/html/', include([
        path('organizations/', views.organizations_view.organizations),
        path('organizations/manage/<str:orgid>/campaigns/', views.organizations_view.manage_campaigns),
        path('organizations/manage/<str:orgid>/staff/', views.organizations_view.manage_staff),
        path('organizations/manage/<str:orgid>/tik_emails/', views.organizations_view.manage_tik_emails),

        path('history/', views.history_view.history),
        path('export_csv/', views.export_csv),

        # Лента ответов на анкету.
        path('feed/answers/', views.answers_feed),
        path('feed/more_answers/', views.more_answers),

        # Лента жалоб в ТИК.
        path('feed/tik_complaints/', views.tik_complaints_feed),

        path('auth/login/', views.auth_login),
        path('auth/logout/', views.auth_logout),

        path('users/', views.users),
    ])),

    #re_path(r'^protocols/$', protocols, name='protocols'),
    ##re_path(r'^protocol/(?P<id>\d+)/$', protocol, name='protocol'),
    #re_path(r'^region/(?P<region_id>\w*)/uik/(?P<uik>\w*)/$', uikview, name='uiks'),
    #re_path(r'^user/(?P<app_id>\w+)/$', usereventsview, name='userevents'),

    # DEPRECATED internal API
    path('api/internal/', include([path(*x) for x in (
        ('email/outbox/tik_complaints/', old_internal_api.send_tik_email),   # POST
        ('email/outbox/login_links/', old_internal_api.send_login_link),     # POST
        #('email/outbox/join_links/', old_internal_api.send_org_join_link),   # POST
        
        ('campaigns/', old_internal_api.campaigns),                   # POST
        ('campaigns/<str:pk>/', old_internal_api.campaign_edit),      # DELETE, PATCH
        
        
        ('orgs/', old_internal_api.organizations),           # POST
        ('orgs/<str:orgid>/', old_internal_api.org_edit),  # DELETE, PATCH
        
        ('orgs/<str:orgid>/members/', old_internal_api.org_members),  # POST
        ('orgs/<str:orgid>/members/<str:userid>/', old_internal_api.org_member_edit),  # DELETE, PATCH
        
        ('orgs/<str:orgid>/join_applications/', old_internal_api.org_join_applications),  # POST
        ('orgs/<str:orgid>/join_applications/<str:userid>', old_internal_api.org_join_application_edit), # DELETE
        
        ('org_branches/<str:id>/', old_internal_api.org_branch_edit),  # PATCH
        
        ('contacts/', old_internal_api.contacts),                     # POST
        ('contacts/<str:pk>/', old_internal_api.contact_edit),        # DELETE, PATCH
        
        ('profile/settings/', old_internal_api.settings),                      # POST
        ('profile/wipe_notifications/', old_internal_api.wipe_notifications),  # POST
    )])),
    
    path('select2/', include('django_select2.urls')),

]

if 'test' not in sys.argv:
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
