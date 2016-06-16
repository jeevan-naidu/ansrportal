from __future__ import absolute_import
from django.conf import settings
from celery.registry import tasks
from celery.task import Task
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from Leave.models import LeaveApplications, APPLICATION_STATUS, LEAVE_TYPES_CHOICES, SESSION_STATUS, BUTTON_NAME
import datetime
from datetime import date,timedelta
from django.utils import timezone
import logging
logger = logging.getLogger('MyANSRSource')


class EmailSendTask(Task):
    def run(self, user, manager, leave_selected, fromdate, todate, fromsession, tosession, reason, flag):
        leaveTypeDictionary = dict(LEAVE_TYPES_CHOICES)
        leaveSessionDictionary = dict(SESSION_STATUS)
        fromdate = str(fromdate)+' Session: '+leaveSessionDictionary[fromsession]
        todate = str(todate)+' Session: '+leaveSessionDictionary[tosession]
        if flag == 'save':
            msg_html = render_to_string('email_templates/apply_leave.html', {'registered_by': user.first_name, 'leaveType':leaveTypeDictionary[leave_selected],
             'fromdate':fromdate, 'todate':todate, 'reason':reason})

            mail_obj = EmailMessage('New Leave applied - Leave Type - ' + leaveTypeDictionary[leave_selected], msg_html, settings.EMAIL_HOST_USER, [user.email],
            cc=[manager.email])
        elif flag == 'cancel':
            msg_html = render_to_string('email_templates/cancel_leave.html', {'registered_by': user.first_name, 'leaveType':leaveTypeDictionary[leave_selected],
            'fromdate':fromdate, 'todate':todate, 'reason':reason})

            mail_obj = EmailMessage('Leave canceled - Leave Type - ' + leaveTypeDictionary[leave_selected], msg_html, settings.EMAIL_HOST_USER, [user.email],
             cc=[manager.email])

        mail_obj.content_subtype = 'html'
        email_status = mail_obj.send()

        if email_status < 1:
            logger.error(
                "Unable To send Mail To The Authorities For"
                "The Following Leave Applicant : {0} Date time : {1} ".format(
                 user.first_name, timezone.make_aware(datetime.datetime.now(),
                                                                        timezone.get_default_timezone())))
        else:
            logger.debug("send succesfull")


class ManagerEmailSendTask(Task):
    def run(self, user, status, from_date, to_date, status_comments, manager):
        msg_html = render_to_string('email_templates/leave_status.html',
                                    {'registered_by': user.first_name,
                                     'status': status,
                                     'from_date': from_date,
                                     'to_date': to_date,
                                     'comment': status_comments,
                                     'action_taken_by': user.username})

        mail_obj = EmailMessage('Leave Application Status',
                                msg_html, settings.EMAIL_HOST_USER, [user.email],
                                cc=[manager.email])

        mail_obj.content_subtype = 'html'

        email_status = mail_obj.send()
        if email_status == 0:
                    logger.error(
                        "Unable To send Mail To The Authorities For"
                        "The Following Leave Applicant : {0} Date time : {1} ".format(
                         leave_application.user.first_name, timezone.make_aware(datetime.datetime.now(),
                                                                                timezone.get_default_timezone())))
                    return "failed"

tasks.register(EmailSendTask)
tasks.register(ManagerEmailSendTask)
