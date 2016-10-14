from __future__ import absolute_import
from django.conf import settings
from celery.registry import tasks
from celery.task import Task
from django.template.loader import render_to_string
from django.core.mail import EmailMessage

import logging
logger = logging.getLogger('MyANSRSource')

class EmailHireSendTask(Task):
    def run(self, user, email, position):
        msg_html = render_to_string('email_templates/selected.html',
                                    {'candidate': user,
                                     'position': position,
                                 })

        mail_obj = EmailMessage('Congrats you are selected',
                                msg_html, settings.EMAIL_HOST_USER, ['vivek.pradhan@ansrsource.com'],
                                cc=['vivek.pradhan@ansrsource.com'])

        mail_obj.content_subtype = 'html'
        email_status = mail_obj.send()
        if email_status == 0:
            logger.error(
                "Unable To send Mail To The Authorities For"
                "The Following Leave Applicant : Date time : ")
            return "failed"
        else:
            logger.debug('send successful')



tasks.register(EmailHireSendTask)