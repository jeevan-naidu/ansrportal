from __future__ import absolute_import
from django.conf import settings
from celery.registry import tasks
from celery.task import Task
from django.template.loader import render_to_string
from django.core.mail import EmailMessage

import logging
logger = logging.getLogger('MyANSRSource')


class TimeSheetWeeklyReminder(Task):
    def run(self, user,  email_list, from_date, to_date):
        msg_html = render_to_string('email/time_sheet_reminder.html',
                                    {
                                     'start_date': from_date,
                                     'end_date': to_date,
                                    })
        mail_obj = EmailMessage('Time sheet Weekly Submission Reminder',
                                msg_html, settings.EMAIL_HOST_USER, email_list,
                                cc=[user.email])

        mail_obj.content_subtype = 'html'
        try:
            mail_obj.send()
        except Exception as e:
            logger.error(
                u'Unable to send time sheet reminder mail for   {0}{1}{2} and the error is {3}'
                u' '.format(from_date, to_date, email_list, str(e)))


class TimeSheetRejectionNotification(Task):
    def run(self, user,  email_list, from_date, to_date, projects, feedback):
        msg_html = render_to_string('email/time_sheet_rejection.html',
                                    {
                                     'start_date': from_date, "projects": projects,
                                     'end_date': to_date, 'feedback': feedback,
                                    })
        mail_obj = EmailMessage('Time sheet Weekly Rejection Reminder',
                                msg_html, settings.EMAIL_HOST_USER, [email_list],
                                cc=[user.email])

        mail_obj.content_subtype = 'html'
        try:
            mail_obj.send()
        except Exception as e:
            logger.error(
                u'Unable to send time sheet rejection reminder mail for   {0}{1}{2} and the error is {3}'
                u' '.format(from_date, to_date, email_list, str(e)))


class ProjectChangeRejection(Task):
    def run(self, email_list, crid, reason, projectname, rejection_date):
        msg_html = render_to_string('email/project_rejection.html',
                                    {
                                     'crId': crid,
                                     'reason': reason,
                                     'projectname': projectname,
                                      'rejectiondate' : rejection_date,
                                    })
        mail_obj = EmailMessage(crid+' ID Request Rejection',
                                msg_html, settings.EMAIL_HOST_USER, email_list,
                                cc=[])

        mail_obj.content_subtype = 'html'
        email_status = mail_obj.send()
        if email_status == 0:
            logger.error(
                "Unable To send Mail To The Authorities For"
                "The Following Exit Applicant : Date time : ")
            return "failed"
        else:
            logger.debug('send successful')


class ProjectRejection(Task):
    def run(self, email_list, remark, username, projectname, rejection_date):
        msg_html = render_to_string('email/projectbu_rejection.html',
                                    {
                                     'username': username,
                                     'reason': remark,
                                     'projectname': projectname,
                                      'rejectiondate' : rejection_date,
                                    })
        mail_obj = EmailMessage(projectname+' Rejected',
                                msg_html, settings.EMAIL_HOST_USER, [email_list],
                                cc=[])

        mail_obj.content_subtype = 'html'
        email_status = mail_obj.send()
        if email_status == 0:
            logger.error(
                "Unable To send Mail To The Authorities For"
                "The Following Exit Applicant : Date time : ")
            return "failed"
        else:
            logger.debug('send successful')

tasks.register(TimeSheetWeeklyReminder)
tasks.register(TimeSheetRejectionNotification)
tasks.register(ProjectChangeRejection)
tasks.register(ProjectRejection)
