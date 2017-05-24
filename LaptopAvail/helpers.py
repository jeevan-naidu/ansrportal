from LaptopAvail.models import LaptopApply
from employee.models import Employee


def manager(request, roles):
    manager = Employee.objects.get(user_id=request.user.id)
    reportees = manager.Manager.filter(user__is_active=True)
    reportees_id = [employee.user for employee in reportees]
    avail_active = LaptopApply.objects.filter(is_active=True,
                                              user__in=reportees_id,
                                              role=roles).exclude(process_status='Completed',
                                                                  request_status__in=['Completed',
                                                                                      'Rolled Back'])
    avail_inactive = LaptopApply.objects.filter(is_active=False,
                                                user__in=reportees_id,
                                                process_status='Completed'
                                    )
    return avail_active, avail_inactive


def admin(request, roles):
    if request.user.groups.filter(name="LaptopAdmin"):
        avail_active = LaptopApply.objects.filter(is_active=True,
                                                  role=roles).exclude(process_status='Completed',
                                                                      request_status__in=['Completed',
                                                                                          'Rolled Back'])
        avail_inactive = LaptopApply.objects.filter(is_active=False, process_status='Completed')
        return avail_active, avail_inactive
    return None

