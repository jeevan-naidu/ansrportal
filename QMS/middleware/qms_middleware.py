from django.core.exceptions import PermissionDenied
from django.utils import timezone
import datetime
import logging
import re
from django.http import HttpResponseRedirect
from GrievanceAdmin.middleware.grievanceadminmiddleware import get_client_ip

logger = logging.getLogger('MyANSRSource')


def log_qms(request):
    logger.error("This User is tried to"
                 " access QMS admin module "
                 "{0}  and the ip address is : {1} and the path :{2} "
                 " Date Time is {3}".format(request.user,
                                            get_client_ip(request), request.path,
                                            timezone.make_aware(datetime.datetime.now(),
                                                                timezone.get_default_timezone())))


class QMSPermissionCheckMiddleware(object):
    def process_view(self, request, view_func, view_args, view_kwargs):
        restricted_urls = ['/qms/choose_tabs/', '/qms/dashboard/']
        if request.path in restricted_urls and not request.user.groups.filter(
                    name='myansrsourcePM').exists():
            log_qms(request)
            raise PermissionDenied("Sorry You Don't Have Permission To Access This Feature")  # raise 403 error
