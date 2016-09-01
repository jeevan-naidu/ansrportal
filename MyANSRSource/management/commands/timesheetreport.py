from templated_email import send_templated_mail
from django.core.management.base import BaseCommand
from MyANSRSource.models import TimeSheetEntry, ProjectManager
from datetime import datetime, timedelta
from django.conf import settings
from django.db.models import Sum


class Command(BaseCommand):
    help = 'Send Timesheet status to project manager'

    def handle(self, *args, **options):
        today = datetime.now().date()
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=6)
        data = getTSStatus(start, end)
        sendEmail(self, data, start, end)


def sendEmail(self, data, start, end):
    for eachDetail in data:
        if len(eachDetail['ts']):
            send_templated_mail(
                template_name='timesheetStatus',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[eachDetail['email'], ],
                context={
                    'tsDetails': eachDetail['ts'],
                    'startDate': start,
                    'endDate': end
                    },
            )
            self.stdout.write('Successfully sent TS status to team manager')


def getTSStatus(start, end):
    managers = ProjectManager.objects.filter(
        project__closed=False).values('user', 'user__email').distinct()

    weekData = []
    for eachManager in managers:
        d = {}
        d['email'] = eachManager['user__email']
        d['ts'] = TimeSheetEntry.objects.filter(
            project__projectManager=eachManager['user'],
            wkstart=start,
            wkend=end
        ).values('teamMember__username', 'project__name',
                 'approved', 'hold').annotate(
            monday=Sum('mondayH'),
            tuesday=Sum('tuesdayH'),
            wednesday=Sum('wednesdayH'),
            thursday=Sum('thursdayH'),
            friday=Sum('fridayH'),
            saturday=Sum('saturdayH'),
            sunday=Sum('sundayH')
        )
        weekData.append(d)

    for eachData in weekData:
        for eachTsData in eachData['ts']:
            eachTsData['total'] = eachTsData['monday'] + \
                eachTsData['tuesday'] + \
                eachTsData['wednesday'] + \
                eachTsData['thursday'] + \
                eachTsData['friday'] + \
                eachTsData['saturday'] + \
                eachTsData['sunday']
    return weekData
