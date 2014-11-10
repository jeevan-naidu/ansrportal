from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic.base import RedirectView
from timesheet import apps
from employee.views import logincred

admin.autodiscover()

# Modify this to change the title from "Django Administration"

admin.site.site_header = apps.TimesheetConfig.verbose_name + ' - Management UI'

urlpatterns = patterns('',
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^timesheet/', include('timesheet.urls')),
                       url(r'^chaining/', include('smart_selects.urls')),
		       url(r'^login$', 'employee.views.logincred', name='logincred'),
                       url(r'^$', RedirectView.as_view(url='/timesheet/')),
                       )
