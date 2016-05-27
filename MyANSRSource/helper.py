from CompanyMaster import models as company_model
from MyANSRSource import models as myansr_model
from django.db.models import Q


def get_my_project_list(requestee):
    """
    :param requestee:
    :return Eligible Project's ID as list:
    """
    
    bu_head = company_model.BusinessUnit.objects.filter(new_bu_head=requestee)
    acc_mgmt = company_model.Customer.objects.filter(Q(Crelation=requestee) | Q(Cdelivery=requestee))
    pm = myansr_model.ProjectManager.objects.filter(user=requestee)

    if bu_head:
        return myansr_model.Project.objects.filter(bu__in=bu_head).values('id')
    elif acc_mgmt:
        return myansr_model.Project.objects.filter(customer__in=acc_mgmt).values('id')
    elif pm:
        return myansr_model.ProjectManager.objects.filter(user=requestee).values('project__id')
    else:
        return []

