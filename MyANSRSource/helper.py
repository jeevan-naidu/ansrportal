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
    portfolio_manager = myansr_model.ProjectDetail.objects.filter(portfolio_manager_id=requestee.id)
    delivery_manager = myansr_model.ProjectDetail.objects.filter(deliveryManager_id=requestee.id)
    pm = myansr_model.ProjectManager.objects.filter(user=requestee)
    acc_mgmt = company_model.Customer.objects.filter(Q(Crelation=requestee) | Q(Cdelivery=requestee))

    if requestee.is_superuser:
        return myansr_model.Project.objects.all().values('id')

    elif bu_head:
        return myansr_model.Project.objects.filter(bu__in=bu_head).values('id')

    elif pm_delegate or delivery_manager or portfolio_manager or pm:
        newlist = []
        project_list = myansr_model.ProjectDetail.objects.filter(
            Q(deliveryManager_id=requestee.id) | Q(pmDelegate_id=requestee.id) | Q(
                portfolio_manager_id=requestee.id)).values('project_id')
        for val in project_list:
            newlist.append(val['project_id'])

        return projectidlist(newlist, requestee)

    elif acc_mgmt:
        return myansr_model.Project.objects.filter(customer__in=acc_mgmt).values('id')
    else:
        return []

def projectidlist(newlist, requestee):
    pm_list = myansr_model.ProjectManager.objects.filter(user=requestee).values('project__id')
    for val in pm_list:
        newlist.append(val['project__id'])
        list(set(newlist))
    return list(set(newlist))
