from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'sniff.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'main.views.home'),
    url(r'^home/$', 'main.views.home'),
    url(r'^work/$', 'main.views.work'),
    url(r'^read_config_file/$', 'main.views.read_config_file'),
    url(r'^save_config_file/$', 'main.views.save_config_file'),
    url(r'^get_config_file/$', 'main.views.get_config_file'),
    url(r'^save_update_config_file/$', 'main.views.save_update_config_file'),
)
