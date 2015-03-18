from templated_email import send_templated_mail
from django.core.management.base import BaseCommand
from MyANSRSource.models import SendEmail
import json
from django.conf import settings


class Command(BaseCommand):
    help = 'Sends Emails to remind concerned \
        persons about thier status in project'

    def handle(self, *args, **options):
        data = SendEmail.objects.filter(sent=False).values('toAddr',
                                                          'template_name',
                                                          'content', 'id')
        for eachData in data:
            toAddr = eachData['toAddr']
            template_nam = eachData['template_name']
            content = json.loads(eachData['content'])
            content['startDate'] = content['startDate']
            content['mystartdate'] = content['mystartdate']
            print content
            # sendEmail(templated_name, toAddr, content)
            # sm = SendEmail.objects.get(eachData['id'])
            # sm.sent = True
            # sm.save()
        self.stdout.write('Successfully sent mail to team manager')


def sendEmail(template_name, toAddr, content):
    send_templated_mail(
        template_name=template_name,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[eachDetail['project__projectManager__email'], ],
        context=content
    )
