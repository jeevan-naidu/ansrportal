from django.core.exceptions import PermissionDenied
from django.conf import settings
import re
from django.http import Http404
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import Group


class GrievancePermissionCheckMiddleware(object):
    def __init__(self):
        """
         init will determine which url to be examined before serving to user, here its grievanceAdmin app url
        """
        self.restricted = tuple([(re.compile(url[0], )) for url in settings.RESTRICTED_URLS])

    def process_view(self, request, view_func, view_args, view_kwargs):
        for rule in self.restricted:
            if rule.match(request.path):
                if request.user.groups.filter(name=settings.GRIEVANCE_ADMIN_GROUP_NAME).exists():
                    return None  # allow the users who is in the group
                else:
                    raise PermissionDenied("You Don't Have The Privilege To Access This Page")  # raise 403 error
            return None  # rest of the urls,allow them
