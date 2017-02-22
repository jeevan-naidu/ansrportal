from django.contrib.auth.models import User
from Invoice.models import Invoice


def manager(request, roles):
    user = User.objects.filter()
    reimburse = Invoice.objects.filter(is_active=True, user__in=user).exclude(process_status='Completed',
                                                                request_status__in=['Completed',
                                                                                    'Rolled Back'])
    return reimburse