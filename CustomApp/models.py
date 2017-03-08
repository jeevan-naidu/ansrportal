from django.contrib.auth.models import User, Group
from django.db.models import (
    Model,
    DateTimeField,
    BooleanField,
    CharField,
    ForeignKey)
from helpers import get_request_params, flow_config
from constants import TASK_STATUS, REQUEST_STATUS


class AbstractEntity(Model):
    """Common attributes for all models"""
    role = CharField(verbose_name="role", max_length=30, default="submitter")
    creation_date = DateTimeField('Creation Date', auto_now_add=True)
    last_updated = DateTimeField('Last Updated', auto_now=True)

    class Meta(object):
        abstract = True

    @property
    def class_meta(self):
        """Returns class meta"""
        return self._meta

    @property
    def module_label(self):
        """Returns module label"""
        return self.class_meta.app_label

    @property
    def code(self):
        """Returns a unique code"""
        return "{0}-{1}-{2}".format(
            self.class_meta.app_label,
            self.title,
            self.id)

    def __unicode__(self):
        """Returns ID"""
        return str(self.id)


class AbstractProcess(AbstractEntity):
    user = ForeignKey(User, related_name='%(class)s_requested_by')
    is_active = BooleanField('Is Active', default=True)
    process_status = CharField(choices=TASK_STATUS, max_length=20, default="In Progress")
    request_status = CharField(choices=REQUEST_STATUS, max_length=20, default="Initiated")

    class Meta:
        abstract = True


def get_app_detail(request, **kwargs):
    app_title = get_request_params('app_name', request, **kwargs)
    config = flow_config(app_title)
    return config


def manager_queryset(request, **kwargs):
    config = get_app_detail(request, **kwargs)
    queryset = can_approve(request, config)
    return queryset

def user_queryset(request, config):
    queryset = {}
    model = config.PROCESS[config.INITIAL]['model']
    queryset['active'] = model.objects.filter(user=request.user,
                                              is_active=True)
    queryset['inactive'] = model.objects.filter(user=request.user,
                                                is_active=False).exclude(process_status__in=['Rolled Back'])
    queryset['rollback'] = model.objects.filter(user=request.user,
                                                is_active=False).exclude(request_status__in=['Completed'])
    return queryset


def can_approve(request, config):
    model = config.PROCESS[config.INITIAL]['model']
    role = config.PROCESS[config.INITIAL]['role']
    transition = config.PROCESS[config.INITIAL]['transitions']
    queryset_active = model.objects.none()
    queryset_inactive = model.objects.none()
    while transition[0]:
        next_transition = transition[0]
        method = config.PROCESS[next_transition]['method']
        access = method(request, role)
        role = config.PROCESS[next_transition]['role']
        if access:
            queryset_active = queryset_active | access[0]
            queryset_inactive = queryset_inactive | access[1]
        transition = config.PROCESS[next_transition]['transitions']
    return queryset_active, queryset_inactive


def get_role(config, status, current_role):
    result_role = config.PROCESS[config.INITIAL]['role']
    transition = config.PROCESS[config.INITIAL]['transitions']
    role = result_role
    while transition[0]:
        if current_role == role:
            if status == "approve":
                result_role = config.PROCESS[transition[0]]['role']
            elif transition[1]:
                result_role = config.PROCESS[transition[1]]['role']
        role = config.PROCESS[transition[0]]['role']
        transition = config.PROCESS[transition[0]]['transitions']
    return result_role


def update_process(process, role, status, final):
    if status == "approve" and final:
        process.role = role
        process.process_status = "Completed"
        process.request_status = "Completed"
        process.is_active = False
        process.save()
    elif status == "approve":
        process.role = role
        process.process_status = "Initiated"
        process.request_status = "In Progress"
        process.save()
    else:
        process.role = role
        process.save()


def is_final(config, current_role):
    role = get_final_role(config)
    if role == current_role:
        flag = True
    else:
        flag = False
    return flag


def get_final_role(config):
    final_role = ""
    transition = config.PROCESS[config.INITIAL]['transitions']
    for i in range(20):
        if not transition[0]:
            final_role = config.PROCESS[transition[1]]['role']
            break
        transition = config.PROCESS[transition[0]]['transitions']
    return final_role


def get_app_name(request, **kwargs):
    app_title = get_request_params('app_name', request, **kwargs)
    return app_title


def get_process_transactions(modal, transaction_modal):
    """
    this methods uses for getting all the Fields for grid view
    :return: Fields
    """
    abstract_fields = ['creation_date', 'last_updated', 'is_active', transaction_modal]
    fields = [f.name for f in modal._meta.get_fields()]
    fields = filter(lambda x: x not in abstract_fields, fields)
    fields.sort(reverse=True)
    return fields












