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
    def run(self, user,  email_list, from_date, to_date, feedback):
        msg_html = render_to_string('email/time_sheet_rejection.html',
                                    {
                                     'start_date': from_date,
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

tasks.register(TimeSheetWeeklyReminder)
tasks.register(TimeSheetRejectionNotification)
