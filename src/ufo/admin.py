from adminsortable2.admin import SortableInlineAdminMixin, SortableAdminMixin
#from django.urls import reverse
from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
#from django.contrib.postgres.forms import JSONField
from django.db.models import JSONField
from django.db.models import TextField
from django.forms import Field, Widget, Textarea, TextInput
from django.utils.safestring import mark_safe

from django_jsonform.widgets import JSONFormWidget
from django_pydantic_field.v2.fields import PydanticSchemaField
from prettyjson import PrettyJSONWidget

from utils.admin import LinkedTabularInline

from . import models

#from django.forms.field import Widget

class BaseAdmin(admin.ModelAdmin):
    readonly_fields = ('time_created',)
    

def override_fields(**overrides):
    """
    Override form fields or widgets.
    
    Usage:
    
    > from prettyjson import PrettyJSONWidget
    > from django.contrib.postgres.forms import JSONField
    > 
    > class MyAdmin(admin.ModelAdmin):
    >     formfield_for_dbfield = override_fields(
    >         data1 = JSONField(widget=PrettyJSONWidget()),  # Override formfield.
    >         data2 = PrettyJSONWidget(),   # Or just widget.
    >     )
    """
    def formfield_for_dbfield(self, dbfield, request, **kwargs):
        if dbfield.name not in overrides:
            return admin.ModelAdmin.formfield_for_dbfield(self, dbfield, request=request, **kwargs)

        override = overrides[dbfield.name]
        if isinstance(override, Field):
            return override  # FormField was specified.
        else:
            return dbfield.formfield(widget=override)
        #return dbfield.formfield(widget=forms.TextInput(attrs={'size': size, }))
    return formfield_for_dbfield


    
#pretty_json = {
    #JSONField: {'widget': prettyjson.PrettyJSONWidget(
        ## Does not work with `readonly_fields`:
        ## See BUG https://github.com/kevinmickey/django-prettyjson/issues/21
        ## Just make all json widgets disabled for now.
        #attrs={'initial': 'parsed', 'disabled': True}
    #)}
#}


#class PrettyJSON(Widget):
    #def render(self, name, value, attrs=None, renderer=None):
        #kvs = '\n'.join('%s\n   %s' % (k, v) for k, v in json.loads(value).items())
        #return '<pre style="clear:both">%s</pre>' % kvs


class QuestionInline(SortableInlineAdminMixin, admin.TabularInline):
    fields = ('question',)
    raw_id_fields = ('question',)
    model = models.QuizTopic.questions.through
    extra = 0
    #show_change_link = True
    #has_change_permission = lambda *a: False
    
#class TikSubscriptionInline(BaseInline, admin.StackedInline):
    #ordering = ('campaign', 'tik__name')

def inline(model, base, **kw):
    #args = dict(kw, extra=0, model=model, formfield_overrides=pretty_json)
    #import ipdb; ipdb.sset_trace()
    model = getattr(models, model)
    if 'time_created' in dir(model):
        kw.setdefault('readonly_fields', ('time_created',))
    return type(f'{model}Inline', (base,), dict(kw, extra=0, model=model))

stacked = lambda model, **kw: inline(model, admin.StackedInline, **kw)
tabbed = lambda model, **kw: inline(model, admin.TabularInline, **kw)


class Answer_Admin(admin.ModelAdmin):
    list_display = (
        'timestamp', 'who', 'label', 'val', 'revoked',
        'time_tik_email_request_created', 'tik_complaint_status', 'region'
    )
    list_filter = (
        'tik_complaint_status', 'region', 'uik_complaint_status', 'appuser__email',
    )
    ordering = ('-timestamp',)
    # readonly_fields = ('timestamp',)

    def val(self, obj):
        return obj.value_bool if obj.question.type == 'YESNO' else obj.value_int
    
    def label(self, obj):
        return obj.question.label[:30]
    
    def who(self, obj):
        return obj.operator or obj.appuser


class Campaign_Admin(BaseAdmin):
    list_display = ('election', 'id', 'organization')
    inlines = [
        # stacked('Contact'),
        #stacked('CampaignPhone'), 
        #stacked('TikSubscription')
    ]

class ClientError_Admin(admin.ModelAdmin):
    list_display = ('timestamp', 'app_id', 'error')
    readonly_fields = ('timestamp', 'time_created')

    def app_id(self, obj):
        return obj.data.get('app_id', 'xz')

    def error(self, obj):
        msg = obj.data.get('traceback', '') or obj.data.get('msg', '')
        errors = '<br/>'.join(msg.split('\n'))
        return mark_safe(errors)

    formfield_for_dbfield = override_fields(data=PrettyJSONWidget())



