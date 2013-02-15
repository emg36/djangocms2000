from django import forms
from django.contrib import admin
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse_lazy
from django.utils.html import strip_tags
from django.utils.text import truncate_words

import settings as cms_settings
from forms import PageForm, ReadonlyInput
from models import Page, Block, Image


admin_js = (
    cms_settings.STATIC_URL + 'lib/jquery-1.4.2.min.js',
    cms_settings.STATIC_URL + 'tiny_mce/tiny_mce.js',
    cms_settings.STATIC_URL + 'tiny_mce/jquery.tinymce.js',
    cms_settings.STATIC_URL + 'js/page_admin.js',
    reverse_lazy('cms.views.page_admin_init'),
)
admin_css = {
    'all': (cms_settings.STATIC_URL + 'css/page_admin.css',),
}

class BlockForm(forms.ModelForm):
    class Meta:
        model = Block
    def __init__(self, *args, **kwargs):
        super(BlockForm, self).__init__(*args, **kwargs)

        # change the content widget based on the format of the block - a bit hacky but best we can do
        if 'instance' in kwargs:
            format = kwargs['instance'].format
            if format == 'attr':
                self.fields['content'].widget = forms.TextInput()                
            self.fields['content'].widget.attrs['class'] = " cms cms-%s" % format
        
        required_cb = cms_settings.BLOCK_REQUIRED_CALLBACK
        if callable(required_cb) and 'instance' in kwargs:
            self.fields['content'].required = required_cb(kwargs['instance'])


class BlockInline(generic.GenericTabularInline):
    model = Block
    max_num = 0
    fields = ('content',)
    form = BlockForm


class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
    def __init__(self, *args, **kwargs):
        super(ImageForm, self).__init__(*args, **kwargs)

        required_cb = cms_settings.IMAGE_REQUIRED_CALLBACK
        if callable(required_cb) and 'instance' in kwargs:
            self.fields['file'].required = required_cb(kwargs['instance'])


class ImageInline(generic.GenericTabularInline):
    model = Image
    max_num = 0
    exclude = ('label',)
    form = ImageForm


class CMSBaseAdmin(admin.ModelAdmin):
    inlines=[BlockInline,ImageInline,]
    list_display=['get_title',]
    save_on_top = True
    
    def get_title(self, obj):
        try:
            return strip_tags(obj.blocks.get(label="title").content)
        except Block.DoesNotExist:
            try:
                return strip_tags(obj.blocks.get(label="name").content)
            except Block.DoesNotExist:
                return obj.url
                
    class Media:
        js = admin_js
        css = admin_css
    class Meta:
        abstract=True

    
class PageAdmin(CMSBaseAdmin):
    list_display=['get_title', 'url', 'template', 'is_live', 'creation_date', 'view_on_site',]
    list_display_links=['get_title', 'url', ]

    list_filter=['site', 'template', 'is_live', 'creation_date',]
    
    def view_on_site(self, instance):
        return '<a href="%s" target="_blank">view page</a>' % (instance.get_absolute_url())
    view_on_site.allow_tags = True
    view_on_site.short_description = ' '
    
    
    search_fields = ['url', 'blocks__content', 'template',]
    form = PageForm
    exclude = []
    
if cms_settings.USE_SITES_FRAMEWORK:
    PageAdmin.list_display.append('site')
else:
    PageAdmin.exclude.append('site')
        
admin.site.register(Page, PageAdmin)


# Block/Image admin - restrict to just "site" blocks to avoid confusing the user
# Note - end users should only be given change permissions on these

class BlockFormSite(BlockForm):
    label = forms.CharField(widget=ReadonlyInput)

class BlockAdmin(admin.ModelAdmin):
    def queryset(self, request):
        '''TODO: this is a bit hacky, and might cause confusion - perhaps revisit?'''
        return Block.objects.filter(content_type=ContentType.objects.get_for_model(Site))

    form = BlockFormSite
    fields = ['label', 'content',]
    list_display = ['label_display', 'format', 'content_snippet',]
    search_fields = ['label', ]
    
    def label_display(self, obj):
        return obj.label.replace('-', ' ').replace('_', ' ').capitalize()
    label_display.short_description = 'label'
    label_display.admin_order_field = 'label'
    
    def content_snippet(self, obj):
        return truncate_words(strip_tags(obj.content), 10)
        
    class Media:
        js = admin_js
        css = admin_css

if cms_settings.USE_SITES_FRAMEWORK:
    BlockAdmin.list_display.append('content_object')

admin.site.register(Block, BlockAdmin)


class ImageFormSite(forms.ModelForm):
    class Meta:
        model = Image
    label = forms.CharField(widget=ReadonlyInput)


class ImageAdmin(admin.ModelAdmin):
    def queryset(self, request):
        if False and request.user.is_superuser:
            return Image.objects.all()
        else:
            return Image.objects.filter(content_type=ContentType.objects.get_for_model(Site))

    fields = ['label', 'file', 'description', ]
    list_display = ['label_display',]
    form = ImageFormSite
    search_fields = ['label', ]

if cms_settings.USE_SITES_FRAMEWORK:
    ImageAdmin.list_display.append('content_object')

admin.site.register(Image, ImageAdmin)
