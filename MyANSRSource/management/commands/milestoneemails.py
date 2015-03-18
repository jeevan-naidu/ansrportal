from templated_email import send_templated_mail
from django.core.management.base import BaseCommand
from MyANSRSource.models import ProjectMilestone
from datetime import datetime, timedelta
from django.conf import settings


class Command(BaseCommand):
    help = 'Sends Emails to remind concerned persons \
        in the project on regular basis'

    def handle(self, *args, **options):
        lastOneWeek = datetime.now().date() - timedelta(weeks=1)
        lastDay = datetime.now().date() - timedelta(days=1)
        expired = datetime.now().date() + timedelta(days=1)
        sendEmail(self, getContent(lastOneWeek), lastOneWeek, 'week')
        sendEmail(self, getContent(lastDay), lastDay, 'lastDay')
        sendEmail(self, getContent(expired), expired, 'expired')


def getContent(deadlineDate):
    return ProjectMilestone.objects.filter(
        milestoneDate=deadlineDate
    ).values('project__name',
             'project__projectId',
             'description',
             'milestoneDate',
             'project__projectManager__first_name',
             'project__projectManager__email'
             )


def sendEmail(self, details, date, label):
    if len(details) > 0:
        for eachDetail in details:
            send_templated_mail(
                template_name='projectMilestoneEmailNotification',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[eachDetail['project__projectManager__email'], ],
                context={
                    'first_name': eachDetail[
                        'project__projectManager__first_name'
                    ],
                    'projectId': eachDetail[
                        'project__projectId'
                    ],
                    'projectname': eachDetail[
                        'project__name'
                    ],
                    'milestonename': eachDetail[
                        'description'
                    ],
                    'milestonedate': eachDetail[
                        'milestoneDate'
                    ],
                    },
            )
            self.stdout.write('Successfully sent mail to team manager')
