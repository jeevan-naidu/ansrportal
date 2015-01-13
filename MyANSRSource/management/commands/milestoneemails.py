from templated_email import send_templated_mail
from django.core.management.base import BaseCommand
from MyANSRSource.models import ProjectMilestone
from datetime import datetime, timedelta
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
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
             'project__projectManager__first_name',
             'project__projectManager__last_name',
             'project__projectManager__email'
             )


def sendEmail(self, details, date, label):
    if len(details) > 0:
        for eachDetail in details:
            if label == "week":
                message = 'Project {0}\'s milestone is about to meet \
                    its deadline by next week. \
                    Make sure you have done the invoice for it.'.format(
                    eachDetail['project__name']
                    )
            elif label == "lastDay":
                message = 'Project {0}\'s milestone is about to \
                    meet its deadline by tommorow.'.format(
                    eachDetail['project__name']
                    )
            else:
                message = 'Project {0}\'s milestone is expired'.format(
                    eachDetail['project__name']
                )
            send_templated_mail(
                template_name='ProjectMilestoneEmailNotification.html',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[eachDetail['project__projectManager'], ],
                context={
                    'firstName': eachDetail[
                        'project__projectManager__first_name'
                    ],
                    'lastName': eachDetail[
                        'project__projectManager__last_name'
                    ],
                    'message': message
                    },
            )
            self.stdout.write('Successfully sent mail to team manager \
                              about {0} project\'s milestone'.format(
                eachDetail['project__name']
                ))
