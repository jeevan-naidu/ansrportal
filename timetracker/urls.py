import autocomplete_light
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic.base import RedirectView
from MyANSRSource import apps
from django.conf import settings
from django.conf.urls.static import static

autocomplete_light.autodiscover()
admin.autodiscover()

# Modify this to change the title from "Django Administration"

admin.site.site_header = apps.MyANSRSourceConfig.verbose_name +  \
    ' - Management UI'

urlpatterns = patterns('',
                       url(r'^autocomplete/',
                           include('autocomplete_light.urls')),
                       url(r'^grappelli/', include('grappelli.urls')),
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^fb360/', include('fb360.urls')),
                       url(r'^myansrsource/', include('MyANSRSource.urls')),
                       url(r'session_security/',
                           include('session_security.urls')
                           ),
                       url(r'^$', RedirectView.as_view(url='/myansrsource/')),
                       url(r'^grievances/', include('Grievances.urls')),
                       url(r'^grievances_admin/', include('GrievanceAdmin.urls')),
                       url(r'^reports/', include('Reports.urls')),
                       url(r'^leave/', include('Leave.urls')),
                       
                       ) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
