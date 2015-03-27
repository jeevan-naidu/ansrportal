import logging
from templated_email import send_templated_mail
from django.core.management.base import BaseCommand
from MyANSRSource.models import ProjectMilestone
from datetime import datetime, timedelta
from django.conf import settings

logger = logging.Logger('milestone-emails')


class Command(BaseCommand):
    help = 'Sends Emails reminders about milestones both approaching \
        and expired ones on a daily basis'

    def handle(self, *args, **options):
        logger.info(
            'Starting Milestone Update email batch for date {0}'.format(
                datetime.now().date()))
        nextWeek = datetime.now().date() + timedelta(weeks=1)
        nextDay = datetime.now().date() + timedelta(days=1)
        expired = datetime.now().date() - timedelta(days=1)

        logger.info('Running milestone batch job for Today + 1 week :{0}, \
                    Today + 1 day {1}, Today - 1 day {2}'.
                    format(nextWeek, nextDay, expired))
        sendEmail(self, getContent(nextWeek),
                  nextWeek, 'week')
        sendEmail(self, getContent(nextDay),
                  nextDay, 'nextDay')
        sendEmail(self, getContent(expired),
                  expired, 'expired')


def getContent(deadlineDate):
    return ProjectMilestone.objects.filter(
        milestoneDate=deadlineDate,
        closed=False
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
                    'label': label,
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
            logger.info('Sent email to {0} about project {1} milestone date {2}.  \
                         This is type {3} reminder'.
                        format(eachDetail['project__projectManager__email'],
                               eachDetail['project__projectId'],
                               eachDetail['milestoneDate'],
                               label))
