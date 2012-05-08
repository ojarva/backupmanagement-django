from django.conf.urls.defaults import *
import os.path

from django.contrib import admin
admin.autodiscover()

from django.http import HttpResponse

def ping(request):
    return HttpResponse('status: OK')

urlpatterns = patterns('',
    url(r'^ping/$', ping),
    url(r'^management/static/(?P<path>.*)$', 'django.views.static.serve',  {'document_root': os.path.join(os.path.dirname(__file__), 'static')}),
    (r'^management/admin/', include(admin.site.urls)),
    url(r'^management/', include("management.urls")),
)
