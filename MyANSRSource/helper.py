from CompanyMaster import models as company_model
from MyANSRSource import models as myansr_model
from django.db.models import Q


def get_my_project_list(requestee, pmflag=0):
    """
    :param requestee:
    :return Eligible Project's ID as list:
    """
    pm_delegate = myansr_model.ProjectDetail.objects.filter(pmDelegate_id=requestee.id)
    delivery_manager = myansr_model.ProjectDetail.objects.filter(deliveryManager_id=requestee.id)
    bu_head = company_model.BusinessUnit.objects.filter(new_bu_head=requestee)
    if bu_head:
        return myansr_model.Project.objects.filter(bu__in=bu_head).values('id')
    pmdelegate_id = myansr_model.ProjectDetail.objects.filter(pmDelegate_id=requestee.id).values('pmDelegate_id')
    if requestee.id == pmdelegate_id:
        if pm_delegate:
            return myansr_model.ProjectDetail.objects.filter(pmDelegate_id=requestee.id).values('project_id')
        if pm_delegate and requestee.is_superuser:
            return myansr_model.ProjectManager.objects.values('project__id')
    if requestee.id == delivery_manager:
        if delivery_manager:
            return myansr_model.ProjectDetail.objects.filter(deliveryManager_id=requestee.id).values('project_id')
        if delivery_manager and requestee.is_superuser:
            return myansr_model.ProjectManager.objects.values('project__id')
    if pmflag and requestee.is_superuser:
        return myansr_model.ProjectManager.objects.values('project__id')
    if pmflag:
        return myansr_model.ProjectManager.objects.filter(user=requestee).values('project__id')


    acc_mgmt = company_model.Customer.objects.filter(Q(Crelation=requestee) | Q(Cdelivery=requestee))
    pm = myansr_model.ProjectManager.objects.filter(user=requestee)
    if requestee.is_superuser:
        return myansr_model.Project.objects.all().values('id')

    elif acc_mgmt:
        return myansr_model.Project.objects.filter(customer__in=acc_mgmt).values('id')
    elif pm:
        return myansr_model.ProjectManager.objects.filter(user=requestee).values('project__id')
    else:
        return []
