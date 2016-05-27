from django.conf.urls import patterns, url
from views import UploadSalesforceDataView
from django.contrib.auth.decorators import login_required
from Grievances import views
urlpatterns = patterns(u'',
                       url(r'^upload-file/$', login_required(UploadSalesforceDataView.as_view()), name=u'upload_file'),
                       
                       )