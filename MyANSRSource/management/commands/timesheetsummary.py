from templated_email import send_templated_mail
from django.core.management.base import BaseCommand
from MyANSRSource.models import TimeSheetEntry, Report
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models import Sum, Count
from CompanyMaster.models import Holiday


class Command(BaseCommand):
    help = 'Send Timesheet data to notifiers'

    def handle(self, *args, **options):
        report_name = 'timesheetsummary'
        today = datetime.now().date()
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=6)
        weekData = getTS(start, end)
        weekDataNon = getNonTS(start, end)
        if len(weekDataNon):
            nonData = []
            for eachTsData in weekDataNon:
                eachTsData['total'] = eachTsData['monday'] + \
                    eachTsData['tuesday'] + \
                    eachTsData['wednesday'] + \
                    eachTsData['thursday'] + \
                    eachTsData['friday'] + \
                    eachTsData['saturday'] + \
                    eachTsData['sunday']
                currentUser = User.objects.get(pk=eachTsData['teamMember'])
                locationId = currentUser.employee.location
                weekHolidays = Holiday.objects.filter(
                    location=locationId,
                    date__range=[start, end]
                ).values('date')
                weekTotal = 40 - (8 * len(weekHolidays))
                deviation = (weekTotal * 20) / 100
                if eachTsData['total'] > deviation:
                    nonData.append(eachTsData)
        if len(weekData):
            for eachTsData in weekData:
                eachTsData['total'] = eachTsData['monday'] + \
                    eachTsData['tuesday'] + \
                    eachTsData['wednesday'] + \
                    eachTsData['thursday'] + \
                    eachTsData['friday'] + \
                    eachTsData['saturday'] + \
                    eachTsData['sunday']
            notifier = Report.objects.filter(name=report_name).values(
                'notify__email')
            if len(notifier):
                tsData = {'notify': notifier, 'data': weekData}
                if len(nonData):
                    tsData['nonData'] = nonData
                sendEmail(tsData)
            else:
                print 'No Notifiers are mentioned'
        else:
            print 'No TS Data for {0} - {1} week'.format(start, end)


def sendEmail(content):
    if 'nonData' in content:
        tsData = {'data': content['data'], 'nonData': content['nonData']}
    else:
        tsData = {'data': content['data']}
    send_templated_mail(
        template_name='timesheetSummary',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[eachData['notify__email'] for eachData in content[
            'notify']],
        context=tsData
    )


def getTS(start, end):
    return TimeSheetEntry.objects.filter(wkstart=start,
                                         wkend=end,
                                         project__isnull=False).values(
        'teamMember__first_name',
        'teamMember__last_name',
        'teamMember__email',
        'project__projectId'
        ).annotate(
        timesheets=Count(
            'project__projectId'
            ),
        monday=Sum('mondayH'),
        tuesday=Sum('tuesdayH'),
        wednesday=Sum('wednesdayH'),
        thursday=Sum('thursdayH'),
        friday=Sum('fridayH'),
        saturday=Sum('saturdayH'),
        sunday=Sum('sundayH'),
        )


def getNonTS(start, end):
    return TimeSheetEntry.objects.filter(wkstart=start,
                                         wkend=end,
                                         project__isnull=True).values(
        'teamMember',
        'teamMember__first_name',
        'teamMember__last_name',
        'teamMember__email',
        ).annotate(
        monday=Sum('mondayH'),
        tuesday=Sum('tuesdayH'),
        wednesday=Sum('wednesdayH'),
        thursday=Sum('thursdayH'),
        friday=Sum('fridayH'),
        saturday=Sum('saturdayH'),
        sunday=Sum('sundayH'),
        )
