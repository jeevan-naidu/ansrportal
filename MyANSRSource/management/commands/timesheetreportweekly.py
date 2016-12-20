from django.core.management.base import BaseCommand
from datetime import datetime, timedelta
from MyANSRSource.models import TimeSheetEntry
from django.contrib.auth.models import User
from employee.models import Employee
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings


class Command(BaseCommand):
    help = 'Send Timesheet status to project manager'

    def add_arguments(self, parser):
        parser.add_argument('week', type=int)

    def handle(self, *args, **options):
        week = options['week']
        timesheet_report(week)


def timesheet_report(week):
    print str(datetime.now()) + " timesheet report weekly started running"
    manager_list = Employee.objects.all().values('manager').distinct()
    for manager in manager_list:
        manager_id = manager_check(manager)
        if manager_id:
            user_list = Employee.objects.filter(manager=manager['manager'])
            report_based_on_manger(user_list, manager_id, week)
    print str(datetime.now()) + " timesheet report weekly finished running. processed data" + str(len(manager_list))


def manager_check(manager):
    try:
        user = User.objects.get(id=Employee.objects.get(employee_assigned_id=manager['manager']).user_id)
        return user
    except:
        return False


def report_based_on_manger(user_list, manager, week):
    try:
        day = 7 * int(week)
    except:
        print "please enter integer value"
    today = datetime.now().date()
    startweek = today - timedelta(days=today.weekday())
    start = startweek - timedelta(days=day)
    end = start + timedelta(days=6)
    timesheet_report_list = []
    user_report = {'name': '', 'status': '', 'total': ''}
    for user in user_list:
        user_id = User.objects.filter(id=user.user_id, is_active=True)
        if user_id:
            user_report['name'] = user_id[0].first_name + " " + user_id[0].last_name
            timesheet_entry = TimeSheetEntry.objects.filter(wkstart=start, wkend=end, teamMember=user_id[0].id)

            time_sheet_detail = timesheet_status(timesheet_entry)
            user_report['status'] = time_sheet_detail['status']
            user_report['total'] = time_sheet_detail['total']
            timesheet_report_list.append(user_report)
            user_report = {'name': '', 'status': '', 'total': ''}
    timesheet_report_list = sorted(timesheet_report_list, key=lambda k: k['status'])
    msg_html = render_to_string('email/timesheetreport.html',
                                {'registered_by': manager.first_name, 'startdate': start,
                                 'enddate': end, 'timesheet_report_list': timesheet_report_list})
    mail_obj = EmailMessage('TimeSheet Status Report for Week ' + str(start), msg_html,
                            settings.EMAIL_HOST_USER, [manager.email], cc=[])
    mail_obj.content_subtype = 'html'
    if timesheet_report_list:
        email_status = mail_obj.send()


def timesheet_status(timesheet_entry):
    time_sheet_detail = dict()
    if timesheet_entry and timesheet_entry[0].hold == 1:
        time_sheet_detail['status'] = "Submitted"
        time_sheet_detail['total'] = week_total_hour(timesheet_entry)
    elif timesheet_entry:
        time_sheet_detail['status'] = "Incomplete"
        time_sheet_detail['total'] = week_total_hour(timesheet_entry)
    else:
        time_sheet_detail['status'] = "No Entry"
        time_sheet_detail['total'] = 0.0
    return time_sheet_detail



def week_total_hour(timesheet_entry):
    total = 0.0
    for entry in timesheet_entry:
        total += float(entry.totalH)
    return total








