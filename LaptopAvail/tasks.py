from celery.registry import tasks
from celery.task import Task
from django.core.mail import EmailMessage
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from employee.models import Employee
from django.conf import settings
import datetime
from django.utils import timezone
import logging
logger = logging.getLogger('MyANSRSource')


def manger_detail(user):
    return Employee.objects.get(employee_assigned_id=user.employee.manager_id).user.email


def admin_detail():
    return [user.email for user in User.objects.filter(groups__name='LaptopAdmin')]


class LaptopRaiseEmail(Task):

    def run(self, laptop_raise, flag, role, status):
        manager_email = manger_detail(laptop_raise.user)
        admin_email = admin_detail()
        if flag == 'raise':
            email_obj = email_object_return(laptop_raise,
                                            [manager_email],
                                            [laptop_raise.user.email],
                                            'email_templates/user_raise_request.html',
                                            role)
        elif role == 'Manager':
            if status == 'reject':
                email_obj = email_object_return(laptop_raise,
                                                [laptop_raise.user.email],
                                                [manager_email],
                                                'email_templates/request_reject.html',
                                                role)
            else:
                email_obj = email_object_return(laptop_raise,
                                                admin_email,
                                                [manager_email] + [laptop_raise.user.email],
                                                'email_templates/user_raise_request.html',
                                                role)
        elif role == 'Admin':
            if status == 'reject':
                email_obj = email_object_return(laptop_raise,
                                                [laptop_raise.user.email],
                                                [manager_email] + admin_email,
                                                'email_templates/request_reject.html',
                                                role)
            else:
                email_obj = email_object_return(laptop_raise,
                                                [laptop_raise.user.email],
                                                [manager_email] + admin_email,
                                                'email_templates/request_complete_approval.html',
                                                role)
        email_obj.content_subtype = 'html'
        email_status = email_obj.send()
        if email_status < 1:
            logger.error(
                "Unable To send Mail To The Authorities For"
                "The Following Leave Applicant : {0} Date time : {1} ".format(
                    laptop_raise.user.first_name, timezone.make_aware(datetime.datetime.now(),
                                                         timezone.get_default_timezone())))
        else:
            logger.debug("send succesfull")


def email_object_return(laptop_raise, to_email, cc_email, template,role):
    email_content = render_to_string(template,
                                     {'user': laptop_raise.user.first_name,
                                      'approved_by': role,
                                      'from_date': laptop_raise.from_date,
                                      'to_date': laptop_raise.to_date,
                                      'laptop_no': laptop_raise.laptop.laptop_id,
                                      'reason': laptop_raise.reason})
    email_obj = EmailMessage('Request raised for laptop',
                             email_content,
                             settings.EMAIL_HOST_USER,
                             to_email,
                             cc=cc_email
                             )
    return email_obj


