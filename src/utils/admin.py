from django.contrib import admin
from django import forms

def register(model):
    def wrapper(cls):
        admin.site.register(model, cls)
        return cls
    return wrapper

def pop_subset(fields, *args):
    for item in args:
        if isinstance(item, (str, unicode)):
            fields -= set([item])
        else:
            fields -= set(item)
    return args


class BaseAdmin(object):
    textfield_size = {}
    cache_choices = []
    
    def formfield_for_dbfield(self, dbfield, request, **kwargs):
        for names, size in self.textfield_size.items():
            if dbfield.name in names:
                return dbfield.formfield(widget=forms.TextInput(attrs={'size': size, }))
                
        formfield = super().formfield_for_dbfield(dbfield, request=request, **kwargs)
        if dbfield.name in self.cache_choices:
            if isinstance(self, admin.options.InlineModelAdmin):
                # dirty trick so queryset is evaluated and cached in .choices
                formfield.choices = formfield.choices
            else:
                choices_cache = getattr(request, dbfield.name + '_choices_cache', None)
                if choices_cache is not None:
                    formfield.choices = choices_cache
                else:
                    setattr(request, dbfield.name + '_choices_cache', formfield.choices)
        return formfield
        
        
    def get_fieldsets(self, *args):
        fs = super().get_fieldsets(*args)
        if hasattr(self, 'make_fs'):
            return self.make_fs(set(fs[0][1]['fields']))
        return fs
        
    

        

class SeoAdmin(BaseAdmin):
    search_fields = ('name','html_h1','html_title',)
    seo_classes = []
    seo_fields = ['html_title', 'html_h1', 'meta_description', 'meta_keywords']
    
    def make_seo_fs(self, fields):
        return ('SEO', {'fields': pop_subset(fields, *self.seo_fields), 'classes': self.seo_classes})
    
    def make_fs(self, fields):
        return [
            (None, {'fields': pop_subset(fields, 'name')}),
            self.make_seo_fs(fields), 
            (None, {'fields': fields}), 
        ]
        
        

class PageAdmin(SeoAdmin):
    seo_classes = ['realigned', 'collapse']
    seo_fields = ['html_title', 'html_h1', 'slug', 'meta_description', 'meta_keywords']
    prepopulated_fields = {"slug": ("name",)}
    
    

class LinkedTabularInline(admin.options.InlineModelAdmin):
    template = "admin/tabular_linked_inline.html"
    admin_model_path = None

    def __init__(self, *args):
        super().__init__(*args)
        if self.admin_model_path is None:
            self.admin_model_path = self.model.__name__.lower()
