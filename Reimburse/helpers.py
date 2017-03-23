from Reimburse.models import Reimburse
from employee.models import Employee


def manager(request, roles):
    manager = Employee.objects.get(user_id=request.user.id)
    reportees = manager.Manager.filter(user__is_active=True)
    reportees_id = [employee.user for employee in reportees]
    reimburse_active = Reimburse.objects.filter(is_active=True,
                                         user__in=reportees_id,
                                         role=roles).exclude(process_status='Completed',
                                                                request_status__in=['Completed',
                                                                                    'Rolled Back'])
    reimburse_inactive = Reimburse.objects.filter(is_active=False,
                                         user__in=reportees_id,
                                                  process_status='Completed'
                                                  )
    return reimburse_active, reimburse_inactive

def hr(request, roles):
    if request.user.groups.filter(name="Finance"):
        reimburse_active = Reimburse.objects.filter(is_active=True,
                                                    role=roles).exclude(process_status='Completed',
                                                                        request_status__in=['Completed',
                                                                                            'Rolled Back'])
        reimburse_inactive = Reimburse.objects.filter(is_active=False, process_status='Completed')
        return reimburse_active, reimburse_inactive
    return None


def admin(request, roles):
    if request.user.groups.filter(name="BookingRoomAdmin"):
        reimburse_active = Reimburse.objects.filter(is_active=True,
                                                    role=roles).exclude(process_status='Completed',
                                                                        request_status__in=['Completed',
                                                                                            'Rolled Back'])
        reimburse_inactive = Reimburse.objects.filter(is_active=False, process_status='Completed')
        return reimburse_active, reimburse_inactive
    return None