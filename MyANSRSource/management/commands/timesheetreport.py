from templated_email import send_templated_mail
from django.core.management.base import BaseCommand
from MyANSRSource.models import TimeSheetEntry, Project, ProjectTeamMember
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.conf import settings


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
        send_templated_mail(
            template_name='timesheetStatus',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[eachDetail['manager'].email, ],
            context={
                'project': eachDetail['project'],
                'billableHours': eachDetail['billableHours'],
                'nonBillableHours': eachDetail['nonBillableHours'],
                'status': eachDetail['status'],
                'teamMember': eachDetail['teamMember'],
                'startDate': start,
                'endDate': end
                },
        )
        self.stdout.write('Successfully sent TS status to team manager')


def getTSStatus(start, end):

    openProjects = Project.objects.filter(closed=False).values_list(
        'id', flat=True)

    teamMembers = []
    for eachProject in openProjects:
        d = {}
        d['project'] = eachProject
        members = ProjectTeamMember.objects.filter(
            project__id=eachProject).values('member')
        d['teamMember'] = members
        teamMembers.append(d)

    tsEntry = teamMembers[:]

    tsMemberEntry = []
    for eachTS in tsEntry:
        d = {}
        d['project'] = eachTS['project']
        d['timesheet'] = TimeSheetEntry.objects.filter(
            project__id=eachTS['project'],
            wkstart=start,
            wkend=end
        ).values('teamMember__id', 'mondayH', 'tuesdayH', 'wednesdayH',
                 'thursdayH', 'fridayH', 'saturdayH', 'sundayH',
                 'approved', 'hold')
        if len(d['timesheet']):
            tsMemberEntry.append(d)

    tsMemberTotals = []
    for eachEntry in tsMemberEntry:
        d = {}
        d['project'] = eachEntry['project']
        for eachTS in eachEntry['timesheet']:
            d['teamMember'] = eachTS['teamMember__id']
            d['billableHours'] = eachTS['mondayH'] + eachTS['tuesdayH'] + \
                eachTS['wednesdayH'] + eachTS['thursdayH'] + \
                eachTS['fridayH'] + eachTS['saturdayH'] + eachTS['sundayH']
            if eachTS['approved']:
                d['status'] = 'Approved'
            elif eachTS['hold']:
                d['status'] = 'Submitted'
            else:
                d['status'] = 'Not Submitted'
            tsMemberTotals.append(d)

    memberTotals = []
    for eachNon in tsMemberTotals:
        d = {}
        d['project'] = Project.objects.get(id=eachNon['project']).name
        d['manager'] = Project.objects.get(id=eachNon['project']).projectManager
        d['billableHours'] = eachNon['billableHours']
        d['status'] = eachNon['status']
        d['teamMember'] = User.objects.get(id=eachNon['teamMember']).username
        nonBillableHours = TimeSheetEntry.objects.filter(
            teamMember__id=eachNon['teamMember'],
            wkstart=start, wkend=end, project=None
        ).values('mondayH', 'tuesdayH', 'wednesdayH', 'thursdayH',
                 'fridayH', 'saturdayH', 'sundayH'
                 )
        for eachnbHours in nonBillableHours:
            d['nonBillableHours'] = eachnbHours['mondayH'] + \
                eachnbHours['tuesdayH'] + eachnbHours['wednesdayH'] + \
                eachnbHours['thursdayH'] + eachnbHours['fridayH'] + \
                eachnbHours['saturdayH'] + eachnbHours['sundayH']
            memberTotals.append(d)

    return memberTotals
