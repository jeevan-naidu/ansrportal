from django.contrib.auth.models import User
from Reimburse.models import Reimburse, Transaction


def manager(request, roles):
    user = User.objects.filter()
    reimburse = Reimburse.objects.filter(is_active=True, user__in=user).exclude(process_status='Completed',
                                                                request_status__in=['Completed',
                                                                                    'Rolled Back'])
    return reimburse