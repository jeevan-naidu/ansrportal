from django.core.management.base import BaseCommand

import fb360

from datetime import date, timedelta, datetime

from templated_email import send_templated_mail

from django.conf import settings


class Command(BaseCommand):
    help = 'To remind the user to take an action on request'

    def handle(self, *args, **options):
        two_days_back = datetime.now().date() - timedelta(days=2)

        data = fb360.models.Respondent.objects.filter(
            status=fb360.models.STATUS[0][0],
            initiator__survey__start_date__year=date.today().year,
            createdon__lte=two_days_back
        ).values('employee__email', 'initiator__employee__first_name', 'initiator__employee__last_name')

        if len(data):
            send_ email(self, data)


def send_email(self, data):
    for eachData in data:
        send_templated_mail(
            template_name='FB360RequestNotification',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[eachData['employee__email'], ],
            context={'request_from': '{0} {1}'.format(eachData['initiator__employee__first_name'],
                                                      eachData['initiator__employee__last_name'])}
        )
