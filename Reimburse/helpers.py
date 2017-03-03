from Reimburse.models import Reimburse
from employee.models import Employee


def manager(request, roles):
    # import ipdb; ipdb.set_trace()
    manager = Employee.objects.get(user_id=request.user.id)
    reportees = manager.Manager.filter(user__is_active=True)
    reportees_id = [employee.user for employee in reportees]
    reimburse = Reimburse.objects.filter(is_active=True,
                                         user__in=reportees_id,
                                         role=roles).exclude(process_status='Completed',
                                                                request_status__in=['Completed',
                                                                                    'Rolled Back'])
    return reimburse

def hr(request, roles):
    if request.user.groups.filter(name="myansrsourceHR"):
        return Reimburse.objects.filter(is_active=True,
                                        role=roles).exclude(process_status='Completed',
                                                            request_status__in=['Completed',
                                                                                'Rolled Back'])
    return None