class Election_Admin(BaseAdmin):
    search_fields = ('name',)
    list_display = ('name', 'date', 'region')
    inlines = [stacked('Campaign')]
    

class MobileUser_Admin(BaseAdmin):
    #textfield_size = {('first_name'): 100}
    list_display = ('first_name', 'last_name', 'uik', 'region')
    inlines = [
        stacked('ElectionMobileUsers', readonly_fields=('election',))
    ]
    formfield_overrides = {
        TextField: {'widget': Textarea(attrs={'rows': 1})},
    }

    

class Munokrug_Admin(BaseAdmin):
    list_display = ('name', 'district', 'uik_ranges',)
    list_filter = ['district']
    
    
class OrgBranch_Admin(admin.ModelAdmin):
    #textfield_size = {('name'): 100}
    list_display = ('id', 'organization', 'region')
    # list_editable = ('name',)
    inlines = [
        # stacked('Campaign'),
        # stacked('Contact'),
        #stacked('OrganizationPhone'),
    ]


class OrgJoinApplication_Admin(BaseAdmin, admin.ModelAdmin):
    #textfield_size = {('name'): 100}
    list_display = ('organization', 'user', 'time_created')


class Organization_Admin(BaseAdmin, admin.ModelAdmin):
    #textfield_size = {('name'): 100}
    list_display = ('id', 'name', 'qregions', 'creator')
    list_editable = ('name',)
    inlines = [
        stacked('Campaign'), 
        stacked('Contact'), 
        stacked('OrgBranch'),
    ]

    def qregions(self, org: models.Organization):
        return mark_safe(', '.join(org.regions.values_list('name', flat=True)))


class Question_Admin(admin.ModelAdmin):
    search_fields = ('label',)
    list_display = ('label', 'id',)
    readonly_fields = ('qtopics', 'time_created', 'id', 'type')
    list_filter = ['topics']

    def qtopics(self, obj):
        return mark_safe(', '.join('<a href="/admin/ufo/quiztopic/%s/change/">%s<a>' % (x.pk, x) for x in obj.topics.all()))

    formfield_overrides = {
        TextField: {'widget': Textarea(attrs={'rows': 1})},
        JSONField: {'widget': Textarea(attrs={'rows': 1})},
        # JSONField: {'widget': JSONFormWidget(attrs={'rows': 1, 'initial': 'parsed'}, schema={
        #     'type': 'dict',
        # })}
    }
    

class QuizTopic_Admin(SortableAdminMixin, BaseAdmin):
    search_fields = ('name',)
    list_display = ('name',)
    #list_filter=('form_type',)
    inlines = [QuestionInline]

    formfield_overrides = { TextField: {'widget': TextInput(attrs={'size': 60})} }

class Region_Admin(BaseAdmin):
    search_fields = ('name',)
    list_display = ('name', 'external_id')


class Tik_Admin(BaseAdmin):
    list_display = ('name', 'region', 'uik_ranges')
    list_filter = ('region', )
    #ordering = ('-timestamp',)
    inlines = [stacked('TikSubscription')]

    formfield_overrides = {
        PydanticSchemaField: {"widget": JSONFormWidget},
    }
    
class TikSubscription_Admin(BaseAdmin):
    list_display = ('id', 'tik', 'email', 'organization')
    list_filter = ('organization', )
    list_editable = ('tik', 'email', )
    ordering = ('organization', 'tik__name')



from django.utils.translation import gettext, gettext_lazy as _


class WebsiteUser_Admin(UserAdmin):
    filter_horizontal = ('user_permissions', 'groups')
    ordering = ('email',)

    search_fields = ('first_name', 'last_name', 'email')
    list_display = ('email', 'date_joined', 'last_login')
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('password1', 'password2'),
        }),
    )
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (None, {'fields': ('unread_notifications', 'utc_offset',)}),
    )

    inlines = [
        tabbed(
            'Organization', 
            fk_name='creator', 
            fields=['name'], 
            readonly_fields=['name'],
            verbose_name_plural='owned_orgs',
            has_change_permission=lambda *a: False
        ),
        tabbed('OrgMembership', has_change_permission=lambda *a: False)
    ]


for name, klass in dict(locals()).items():
    modelname, _, suffix = name.rpartition('_')
    if not suffix == 'Admin':
        continue
    admin.site.register(getattr(models, modelname), klass)
