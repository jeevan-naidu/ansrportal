from __future__ import absolute_import
from django.conf import settings
from celery.registry import tasks
from celery.task import Task
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from Leave.models import LEAVE_TYPES_CHOICES, SESSION_STATUS, SHORT_ATTENDANCE_TYPE
import datetime
from django.utils import timezone
from employee.models import Employee
from django.contrib.auth.models import User
import logging
logger = logging.getLogger('MyANSRSource')

leaveTypeDictionary = dict(LEAVE_TYPES_CHOICES)
leaveSessionDictionary = dict(SESSION_STATUS)
shortattendancetype = dict(SHORT_ATTENDANCE_TYPE)


def mangerdetail(user):
    useremployeedetail = Employee.objects.get(user_id=user.id)
    mangeremployeedetail = Employee.objects.get(employee_assigned_id=useremployeedetail.manager_id)
    user = User.objects.get(id=mangeremployeedetail.user_id)
    return user


class EmailSendTask(Task):
    def run(self, user, manager, leave_selected, fromdate, todate, fromsession, tosession, count, reason, flag):

        fromdate = str(fromdate)+' Session: '+leaveSessionDictionary[fromsession]
        todate = str(todate)+' Session: '+leaveSessionDictionary[tosession]
        if flag == 'save':
            msg_html = render_to_string('email_templates/apply_leave.html', {'registered_by': user.first_name, 'leaveType':leaveTypeDictionary[leave_selected],
             'fromdate':fromdate, 'todate':todate, 'count':count, 'reason':reason})

            mail_obj = EmailMessage('New Leave applied - Leave Type - ' + leaveTypeDictionary[leave_selected], msg_html, settings.EMAIL_HOST_USER, [user.email],
            cc=[manager.email])
        elif flag == 'cancel':
            msg_html = render_to_string('email_templates/cancel_leave.html', {'registered_by': user.first_name, 'leaveType':leaveTypeDictionary[leave_selected],
            'fromdate':fromdate, 'todate':todate, 'count':count, 'reason':reason})

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
    def run(self, user, leavetype, status, from_date, to_date, count, status_comments, manager):

        msg_html = render_to_string('email_templates/leave_status.html',
                                    {'registered_by': user.first_name,
                                     'leaveType': leaveTypeDictionary[leavetype],
                                     'status': status,
                                     'from_date': from_date,
                                     'to_date': to_date,
                                     'count':count,
                                     'reason': status_comments,
                                     'action_taken_by': manager.first_name})

        mail_obj = EmailMessage('Leave Application Status',
                                msg_html, settings.EMAIL_HOST_USER, [user.email],
                                cc=[manager.email])

        mail_obj.content_subtype = 'html'
        email_status = mail_obj.send()
        if email_status == 0:
                    logger.error(
                        "Unable To send Mail To The Authorities For"
                        "The Following Leave Applicant : Date time : ")
                    return "failed"
        else:
            logger.debug('send successful')


class ShortAttendanceManagerActionEmailSendTask(Task):
    def run(self, user, leavetype, status, fordate, duedate, status_comments):
        manager = mangerdetail(user)
        msg_html = render_to_string('email_templates/short_attendance_manager_action.html',
                                    {'user': user.first_name,
                                     'leaveType': shortattendancetype[leavetype],
                                     'fordate': fordate,
                                     'duedate': duedate,
                                     'action': status,
                                     'reason': status_comments,
                                     'action_taken_by': manager.first_name})

        mail_obj = EmailMessage('Short Attendance Dispute Action',
                                msg_html, settings.EMAIL_HOST_USER, [user.email],
                                cc=[manager.email])

        mail_obj.content_subtype = 'html'
        email_status = mail_obj.send()
        if email_status == 0:
                    logger.error(
                        "Unable To send Mail To The Authorities For"
                        "The Following Leave Applicant : Date time : ")
                    return "failed"
        else:
            logger.debug('send successful')


class ShortAttendanceDisputeEmailSendTask(Task):
    def run(self, user, leavetype, status, fordate, duedate, status_comments, remark):
        manager = mangerdetail(user)
        msg_html = render_to_string('email_templates/short_attendance_dispute.html',
                                    {'user': manager.first_name,
                                     'firstname': user.first_name,
                                     'lastname' : user.last_name,
                                     'leaveType': shortattendancetype[leavetype],
                                     'fordate': fordate,
                                     'duedate': duedate,
                                     'reason': status_comments,
                                     'status': status,
                                     'remark':remark
                                     })

        mail_obj = EmailMessage('Short Attendance Raised',
                                msg_html, settings.EMAIL_HOST_USER, [manager.email],
                                cc=[user.email])

        mail_obj.content_subtype = 'html'
        email_status = mail_obj.send()
        if email_status == 0:
                    logger.error(
                        "Unable To send Mail To The Authorities For"
                        "The Following Leave Applicant : Date time : ")
                    return "failed"
        else:
            logger.debug('send successful')


class ApproveLeaveCancelEmailSendTask(Task):
    def run(self, user, leavetype, status, from_date, to_date, from_session, to_session, count, status_comments, admin):
        manager = mangerdetail(user)
        fromdate = str(from_date) + ' Session: ' + leaveSessionDictionary[from_session]
        todate = str(to_date) + ' Session: ' + leaveSessionDictionary[to_session]
        msg_html = render_to_string('email_templates/admin_leave_cancel.html',
                                    {'registered_by': user.first_name,
                                     'leaveType': leaveTypeDictionary[leavetype],
                                     'status': status,
                                     'from_date': from_date,
                                     'to_date': to_date,
                                     'count': count,
                                     'reason': status_comments,
                                     })

        mail_obj = EmailMessage('Leave Application Status',
                                msg_html, settings.EMAIL_HOST_USER, [user.email],
                                cc=[manager.email,admin.email])

        mail_obj.content_subtype = 'html'
        email_status = mail_obj.send()
        if email_status == 0:
                    logger.error(
                        "Unable To send Mail To The Authorities For"
                        "The Following Leave Applicant : Date time : ")
                    return "failed"
        else:
            logger.debug('send successful')



class ShortAttendanceRaisedEmailSendTask(Task):
    def run(self, user, leavetype, status, fordate, duedate, status_comments):
        manager = mangerdetail(user)
        msg_html = render_to_string('email_templates/short_attendance_raised.html',
                                    {'registered_by': user.first_name,
                                     'leaveType': shortattendancetype[leavetype],
                                     'fordate': fordate,
                                     'duedate': duedate,
                                     'reason': status_comments,
                                     'status': status,
                                     })

        mail_obj = EmailMessage('Short Attendance Raised',
                                msg_html, settings.EMAIL_HOST_USER, [user.email],
                                cc=[])

        mail_obj.content_subtype = 'html'
        email_status = mail_obj.send()
        if email_status == 0:
                    logger.error(
                        "Unable To send Mail To The Authorities For"
                        "The Following Leave Applicant : Date time : ")
                    return "failed"
        else:
            logger.debug('send successful')


tasks.register(EmailSendTask)
tasks.register(ManagerEmailSendTask)
tasks.register(ShortAttendanceDisputeEmailSendTask)
tasks.register(ShortAttendanceManagerActionEmailSendTask)
tasks.register(ApproveLeaveCancelEmailSendTask)
tasks.register(ShortAttendanceRaisedEmailSendTask)
