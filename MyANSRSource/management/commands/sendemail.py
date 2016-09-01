from templated_email import send_templated_mail
from django.core.management.base import BaseCommand
from MyANSRSource.models import SendEmail
import json
from django.conf import settings
from smtplib import SMTPException
import logging
logger = logging.getLogger('MyANSRSource')


class Command(BaseCommand):
    help = 'Sends Emails to remind concerned \
        persons about thier status in project'

    def handle(self, *args, **options):
        data = SendEmail.objects.filter(sent=False).values('toAddr',
                                                           'template_name',
                                                           'content', 'id')
        for eachData in data:
            try:
                toAddr = json.loads(eachData['toAddr'])
                template_name = eachData['template_name']
                content = json.loads(eachData['content'])
            except ValueError as e:
                logger.error(str(e))
            sendEmail(template_name, toAddr, content)
            try:
                sm = SendEmail.objects.get(pk=eachData['id'])
                sm.sent = True
                sm.save()
            except SendEmail.DoesNotExist:
                logger.error(
                    "SendEmail does not have a record with id: {0}".format(
                        eachData['id']))


def sendEmail(template_name, toAddr, content):
    try:
        send_templated_mail(
            template_name=template_name,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=toAddr,
            context=content
        )
    except SMTPException as e:
        logger.error(str(e))
