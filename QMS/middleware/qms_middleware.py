from django.core.exceptions import PermissionDenied
from django.conf import settings
from django.utils import timezone
import datetime
import re
import logging

logger = logging.getLogger('MyANSRSource')


# def get_client_ip(request):
#     x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
#     if x_forwarded_for:
#         ip = x_forwarded_for.split(',')[0]
#     else:
#         ip = request.META.get('REMOTE_ADDR')
#     return ip


class QMSPermissionCheckMiddleware(object):
    def process_view(self, request, view_func, view_args, view_kwargs):
        if 'qms' in request.path and not request.user.is_authenticated():
            # logger.error("This User is tried to"
            #              " access grievance admin module "
            #              "{0}  and the ip address is : {1} "
            #              " Date Time is {2}".format(request.user,
            #                                         get_client_ip(request),
            #                                         timezone.make_aware(datetime.datetime.now(),
            #                                                             timezone.get_default_timezone())))

            raise PermissionDenied("Sorry You Don't Have Permission To Access This Feature")  # raise 403 error
            # return None  # rest of the urls,allow them
