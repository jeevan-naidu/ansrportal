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

    def handle(self, *args, **options):
        timesheet_report()


def timesheet_report():

    manager_list = Employee.objects.all().values('manager').distinct()
    for manager in manager_list:
        manager_id = manager_check(manager)
        if manager_id:
            user_list = Employee.objects.filter(manager=manager['manager'])
            report_based_on_manger(user_list, manager_id)


def manager_check(manager):
    try:
        user = User.objects.get(id=Employee.objects.get(employee_assigned_id=manager['manager']).user_id)
        return user
    except:
        return False


def report_based_on_manger(user_list, manager):
    today = datetime.now().date()
    startweek = today - timedelta(days=today.weekday())
    start = startweek - timedelta(days=49)
    #start = startweek - timedelta(days=14)
    end = start + timedelta(days=6)
    print str(start) + " " + str(end)
    timesheet_report_list = []
    user_report = {'name': '', 'status': ''}
    for user in user_list:
        user_id = User.objects.filter(id=user.user_id, is_active=True)
        if user_id:
            user_report['name'] = user_id[0].first_name + " " + user_id[0].last_name
            timesheet_entry = TimeSheetEntry.objects.filter(wkstart=start, wkend=end, teamMember=user_id[0].id)
            user_report['status'] = timesheet_status(timesheet_entry)
            timesheet_report_list.append(user_report)
            user_report = {'name': '', 'status': ''}
    msg_html = render_to_string('email_templates/TimeSheetReport.html',
                                {'registered_by': manager.first_name, 'startdate': start,
                                 'enddate': end, 'timesheet_report_list': timesheet_report_list})

    mail_obj = EmailMessage('TimeSheet Status Report for Week ' + str(start), msg_html,
                            settings.EMAIL_HOST_USER, ['shalini.bhagat@ansrsource.com'], cc=[])
    mail_obj.content_subtype = 'html'
    email_status = mail_obj.send()


def timesheet_status(timesheet_entry):
    if timesheet_entry and timesheet_entry[0].hold:
        return "Submitted"
    elif timesheet_entry:
        return "Incomplete"
    else:
        return "No Entry"








