from django.urls import re_path

from . import views


urlpatterns = (
    re_path(r'^actions/savepage/$', views.savepage, {}, 'cms_savepage'),
    re_path(r'^actions/savepage/(\d+)/$', views.savepage, {}, 'cms_savepage'),
    re_path(r'^actions/saveblock/(\d+)$', views.saveblock, {}, 'cms_saveblock'),
    re_path(r'^actions/saveimage/(\d+)$', views.saveimage, {}, 'cms_saveimage'),

    re_path(r'^login/$', views.login, {}, 'cms_login'),
    re_path(r'^logout/$', views.logout, {}, 'cms_logout'),
    re_path(r'^block_admin_init\.js$', views.block_admin_init, {},
        'cms_block_admin_init'),
    re_path(r'^linklist\.js$', views.linklist, {}, 'cms_linklist'),
    re_path(r'^editor\.js$', views.editor_js, {}, 'cms_editor_js'),
    re_path(r'^editor\.html$', views.editor_html, {}, 'cms_editor_html'),
    re_path(r'^login\.js$', views.login_js, {}, 'cms_login_js'),
)
