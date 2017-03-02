from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic.base import RedirectView
from MyANSRSource import apps
from django.conf import settings
from django.conf.urls.static import static


# Modify this to change the title from "Django Administration"

admin.site.site_header = apps.MyANSRSourceConfig.verbose_name +  \
    ' - Management UI'

urlpatterns = [
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
                       url(r'^salesforce/', include('Salesforce.urls')),
                       url(r'^bookings/', include('BookMyRoom.urls')),
                       url(r'^leave/', include('Leave.urls')),
                       url(r'^hire/', include('Hire.urls')),
                       url(r'^library/', include('Library.urls')),
                       url(r'^exitapp/', include('ExitApp.urls')),
                       url(r'^skillset/', include('skillset.urls')),
                       ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
