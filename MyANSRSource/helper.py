from CompanyMaster import models as company_model
from MyANSRSource import models as myansr_model
from django.db.models import Q


def get_my_project_list(requestee, pmflag=0):
    """
    :param requestee:
    :return Eligible Project's ID as list:
    """
    pm_delegate = myansr_model.ProjectDetail.objects.filter(pmDelegate_id=requestee.id)
    bu_head = company_model.BusinessUnit.objects.filter(new_bu_head=requestee)
    delivery_manager = myansr_model.ProjectDetail.objects.filter(deliveryManager_id=requestee.id)
    if bu_head:
        if requestee.is_superuser:
            return myansr_model.Project.objects.all().values('id')
        else:
            return myansr_model.Project.objects.filter(bu__in=bu_head).values('id')
    if pm_delegate or delivery_manager:

        if requestee.is_superuser:
            return myansr_model.Project.objects.all().values('id')
        else:
            return myansr_model.ProjectDetail.objects.filter(Q(deliveryManager_id=requestee.id) | Q(pmDelegate_id=requestee.id) ).values('project_id')

    if pmflag and requestee.is_superuser:
        return myansr_model.ProjectManager.objects.values('project__id')
    if pmflag:
        print "pmflag"
        return myansr_model.ProjectManager.objects.filter(user=requestee).values('project__id')


    acc_mgmt = company_model.Customer.objects.filter(Q(Crelation=requestee) | Q(Cdelivery=requestee))
    pm = myansr_model.ProjectManager.objects.filter(user=requestee)
    if requestee.is_superuser:
        return myansr_model.Project.objects.all().values('id')

    elif acc_mgmt:
        return myansr_model.Project.objects.filter(customer__in=acc_mgmt).values('id')
    elif pm:
        print "pm"
        return myansr_model.ProjectManager.objects.filter(user=requestee).values('project__id')
    else:
        return []
