import logging
from templated_email import send_templated_mail
from django.core.management.base import BaseCommand
from MyANSRSource.models import ProjectMilestone, Project
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
    projects = Project.objects.filter(
        closed=False).values('projectId',
                             'name',
                             'projectManager__email',
                             'projectManager__first_name')
    for eachProject in list(projects):
        milestones = ProjectMilestone.objects.filter(
            project__projectId=eachProject['projectId'],
            closed=False,
            milestoneDate=deadlineDate,
        ).values('description', 'milestoneDate')
        eachProject['milestones'] = list(milestones)
    return projects


def sendEmail(self, details, date, label):
    if len(details) > 0:
        for eachDetail in details:
            send_templated_mail(
                template_name='projectMilestoneEmailNotification',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[eachDetail['projectManager__email'], ],
                context={
                    'label': label,
                    'first_name': eachDetail[
                        'projectManager__first_name'
                    ],
                    'projectId': eachDetail[
                        'projectId'
                    ],
                    'projectname': eachDetail[
                        'name'
                    ],
                    'milestones': eachDetail[
                        'milestones'
                    ],
                    },
            )
            logger.info('Sent email to {0} about project {1} \
                         This is type {2} reminder'.
                        format(eachDetail['projectManager__email'],
                               eachDetail['projectId'],
                               label))
