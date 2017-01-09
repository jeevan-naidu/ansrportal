from django.views.generic import View
from django.http import JsonResponse
from forms import *
from models import *
import json
from validations import leaveValidation, oneTimeLeaveValidation, newJoineeValidation, compOffAvailibilityCheck
from django.shortcuts import render
from decimal import *
from django.views.generic.list import ListView
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages
from Leave.models import LeaveApplications, ShortAttendance, APPLICATION_STATUS, LEAVE_TYPES_CHOICES, SESSION_STATUS,\
    BUTTON_NAME, LeaveSummary, SHORT_ATTENDANCE_TYPE
from django.contrib.auth.models import User
import datetime
from datetime import date, timedelta
from employee.models import Employee
import logging
import xlwt
from django.template.defaultfilters import slugify
from django.core.exceptions import PermissionDenied
from tasks import EmailSendTask, ManagerEmailSendTask,\
    ShortAttendanceDisputeEmailSendTask,\
    ShortAttendanceManagerActionEmailSendTask,\
    ApproveLeaveCancelEmailSendTask
from django.conf import settings
from GrievanceAdmin.views import paginator_handler
from calendar import monthrange
import calendar
from CompanyMaster.models import Holiday

logger = logging.getLogger('MyANSRSource')

AllowedFileTypes = ['jpg', 'csv', 'png', 'pdf', 'xlsx', 'xls', 'docx', 'doc', 'jpeg', 'eml']
leaveTypeDictionary = dict(LEAVE_TYPES_CHOICES)
leaveSessionDictionary = dict(SESSION_STATUS)
leaveWithoutBalance = ['loss_of_pay', 'comp_off_earned', 'pay_off', 'work_from_home', 'ooo_dom', 'ooo_int']


def LeaveTransaction(request):
    statusType = request.GET.get('type')
    user_id = request.GET.get('user_id')
    loggedInUser = request.user.id
    statusDict = {'Approved': 'approved',
                  'Rejected': 'rejected',
                  'Cancelled': 'cancelled',
                  'Open': 'open'}
    if statusType == 'All':
        Leave_transact = LeaveApplications.objects.filter(user=user_id,
                                                          leave_type__leave_type=request.GET.get('leave')).values('id',
                                                                                                                  'leave_type__leave_type',
                                                                                                                  'from_date',
                                                                                                                  'from_session',
                                                                                                                  'to_date',
                                                                                                                  'to_session',
                                                                                                                  'days_count',
                                                                                                                  'status')
    else:
        Leave_transact = LeaveApplications.objects.filter(status=statusDict[statusType],
                                                          user=user_id,
                                                          leave_type__leave_type=request.GET.get('leave')).values('id',
                                                                                                                  'leave_type__leave_type',
                                                                                                                  'from_date',
                                                                                                                  'from_session',
                                                                                                                  'to_date',
                                                                                                                   'to_session',
                                                                                                                  'days_count',
                                                                                                                  'status')

    count = 0
    data1 = "<tr class=""><th>Sr.No</th><th>From</th><th>To</th><th>Days</th></tr>"
    for leave in Leave_transact:
        count=count+1
        data1 =data1+ '<tr class="success"><td>{0}<br><a \
         onclick ="showDetails({1})" role="button" data-toggle="modal" title="View Details">Details</a>\
         </td><td>{2}<br>{3}</td><td>{4}, <br>{5}</td><td>{6}<br>\
         <div id="modal-leave-cancel" >'.format(
        count,
        leave['id'],
        leave['from_date'],
        leaveSessionDictionary[leave['from_session']],
        leave['to_date'],
        leaveSessionDictionary[leave['to_session']],
        leave['days_count'],
        )
        if leave['status'] == 'open' and leave['leave_type__leave_type'] != 'comp_off_avail' and int(loggedInUser) == int(user_id):
            data1 = data1 + '<a  role="button" onclick="CancelLeave({0},{1})" >Cancel</a></div>\
            </td></tr>'.format(leave['id'],leave['days_count'],)
        elif request.user.groups.filter(name= settings.LEAVE_ADMIN_GROUP).exists() and leave['status'] in ['open', 'approved']:
            statusflag = lambda: 1 if leave['status'] == 'open' else 0
            data1 = data1 + '<a  role="button" onclick="AdminCancelLeave({0},{1},{2})" >Cancel</a></div>\
                        </td></tr>'.format(leave['id'], leave['days_count'],
                                           statusflag())
        else:
            data1 = data1 + '</div></td></tr>'
    json_data = json.dumps(data1)
    return HttpResponse(json_data, content_type="application/json")



def LeaveCancel(request):
    user_id = request.user.id
    leave_id = request.GET.get('leaveid')
    leavecount = request.GET.get('leavecount')
    leave = LeaveApplications.objects.get(id=leave_id)
    leave_apply_year = leave.from_date.year
    leaveSummary = LeaveSummary.objects.get(leave_type=leave.leave_type, user=user_id, year=leave_apply_year)
    onetimeLeave = ['maternity_leave', 'paternity_leave', 'bereavement_leave']


    if leave.leave_type.leave_type in leaveWithoutBalance:
        leaveSummary.applied = float(leaveSummary.applied) - float(leavecount)
        leaveSummary.save()
    elif leave.leave_type.leave_type in onetimeLeave:
        leaveSummary.balance = float(leavecount)
        leaveSummary.applied = 0
        leaveSummary.save()
    else:
        leaveSummary.balance = float(leaveSummary.balance) + float(leavecount)
        leaveSummary.applied = float(leaveSummary.applied) - float(leavecount)
        leaveSummary.save()

    leave.status = 'cancelled'
    leave.status_action_on = date.today()
    leave.status_action_by = User.objects.get(id=user_id)
    leave.status_comments = "Leave cancelled by user"
    leave.update()
    short_leave_against_cancellation(leave.from_date, leave.to_date, user_id)
    manager = managerCheck(user_id)
    EmailSendTask.delay(request.user, manager, leave.leave_type.leave_type, leave.from_date, leave.to_date, leave.from_session,
     leave.to_session, leave.days_count, leave.reason, 'cancel')
    data1 = "leave cancelled"
    json_data = json.dumps(data1)
    return HttpResponse(json_data, content_type="application/json")


def LeaveDetails(request):
    leave_id = request.GET.get('leaveid')
    leave = LeaveApplications.objects.get(id = leave_id)
    return render(request, 'leave_details.html', {'leave':leave, 'LEAVE_TYPES_CHOICES': LEAVE_TYPES_CHOICES,'SESSION_STATUS': SESSION_STATUS,})


# Create your views here.
class Dashboard(View):
    def get(self, request):
        genderFlag = True
        genderMale = False
        LeaveAdmin = False
        userCheck = False
        user_id = request.user.id
        # leave_summary = LeaveSummary.objects.filter(user=user_id,
        #                                             year=date.today().year).values('leave_type__leave_type',
        #                                                                            'applied',
        #                                                                            'approved',
        #                                                                            'balance')
        leave_summary = LeaveSummary.objects.filter(user=user_id,
                                                    year=2016).values('leave_type__leave_type',
                                                                                   'applied',
                                                                                   'approved',
                                                                                   'balance')
        employeeDetail = Employee.objects.get(user_id = user_id)
        userDetail = User.objects.get(id = user_id)
        newuser = newJoineeValidation(user_id)

        if self.request.user.groups.filter(name=settings.LEAVE_ADMIN_GROUP).exists():
            LeaveAdmin = True

        if user_id:
            userCheck =True

        if not newuser:
            genderFlag =False
        if employeeDetail.gender=='M':
            genderMale =True
        manager = managerCheck(request.user.id)
        if manager:
            mangerfirstname = manager.first_name + " "+manager.last_name
        else:
            mangerfirstname = ''
        emp = Employee.objects.get(user_id=user_id)
        userlist = Employee.objects.filter(manager_id=emp.employee_assigned_id).values('user_id')
        if userlist:
            managerFlag = True
        else:
            managerFlag = False
        # short leave grid population
        leaveShortAttendanceIsActive = settings.LEAVE_SHORT_ATTENDANCE_ISACTIVE
        ShortLeaveApplied = ShortAttendance.objects.filter(user=user_id, active=True).count()
        ShortLeaveAppproved = ShortAttendance.objects.filter(user=user_id, active=False).count()
        context={'leave_summary':leave_summary,
                 'gender': genderFlag,
                 'male': genderMale,
                 'manager': mangerfirstname,
                 'form': UserListViewForm(),
                 'userfullname': userDetail.first_name + " " + userDetail.last_name,
                 'employeeId': employeeDetail.employee_assigned_id,
                 'userid': user_id,
                 'managerFlag': managerFlag,
                 'LeaveAdmin': LeaveAdmin,
                 'userCheck': userCheck,
                 'ShortLeaveApplied':ShortLeaveApplied,
                 'ShortLeaveAppproved':ShortLeaveAppproved,
                 'leaveShortAttendanceIsActive':leaveShortAttendanceIsActive}
        return render(request, 'User.html', context)

    def post(self, request):
        userForm = UserListViewForm(request.POST)
        employee_id = userForm['user'].value()
        user_id_detail = Employee.objects.filter(employee_assigned_id=employee_id).values('user_id')
        if user_id_detail:
            user_id = user_id_detail[0]['user_id']
        else:
            user_id = request.user.id
            LeaveAdmin = True

        LeaveAdmin = False
        userCheck = False
        if self.request.user.groups.filter(name= settings.LEAVE_ADMIN_GROUP).exists():
            LeaveAdmin = True
        elif  int(user_id) == int(request.user.id):
            userCheck = True
        # leave_summary = LeaveSummary.objects.filter(user=user_id,
        #                                           year=date.today().year).values('leave_type__leave_type',
        #                                                                          'applied',
        #                                                                          'approved',
        #                                                                          'balance')
        leave_summary = LeaveSummary.objects.filter(user=user_id,
                                                    year=2016).values('leave_type__leave_type',
                                                                                   'applied',
                                                                                   'approved',
                                                                                   'balance')
        employeeDetail = Employee.objects.get(user_id = user_id)
        userDetail = User.objects.get(id = user_id)
        newuser = newJoineeValidation(user_id)
        genderFlag = True
        genderMale = False
        if not newuser:
            genderFlag =False
        if employeeDetail.gender=='M':
            genderMale =True

        manager = managerCheck(user_id)
        if manager:
            mangerfirstname = manager.first_name + " "+manager.last_name
        else:
            mangerfirstname = ''
        emp = Employee.objects.get(user_id = request.user.id)
        userlist = Employee.objects.filter(manager_id= emp.employee_assigned_id).values('user_id')
        if userlist:
            managerFlag = True
        else:
            managerFlag = False
        # short leave grid population
        ShortLeaveApplied = ShortAttendance.objects.filter(user=user_id, active=True).count()
        ShortLeaveAppproved = ShortAttendance.objects.filter(user=user_id, active=False).count()
        leaveShortAttendanceIsActive = settings.LEAVE_SHORT_ATTENDANCE_ISACTIVE
        context={'leave_summary':leave_summary,
                 'gender': genderFlag,
                 'male': genderMale,
                 'manager': mangerfirstname,
                 'form': UserListViewForm(),
                 'userfullname': userDetail.first_name + " " + userDetail.last_name,
                 'employeeId': employeeDetail.employee_assigned_id,
                 'userid': user_id,
                 'managerFlag': managerFlag,
                 'LeaveAdmin': LeaveAdmin,
                 'userCheck': userCheck,
                 'ShortLeaveApplied': ShortLeaveApplied,
                 'ShortLeaveAppproved': ShortLeaveAppproved,
                 'leaveShortAttendanceIsActive':leaveShortAttendanceIsActive
                 }
        return render(request, 'User.html', context)



class ApplyLeaveView(View):
    ''' add or edit leave '''

    def get(self, request):
        context_data = {'add': True,
                        'record_added': False,
                        'form': None,
                        'success_msg': None,
                        'html_data': None,
                        'errors': [],
                        'leave_type_check': None, 'leave':None}
        try:
            leavetype = request.GET.get('leavetype')
            user_id = request.GET.get('user_id')
            onetime_leave = ['maternity_leave',
                             'paternity_leave',
                             'bereavement_leave',
                             'comp_off_earned',
                             'comp_off_avail',
                             'pay_off',
                             'short_leave']
            count_not_required = ['comp_off_earned',
                                  'pay_off',
                                  'work_from_home',
                                  'loss_of_pay',
                                  'ooo_dom',
                                  'ooo_int']
            form = LeaveForm(leavetype, user_id)
            context_data['form'] = form
            leave_count = LeaveSummary.objects.filter(leave_type__leave_type=leavetype,
                                                      user_id=user_id,
                                                      year=date.today().year)
            if leavetype:
                context_data['leave'] = 'data'
            if leavetype in onetime_leave:
                context_data['leave_type_check'] = 'OneTime'

            if leavetype not in count_not_required and leave_count:
                context_data['leave_count'] = leave_count[0].balance

            return render(request, 'leave_apply.html', context_data)
        except:
            form = LeaveForm('None', request.user.id)
            context_data['form'] = form
            return render(request, 'leave_apply.html', context_data)

    def post(self, request):
        user_id = request.POST['name']
        if not user_id:
            user_id = request.user.id
        leave_form=LeaveForm(request.POST['leave'], user_id, request.POST)
        context_data = {'add': True,
                        'record_added': False,
                        'form' : None, 'success_msg': None,
                        'html_data': None,
                        'errors': [],
                        'leave_type_check': None,
                        'leave': 'formdata'
                        }
        attachment = request.FILES.get('leave_attachment', "")
        if attachment:
            if request.FILES['leave_attachment'].name.split(".")[-1] not in AllowedFileTypes:
                context_data['errors'].append('Attachment : '
                                              'File type not allowed.'
                                              ' Please select a valid file type and then submit again')

        if leave_form.is_valid() and not context_data['errors']:
            fromdate = leave_form.cleaned_data['fromDate']
            leave_applied_year = fromdate.year
            duedate = date.today()
            leave_selected = leave_form.cleaned_data['leave']
            try:
                context_data['leave_count'] = LeaveSummary.objects.filter(leave_type__leave_type=leave_selected,
                                                                          user_id=user_id,
                                                                          year=leave_applied_year)[0].balance
            except:
                context_data['errors'].append('No leave records found on myansrsource portal. Please contact HR.')
                context_data['form'] = leave_form
            onetime_leave = ['maternity_leave',
                             'paternity_leave',
                             'bereavement_leave',
                             'comp_off_earned',
                             'comp_off_avail',
                             'pay_off','short_leave']
            if leave_selected in onetime_leave:
                context_data['leave_type_check'] = 'OneTime'
            reason=leave_form.cleaned_data['Reason']
            manager = managerCheck(user_id)
            if leave_selected in onetime_leave:
                validate = oneTimeLeaveValidation(leave_form, user_id, leave_applied_year)
                fromdate = leave_form.cleaned_data['fromDate']
                todate = validate['todate']
                fromsession = 'session_first'
                tosession = 'session_second'
                if leave_selected in ['comp_off_earned', 'pay_off']:
                    duedate = validate['due_date']


            else:
                validate=leaveValidation(leave_form, user_id, leave_applied_year, attachment)
                fromdate = leave_form.cleaned_data['fromDate']
                todate = leave_form.cleaned_data['toDate']
                fromsession = leave_form.cleaned_data['from_session']
                tosession = leave_form.cleaned_data['to_session']

            if not manager:
                context_data['errors'].append('you are not assigned to any manager. please contact HR ')
                context_data['form'] = leave_form
            elif validate['errors']:
                for error in validate['errors']:
                    context_data['errors'].append(error)
                context_data['form'] = leave_form
            elif fromdate.year != todate.year:
                context_data['errors'].append('From Date and To date need to be in same year')
                context_data['form'] = leave_form
            else:

                leavecount = validate['success']
                leaveType=LeaveType.objects.get(leave_type= leave_form.cleaned_data['leave'])

                leavesummry = LeaveSummary.objects.filter(leave_type=leaveType, user=user_id, year=leave_applied_year)
                if leavesummry:
                    leavesummry_temp = leavesummry[0]
                else:
                    user = User.objects.get(id=user_id)
                    leavesummry_temp = LeaveSummary.objects.create(user=user,
                                                                   leave_type=leaveType,
                                                                   applied=0,
                                                                   approved=0,
                                                                   balance=0,
                                                                   year=leave_applied_year)

                if leavesummry_temp.balance and float(leavesummry_temp.balance) >= leavecount:
                    if leave_form.cleaned_data['leave'] == 'comp_off_avail' and compOffAvailibilityCheck(fromdate,
                                                                                                         user_id):
                        context_data['errors'].append('For this time period there is no comp off ')
                        context_data['form'] = leave_form
                        return render(request, 'leave_apply.html', context_data)

                    leavesummry_temp.applied = float(leavesummry_temp.applied) + leavecount
                    leavesummry_temp.balance = float(leavesummry_temp.balance) - leavecount

                    if attachment:
                         LeaveApplications(leave_type=leaveType,
                                           from_date=fromdate,
                                           to_date=todate,
                                           from_session=fromsession,
                                           to_session=tosession,
                                           days_count=leavecount,
                                           reason=reason,
                                           atachement=attachment).saveas(user_id, request.user.id)
                         leavesummry_temp.save()
                         EmailSendTask.delay(request.user,
                                             manager,
                                             leave_selected,
                                             fromdate,
                                             todate,
                                             fromsession,
                                             tosession,
                                             leavecount,
                                             reason,
                                             'save')
                    else:
                         LeaveApplications(leave_type=leaveType,
                                           from_date=fromdate,
                                           to_date=todate,
                                           from_session=fromsession,
                                           to_session=tosession,
                                           days_count=leavecount,
                                           reason=reason).saveas(user_id, request.user.id)
                         leavesummry_temp.save()
                         EmailSendTask.delay(request.user,
                                             manager,
                                             leave_selected,
                                             fromdate,
                                             todate,
                                             fromsession,
                                             tosession,
                                             leavecount,
                                             reason,
                                             'save')

                    context_data['success']= 'leave saved'
                    context_data['record_added'] = 'True'
                else:
                    if leave_form.cleaned_data['leave'] in ['comp_off_earned',
                                                            'work_from_home',
                                                            'pay_off',
                                                            'loss_of_pay',
                                                            'ooo_dom',
                                                            'ooo_int']:
                        leavesummry_temp.applied = float(leavesummry_temp.applied) + leavecount

                        if attachment:
                             LeaveApplications(leave_type=leaveType,
                                               from_date=fromdate,
                                               to_date=todate,
                                               from_session=fromsession,
                                               to_session=tosession,
                                               days_count=leavecount,
                                               reason=reason,
                                               atachement=attachment,
                                               due_date=duedate).saveas(user_id,
                                                                        request.user.id)
                             leavesummry_temp.save()
                             EmailSendTask.delay(request.user,
                                                 manager,
                                                 leave_selected,
                                                 fromdate,
                                                 todate,
                                                 fromsession,
                                                 tosession,
                                                 leavecount,
                                                 reason,
                                                 'save')
                        else:
                             LeaveApplications(leave_type=leaveType,
                                               from_date=fromdate,
                                               to_date=todate,
                                               from_session=fromsession,
                                               to_session=tosession,
                                               days_count=leavecount,
                                               reason=reason,
                                               due_date=duedate).saveas(user_id,
                                                                        request.user.id)
                             leavesummry_temp.save()
                             EmailSendTask.delay(request.user,
                                                 manager,
                                                 leave_selected,
                                                 fromdate,
                                                 todate,
                                                 fromsession,
                                                 tosession,
                                                 leavecount,
                                                 reason,
                                                 'save')

                        context_data['success']= 'leave saved'
                        context_data['record_added'] = 'True'
                    else:
                        context_data['errors'].append('You do'
                                                      ' not have the necessary leave balance to avail of this leave.')
                        context_data['form'] = leave_form
                if context_data['errors']:
                    return render(request, 'leave_apply.html', context_data)
                else:
                    context_data['success_msg'] = "Your leave application has been submitted successfully."
                    template = render(request, 'leave_apply.html', context_data)
                    context_data['html_data'] = template.content
                    return JsonResponse(context_data)

        else:

            context_data['form'] = leave_form

        return render(request, 'leave_apply.html', context_data)


def managerCheck(user):
    manager_id = Employee.objects.filter(user_id=user).values('manager_id')
    manager = Employee.objects.filter(employee_assigned_id=manager_id).values('user_id')
    if manager:
        return User.objects.get(id=manager[0]['user_id'])


def export_xlwt_overridden(filename, fields, values_list, days_list, save=False, folder=""):
    """export_xlwt is a function based on http://reliablybroken.com/b/2009/09/outputting-excel-with-django/"""
    filename = slugify(filename)
    book = xlwt.Workbook(encoding='utf8')
    sheet = book.add_sheet(filename)
    from datetime import datetime, date
    default_style = xlwt.Style.default_style
    datetime_style = xlwt.easyxf(num_format_str='dd/mm/yyyy hh:mm')
    date_style = xlwt.easyxf(num_format_str='dd/mm/yyyy')
    for j, f in enumerate(fields):
        sheet.write(0, j, fields[j])

    for row, rowdata in enumerate(values_list):
        for col, val in enumerate(rowdata):
            if isinstance(val, datetime):
                style = datetime_style
            elif isinstance(val, date):
                style = date_style
            else:
                style = default_style
            if col == 2:
                for k, v in LEAVE_TYPES_CHOICES:
                    if k == val:
                        val = v
            if col == len(rowdata)-1:
                if rowdata[col] in days_list:
                    val = days_list[rowdata[col]]

            sheet.write(row + 1, col, val, style=style)
    if not save:
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename=%s.xls' % filename
        book.save(response)
        return response
    else:
        dirpath = '%s/%s' % (settings.MEDIA_ROOT, folder)
        if folder != "":
            import os
            if not os.path.exists(dirpath):
                os.makedirs(dirpath)
        filepath = '%s%s.xls' % (dirpath, filename)
        book.save(filepath)
        return "%s%s%s.xls" % (settings.MEDIA_URL, folder, filename)


months_choices = []
for i in range(1, 13):
    months_choices.append((i, calendar.month_name[i]))


def date_range(d1, d2):
    return (d1 + datetime.timedelta(days=i) for i in range((d2 - d1).days + 1))


def total_leave_days(leave_list):
    leave_days = {}
    if leave_list:
        for obj in leave_list:
            leave_days[obj.id] = obj.days_count
    return leave_days


def leave_list_all(manager_id, hr=True):
    current_year = datetime.datetime.now()
    start_date = str(current_year.year)+'-'+'1'+'-'+'1'
    end_date = str(current_year.year)+'-'+'12'+'-'+'31'
    if not manager_id:
        leave_list = LeaveApplications.objects.filter(
                        from_date__range=[start_date, end_date])
    elif hr:
        leave_list = LeaveApplications.objects.filter(
                        from_date__range=[start_date, end_date])
    elif not hr:
        leave_list = LeaveApplications.objects.filter(
                        from_date__range=[start_date, end_date], apply_to=manager_id)
    return leave_list


class LeaveListView(ListView):

    template_name = "Admin_View_All_Leaves.html"
    model = LeaveApplications
    leave_days = {}

    def get_context_data(self, **kwargs):
        context = super(LeaveListView, self).get_context_data(**kwargs)

        if self.request.user.groups.filter(name= settings.LEAVE_ADMIN_GROUP).exists() :
            if 'all' in self.kwargs:
                context['leave_list'] = leave_list_all(None, False)

            else:
                context['leave_list'] = LeaveApplications.objects.filter().order_by("-from_date")
            context['users'] = Employee.objects.filter(user__is_active=True).order_by('user__username')

        elif self.request.user.groups.filter(name='myansrsourcePM').exists():
            if 'all' in self.kwargs:
                context['leave_list'] = LeaveApplications.objects.filter(apply_to=self.request.user)
            else:
                context['leave_list'] = LeaveApplications.objects.filter(apply_to=self.request.user
                                                                        ).order_by("status", "-from_date")
            context['users'] = Employee.objects.filter\
                (manager__user=self.request.user).order_by('manager__user__username')

        else:
            raise PermissionDenied
        context['leave_list_count'] = len(context['leave_list'])
        #

        context['APPLICATION_STATUS'] = APPLICATION_STATUS
        context['LEAVE_TYPES_CHOICES'] = LEAVE_TYPES_CHOICES
        context['SESSION_STATUS'] = SESSION_STATUS
        context['BUTTON_NAME'] = BUTTON_NAME
        context['leave_days'] = total_leave_days(context['leave_list'])

        context['months_choices'] = months_choices
        context['apply_to'] = Employee.objects.exclude(manager__user__first_name__isnull=True).\
            values_list('manager__user__username', 'manager__user__id').distinct().order_by('manager__user__username')
        self.request.session['apply_to'] = context['apply_to']
        # context['users'] = User.objects.filter(is_active=True)
        self.request.session['users'] = context['users']
        form = LeaveListViewForm()
        context['form'] = form

        if 'page' not in self.request.GET:
            if 'leave_list' in self.request.session:
                del self.request.session['leave_list']

        if 'leave_list' in self.request.session:
            context['leave_list'] = self.request.session['leave_list']
        context['leave_list_inherit'] = context['leave_list']
        context['leave_list'] = paginator_handler(self.request, context['leave_list'])
        return context

    def post(self, request, *args, **kwargs):
        leave_list = []
        apply_to = ''
        selected_month = request.POST.get('month')
        if request.POST.get('application_status'):
            post_application_status = status = request.POST.get('application_status')
        else:
            post_application_status = status = ''
        if request.POST.get('from_date'):
            from_date = request.POST.get('from_date')
        else:
            from_date = ''

        if request.POST.get('to_date'):
            to_date = request.POST.get('to_date')
        else:
            to_date = ''
        if request.POST.get('apply_to'):
            apply_to = request.POST.get('apply_to')

        if not request.POST.get('apply_to') and self.request.user.groups.filter(name=settings.LEAVE_ADMIN_GROUP).exists():
            apply_to = ''
        elif not request.POST.get('apply_to') and self.request.user.groups.filter(name='myansrsourcePM').exists():
            apply_to = self.request.user

        if request.POST.get('users'):
            employee = request.POST.get('users')
        else:
            employee = ''
        form = LeaveListViewForm(request.POST)
        if status == 'all':
            status_list = ['open','approved', 'rejected', 'cancelled']
        else:
            status_list =[status]
        try:
            if status != '' and from_date != '' and to_date != '' and apply_to != '' and employee != '':
                leave_list = LeaveApplications.objects.filter(status__in=status_list, apply_to=apply_to,
                                                              from_date__range=[from_date, to_date], user=employee)  # all chosen

            if status != '' and from_date == '' and to_date == '' and apply_to == '' and employee == '':
                leave_list = LeaveApplications.objects.filter(status__in=status_list)  # only status

            if status == '' and from_date != '' and to_date != '' and apply_to == '' and employee == '':
                leave_list = LeaveApplications.objects.filter(from_date__range=[from_date, to_date])  # only date

            if status == '' and from_date == '' and to_date == ''and apply_to != '' and employee == '':
                leave_list = LeaveApplications.objects.filter(apply_to=apply_to)  # only apply_to

            if status == '' and from_date == '' and to_date == ''and apply_to == '' and employee != '':
                leave_list = LeaveApplications.objects.filter(user=employee)  # only user

            if status != '' and from_date == '' and to_date == ''and apply_to != '' and employee == '':
                leave_list = LeaveApplications.objects.filter(status__in=status_list, apply_to=apply_to)  # status and apply_to

            if status != '' and from_date == '' and to_date == ''and apply_to == '' and employee != '':
                leave_list = LeaveApplications.objects.filter(status__in=status_list, user=employee)  # status and user

            if status == '' and from_date == '' and to_date == ''and apply_to != '' and employee != '':
                leave_list = LeaveApplications.objects.filter(user=employee, apply_to=apply_to)  # user and apply_to

            if status != '' and from_date != '' and to_date != ''and apply_to == '' and employee == '':
                leave_list = LeaveApplications.objects.filter(status__in=status_list,
                                                              from_date__range=[from_date, to_date])  # status, date

            if status == '' and from_date != '' and to_date != ''and apply_to == '' and employee != '':
                leave_list = LeaveApplications.objects.filter(user=employee,
                                                              from_date__range=[from_date, to_date])  # user, date

            if status != '' and from_date != '' and to_date != ''and apply_to == '' and employee != '':
                leave_list = LeaveApplications.objects.filter(status__in=status_list, user=employee,
                                                              from_date__range=[from_date, to_date])  # status,user, date

            if status != '' and from_date != '' and to_date != ''and apply_to != '' and employee == '':
                leave_list = LeaveApplications.objects.filter(status__in=status_list, apply_to=apply_to,
                                                              from_date__range=[from_date, to_date])  # status,apply_to, date

            if status != '' and from_date == '' and to_date == ''and apply_to != '' and employee != '':
                leave_list = LeaveApplications.objects.filter(status__in=status_list, user=employee,
                                                              apply_to=apply_to)  # status,user, apply_to

            # if status != '' and from_date == '' and to_date == ''and apply_to != '' and employee != '':
            #     leave_list = LeaveApplications.objects.filter(status=status, user=employee,
            #                                                   apply_to=apply_to)  # status,user, apply_to
            #     print leave_list.query
            #     print "status,user, apply_to"

            if status == '' and from_date != '' and to_date != ''and apply_to != '' and employee != '':
                leave_list = LeaveApplications.objects.filter(apply_to=apply_to, user=employee,
                                                              from_date__range=[from_date, to_date])  # apply_to,user, date

            if status == '' and from_date != '' \
                    and to_date != '' and apply_to != '' and employee == '':
                leave_list = LeaveApplications.objects.filter(apply_to=apply_to,
                                                              from_date__range=[from_date, to_date])  # apply_to, date

        except:
            leave_list = None

        # leave_days = leave_calculation(leave_list.from_date, leave_list.to_date, leave_list.from_session,
        #                                leave_list.to_session, leave_list.leave_type)

        leave_days = total_leave_days(leave_list)


        if 'export' in request.POST:
            if from_date == '' and to_date == '' and status == '' and apply_to == '' \
                    and employee == '':
                if self.request.user.groups.filter(name= settings.LEAVE_ADMIN_GROUP).exists():
                    leave_list_export = leave_list_all(self.request.user, True)
                elif self.request.user.groups.filter(name='myansrsourcePM').exists():
                    leave_list_export = leave_list_all(self.request.user, False)

            else:
                leave_list_export = leave_list
            leave_days = total_leave_days(leave_list_export)

            fields = ['user__employee__employee_assigned_id', 'user__first_name', 'leave_type__leave_type',
                      'from_date', 'to_date', 'applied_on', 'modified_on',
                      'apply_to__first_name',  'status', 'reason', 'id']

            column_names = ['Employee Id', 'Employee Name ', 'Leave Type', 'From Date',
                            'To Date', 'Applied Date', 'Action Taken On',
                            'Applied to',  'Status', 'Reason', 'Days']

            file_name = "Leave Report - " + str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))

            try:
                return export_xlwt_overridden(file_name, column_names,
                                              leave_list_export.values_list(*fields), leave_days)
            except Exception, e:
                logger.error(e)

        if leave_list and leave_list.count > 0:
            self.request.session['leave_list'] = leave_list
            leave_list = paginator_handler(self.request, self.request.session['leave_list'])

        if not leave_list and 'leave_list' in self.request.session:
            del self.request.session['leave_list']
        return render(self.request,
                      self.template_name,
                      {'leave_list': leave_list,
                       'APPLICATION_STATUS': APPLICATION_STATUS,
                       'LEAVE_TYPES_CHOICES': LEAVE_TYPES_CHOICES,
                       'SESSION_STATUS': SESSION_STATUS,
                       'BUTTON_NAME': BUTTON_NAME,
                       'leave_days': leave_days,
                       'month': request.POST.get('month'),
                       'post_application_status': post_application_status,
                       'months_choices': months_choices,
                       'apply_to': self.request.session['apply_to'],
                       'users':  self.request.session['users'],
                       'post_apply_to': self.request.POST.get('apply_to'),
                       'post_users': self.request.POST.get('users'),
                       'form': form})


def update_leave_application(request, status):
    status_tmp = status.split('_')
    exception = False
    if request.POST.get('remark_'+status_tmp[1]):
        remark_tmp = request.POST.get('remark_'+status_tmp[1]).strip()
    else:
        remark_tmp = ''
    leave_application = LeaveApplications.objects.get(id=status_tmp[1])
    # print leave_application

    leave_application.status = status_tmp[0]
    leave_application.status_comments = remark_tmp
    leave_application.status_action_by = request.user
    leave_days = total_leave_days(LeaveApplications.objects.filter(id=status_tmp[1]))
    leave_days = leave_days[leave_application.id]
    leave_applied_year = leave_application.from_date.year
    try:
        leave_status = LeaveSummary.objects.get(user=leave_application.user, leave_type=leave_application.leave_type,
                                                year=leave_applied_year)

    except:
        leave_status = LeaveSummary.objects.create(user=leave_application.user, leave_type=leave_application.leave_type,
                                                   year=leave_applied_year)

        leave_status.approved = 0
        leave_status.balance = 0
        leave_status.applied = Decimal(leave_days)
    approved = Decimal(leave_status.approved)
    leave_status.approved = Decimal(leave_status.approved)
    leave_status.balance = Decimal(leave_status.balance)
    leave_status.applied = Decimal(leave_status.applied)
    is_com_off = LeaveType.objects.get(pk=leave_status.leave_type.id)
    if status_tmp[0] == 'approved':
        if is_com_off.leave_type == 'comp_off_earned':
            com_off_apply = LeaveSummary.objects.get(leave_type__leave_type='comp_off_avail',
                                                     user=leave_application.user.id,
                                                     year=leave_applied_year)
            com_off_apply.balance =Decimal(com_off_apply.balance) + Decimal(leave_days)
            # com_off_apply.balance = str(com_off_apply.balance)
            com_off_apply.save()
        # else:
        #     leave_status.balance -= Decimal(leave_days)
        #     leave_status.balance = str(leave_status.balance)
        leave_status.applied -= Decimal(leave_days)
        leave_status.approved += Decimal(leave_days)
        leave_status.applied = str(leave_status.applied)
        leave_status.approved = str(leave_status.approved)

    if status_tmp[0] == 'cancelled' or status_tmp[0] == 'rejected':
        #short leave check against cancel leave
        short_leave_against_cancellation(leave_application.from_date,
                                         leave_application.to_date,
                                         leave_application.user.id)
        leave_status.applied -= Decimal(leave_days)
        leave_status.applied = str(leave_status.applied)
        if is_com_off not in leaveWithoutBalance:
            leave_status.balance += Decimal(leave_days)
            leave_status.balance = str(leave_status.balance)

    leave_status.save()

    try:
        leave_application.save()
        ManagerEmailSendTask.delay(leave_application.user, is_com_off.leave_type, leave_application.status, leave_application.from_date,
        leave_application.to_date, leave_application.days_count, leave_application.status_comments, request.user)
        return True
    except Exception, e:
        logger.error(e)
        return False


class LeaveManageView(LeaveListView):
    def get_context_data(self, **kwargs):

        context = super(LeaveManageView, self).get_context_data(**kwargs)
        if self.request.user.groups.filter(name=settings.LEAVE_ADMIN_GROUP).exists():
            context['all'] = LeaveApplications.objects.all()
            context['open'] = context['leave_list_inherit'].filter(status='open')
        elif self.request.user.groups.filter(name='myansrsourcePM').exists():
            context['all'] = LeaveApplications.objects.filter(apply_to=self.request.user)
            context['open'] = context['leave_list_inherit'].filter(status='open', apply_to=self.request.user)
        context['open_count'] = len(context['open'])
        context['open'] = paginator_handler(self.request, context['open'])
        #
        return context

    def post(self, request, *args, **kwargs):
        save_failed = reject_failed = cancel_failed = save_email = reject_email = cancel_email = 0
        save_status = False
        if request.POST.getlist('approve'):
            for approve_obj in request.POST.getlist('approve'):
                save_status = update_leave_application(self.request, approve_obj)
                if not save_status:
                    save_failed += 1
                if type(save_status) is str:
                    save_email += 1
        if request.POST.getlist('reject'):
            for reject_obj in request.POST.getlist('reject'):
                reject_status = update_leave_application(self.request, reject_obj)
                if not reject_status:
                    reject_failed += 1
                if type(reject_status) is str:
                    reject_email += 1
        if request.POST.getlist('cancel'):
            for cancel_obj in request.POST.getlist('cancel'):
                cancel_status = update_leave_application(self.request, cancel_obj)
                if not cancel_status:
                    cancel_failed += 1
                if type(cancel_status) is str:
                    cancel_email += 1
        if cancel_email > 0 or reject_email > 0 or save_email > 0:
            messages.error(self.request, "Sorry Unable to Notify The "
                                         "Leave Application Status Update  By Email But  Leave "
                                         "Applications Are Processed Successfully")

        if save_failed > 0 or reject_failed > 0 or cancel_failed > 0:
            messages.warning(self.request, "Sorry Unable to Process Few Leave Applications")
        else:
            messages.success(self.request, "Successfully Updated")

        return HttpResponseRedirect("/leave/manage")




#This method returns the transction for the user in short leave table
def ShortAttendanceTransact(request):
    context = {'user_id':None, 'admin_access':False}
    statusType = request.GET.get('type')
    user_id = request.GET.get('user_id')
    logged_in_user = request.user.id
    if not user_id:
        user_id = request.user.id
    if request.user.groups.filter(name= settings.LEAVE_ADMIN_GROUP).exists() or int(logged_in_user)== int(user_id):
        context['admin_access'] =True


    Short_Leave_transact = ShortAttendance.objects.filter( user=user_id,
                                                         active=True).values('id',
                                                                             'for_date',
                                                                             'due_date',
                                                                  'status','dispute')
    context['user_id'] = user_id
    context['Short_Leave_transact'] = Short_Leave_transact
    return render(request, 'short_leave_transact.html',
                  context)


#details of every leave transaction
def ShortAttendanceDetail(request):
    leave_id = request.GET.get('leaveid')
    leave = ShortAttendance.objects.get(id=leave_id)
    return render(request, 'short_leave_details.html',
                  {'leave': leave, 'SHORT_ATTENDANCE_TYPE': SHORT_ATTENDANCE_TYPE})


def ShortAttendanceLock(*args, **kwargs):
    def lock(fntion):
        def decorated(*args,**kwargs):
            if settings.LEAVE_SHORT_ATTENDANCE_ISACTIVE:
                return fntion(*args, **kwargs)
            else:
                return False
    return lock()


class ShortAttendanceManageView(View):
    def get(self, request):
        if not settings.LEAVE_SHORT_ATTENDANCE_ISACTIVE:
            raise PermissionDenied("Sorry, you don't have permission to access this feature")
        context = {}
        if self.request.user.groups.filter(name= settings.LEAVE_ADMIN_GROUP).exists():
            context['shortAttendanceOpen'] = ShortAttendance.objects.filter(dispute="raised")

        elif self.request.user.groups.filter(name='myansrsourcePM').exists():
            context['shortAttendanceOpen'] = ShortAttendance.objects.filter(dispute="raised", apply_to=self.request.user)
        else:
            raise PermissionDenied("Sorry, you don't have permission to access this feature")

        context['shortAttendanceOpen'] = paginator_handler(self.request, context['shortAttendanceOpen'])
        return render(request, 'short_attendance_manage.html', context)

    def post(self, request, *args, **kwargs):
        save_failed = reject_failed = cancel_failed = save_email = reject_email = cancel_email = 0
        save_status = False
        if request.POST.getlist('approve'):
            for approve_obj in request.POST.getlist('approve'):
                save_status = UpdateShortAttendance(self.request, approve_obj)
                if not save_status:
                    save_failed += 1
                if type(save_status) is str:
                    save_email += 1
        if request.POST.getlist('reject'):
            for reject_obj in request.POST.getlist('reject'):
                reject_status = UpdateShortAttendance(self.request, reject_obj)
                if not reject_status:
                    reject_failed += 1
                if type(reject_status) is str:
                    reject_email += 1
        if request.POST.getlist('cancel'):
            for cancel_obj in request.POST.getlist('cancel'):
                cancel_status = UpdateShortAttendance(self.request, cancel_obj)
                if not cancel_status:
                    cancel_failed += 1
                if type(cancel_status) is str:
                    cancel_email += 1
        if cancel_email > 0 or reject_email > 0 or save_email > 0:
            messages.error(self.request, "Sorry Unable to Notify The "
                                         "Leave Application Status Update  By Email But  Leave "
                                         "Applications Are Processed Successfully")

        if save_failed > 0 or reject_failed > 0 or cancel_failed > 0:
            messages.warning(self.request, "Sorry Unable to Process Few short attendance Applications")
        else:
            messages.success(self.request, "Successfully Updated")

        return HttpResponseRedirect("/leave/shortleavemanage")





def UpdateShortAttendance(request, status):
    status_tmp = status.split('_')
    exception = False
    if request.POST.get('remark_'+status_tmp[1]):
        remark_tmp = request.POST.get('remark_'+status_tmp[1]).strip()
    else:
        remark_tmp = ''
    short_attendance = ShortAttendance.objects.get(id=status_tmp[1])
    if status_tmp[0] == 'approved':
        short_attendance.dispute = "approved"
        short_attendance.active = False

    short_attendance.status = status_tmp[0]
    short_attendance.status_comments = remark_tmp
    short_attendance.status_action_by = request.user
    short_attendance.dispute = "open"

    try:
        short_attendance.save()
        ShortAttendanceManagerActionEmailSendTask.delay(short_attendance.user,
                                                        short_attendance.short_leave_type,
                                                        short_attendance.status,
                                                        short_attendance.for_date,
                                                        short_attendance.due_date,
                                                        remark_tmp)
        # ManagerEmailSendTask.delay(leave_application.user, is_com_off.leave_type, leave_application.status, leave_application.from_date,
        # leave_application.to_date, leave_application.days_count, leave_application.status_comments, request.user)
        return True
    except Exception, e:
        logger.error(e)
        return False


class ApplyShortLeaveView(View):
    ''' add or edit leave '''

    def get(self, request):
        context_data = {'add': True, 'record_added': False, 'form': None, 'success_msg': None, 'html_data': None,
                        'errors': [],
                        'leave_type_check': None, 'leave': None,'leaveid':None}
        try:
            leavetype = request.GET.get('leavetype')
            leaveid = request.GET.get('leaveid')
            user_id = request.GET.get('user_id')
            onetime_leave = ['comp_off_avail', 'short_leave']
            count_not_required = ['comp_off_earned', 'pay_off', 'work_from_home', 'loss_of_pay', 'ooo_dom', 'ooo_int']
            if leaveid:
                shortAttendance = ShortAttendance.objects.get(id=leaveid)
                form = ShortLeaveForm(leavetype, user_id, shortAttendance.for_date,shortAttendance.id)
                context_data['leaveid'] = leaveid
            else:
                form = ShortLeaveForm(leavetype, user_id)
            context_data['form'] = form
            leave_count = LeaveSummary.objects.filter(leave_type__leave_type=leavetype, user_id=user_id,
                                                      year=date.today().year)
            if leavetype:
                context_data['leave'] = 'data'
            if leavetype in onetime_leave:
                context_data['leave_type_check'] = 'OneTime'

            if leavetype not in count_not_required and leave_count:
                context_data['leave_count'] = leave_count[0].balance

            return render(request, 'short_leave_apply_form.html', context_data)
        except:
            form = ShortLeaveForm('None', request.user.id)
            context_data['form'] = form
            return render(request, 'short_leave_apply_form.html', context_data)

    def post(self, request):
        user_id = request.POST['name']
        leaveid = request.POST['leave_id']
        if leaveid:
            shortAttendance = ShortAttendance.objects.get(id=leaveid)
            leave_form = ShortLeaveForm(request.POST['leave'], user_id,
                                        shortAttendance.for_date,
                                        shortAttendance.id,
                                        request.POST)
        else:
            leave_form = ShortLeaveForm(request.POST['leave'], user_id, request.POST)

        if not user_id:
            user_id = request.user.id

        context_data = {'add': True,
                        'record_added': False,
                        'form': None,
                        'success_msg': None,
                        'html_data': None,
                        'errors': [],
                        'leave_type_check': None,
                        'leave': 'formdata'
                        }

        if leave_form.is_valid() and not context_data['errors']:

            duedate = date.today()
            fromdate = leave_form.cleaned_data['fromDate']
            leave_apply_year = fromdate.year
            leave_selected = leave_form.cleaned_data['leave']
            try:
                context_data['leave_count'] = LeaveSummary.objects.filter(leave_type__leave_type=leave_selected,
                                                                          user_id=user_id,
                                                                          year=leave_apply_year)[0].balance
            except:
                context_data['errors'].append( 'No leave records found on myansrsource portal. Please contact HR.')
                context_data['form'] = leave_form
            onetime_leave = ['maternity_leave',
                             'paternity_leave',
                             'bereavement_leave',
                             'comp_off_earned',
                             'comp_off_avail',
                             'pay_off',
                             'short_leave']
            if leave_selected in onetime_leave:
                context_data['leave_type_check'] = 'OneTime'
            reason = leave_form.cleaned_data['Reason']
            manager = managerCheck(user_id)
            if leave_selected in onetime_leave:
                validate = oneTimeLeaveValidation(leave_form, user_id, leave_apply_year)
                fromdate = leave_form.cleaned_data['fromDate']
                todate = validate['todate']
                fromsession = 'session_first'
                tosession = 'session_second'
                if leave_selected in ['comp_off_earned', 'pay_off']:
                    duedate = validate['due_date']
            else:
                validate=leaveValidation(leave_form, user_id, leave_apply_year)
                fromdate = leave_form.cleaned_data['fromDate']
                todate = leave_form.cleaned_data['toDate']
                fromsession = leave_form.cleaned_data['from_session']
                tosession = leave_form.cleaned_data['to_session']

            if not manager:
                context_data['errors'].append('you are not assigned to any manager. please contact HR ')
                context_data['form'] = leave_form
            elif validate['errors']:
                for error in validate['errors']:
                    context_data['errors'].append(error)
                context_data['form'] = leave_form
            else:

                leavecount = validate['success']
                leaveType=LeaveType.objects.get(leave_type= leave_form.cleaned_data['leave'])

                leavesummry = LeaveSummary.objects.filter(leave_type=leaveType, user=user_id, year = leave_apply_year)
                if leavesummry:
                    leavesummry_temp = leavesummry[0]
                else:
                    user = User.objects.get(id=user_id)
                    leavesummry_temp = LeaveSummary.objects.create(user=user,
                                                                   leave_type=leaveType,
                                                                   applied=0,
                                                                   approved=0,
                                                                   balance=0,
                                                                   year=leave_apply_year)

                if leavesummry_temp.balance and float(leavesummry_temp.balance) >= leavecount:
                    if leave_form.cleaned_data['leave'] == 'comp_off_avail' and compOffAvailibilityCheck(fromdate, user_id):
                        context_data['errors'].append( 'For this time period there is no comp off ')
                        context_data['form'] = leave_form
                        return render(request, 'leave_apply.html', context_data)

                    leavesummry_temp.applied = float(leavesummry_temp.applied) + leavecount
                    leavesummry_temp.balance = float(leavesummry_temp.balance) - leavecount

                    ShortAttendanceResolution(leaveid, fromdate, fromsession, tosession, user_id)
                    LeaveApplications(leave_type=leaveType,
                                      from_date=fromdate,
                                      to_date=todate,
                                      from_session=fromsession,
                                      to_session=tosession,
                                      days_count=leavecount,
                                      reason=reason).saveas(user_id, request.user.id)
                    leavesummry_temp.save()
                    EmailSendTask.delay(request.user, manager, leave_selected, fromdate, todate, fromsession, tosession, leavecount, reason, 'save')

                    context_data['success'] = 'leave saved'
                    context_data['record_added'] = 'True'
                else:
                    if leave_form.cleaned_data['leave'] in ['comp_off_earned', 'work_from_home', 'pay_off',
                                                            'loss_of_pay',
                                                            'short_leave',
                                                            'ooo_dom',
                                                            'ooo_int']:
                        leavesummry_temp.applied = float(leavesummry_temp.applied) + leavecount
                        ShortAttendanceResolution(leaveid, fromdate, fromsession, tosession, user_id)
                        LeaveApplications(leave_type=leaveType,
                                          from_date=fromdate,
                                          to_date=todate,
                                          from_session=fromsession,
                                          to_session=tosession,
                                          days_count=leavecount,
                                          reason=reason,
                                          due_date= duedate).saveas(user_id, request.user.id)
                        leavesummry_temp.save()
                        EmailSendTask.delay(request.user,
                                            manager,
                                            leave_selected,
                                            fromdate,
                                            todate,
                                            fromsession,
                                            tosession,
                                            leavecount,
                                            reason,
                                            'save')

                        context_data['success']= 'leave saved'
                        context_data['record_added'] = 'True'
                    else:
                        context_data['errors'].append(
                            'You do not have the necessary leave balance to avail of this leave.')
                        context_data['form'] = leave_form

                    # return render(request, 'leave_apply.html', context_data)
                if context_data['errors']:

                    return render(request, 'short_leave_apply_form.html', context_data)
                else:
                    context_data['success_msg'] = "Your leave application has been submitted successfully."

                    template = render(request, 'short_leave_apply_form.html', context_data)
                    context_data['html_data'] = template.content
                    return JsonResponse(context_data)

        else:

            context_data['form'] = leave_form

        return render(request, 'short_leave_apply_form.html', context_data)


#short leave resolution
def ShortAttendanceResolution(leaveid, fromdate, fromsession, tosession, user):
    shortLeaves = ShortAttendance.objects.get(id=leaveid)
    leave = LeaveApplications.objects.filter(from_date__lte=fromdate,
                                             to_date__gte=fromdate,
                                             user=user,
                                             status__in=['open', 'approved'])
    if shortLeaves.short_leave_type == 'half_day':
        shortLeaves.active = False
        shortLeaves.save()
    elif fromsession == 'session_first' and tosession == 'session_second':
        shortLeaves.active = False
        shortLeaves.save()
    elif leave:
        shortLeaves.active = False
        shortLeaves.save()



class RaiseDispute(View):
    '''raise dispute form for comments'''

    def get(self, request):
        context_data = {'record_added': False}
        leaveid = request.GET.get('leaveid')
        shortAttendance = ShortAttendance.objects.get(id=leaveid)
        form = ShortAttendanceRemarkForm(initial={'leave_id':leaveid,'fordate':shortAttendance.for_date})
        context_data['form'] = form
        return render(request, 'short_attendance_remark.html', context_data)

    def post(self, request):
        form = ShortAttendanceRemarkForm(request.POST)
        context_data = {'record_added': False}
        if form.is_valid():

            leave_id = form.cleaned_data['leave_id']
            status_comment = form.cleaned_data['Reason']
            user_id = request.user.id
            user = User.objects.get(id=user_id)
            shortAttendance = ShortAttendance.objects.get(id=leave_id)
            shortAttendance.dispute = 'raised'
            shortAttendance.status_action_by = user
            shortAttendance.status_comments = status_comment
            shortAttendance.save()
            ShortAttendanceDisputeEmailSendTask.delay(user,
                                                      shortAttendance.short_leave_type,
                                                      shortAttendance.status,
                                                      shortAttendance.for_date,
                                                      shortAttendance.due_date,
                                                      status_comment,
                                                      shortAttendance.reason)
            context_data['record_added'] = True
            context_data['success_msg'] = "Your short attendance had sent for manager approval."
            template = render(request, 'short_attendance_remark.html', context_data)
            context_data['html_data'] = template.content
            return JsonResponse(context_data)
        else:

            form = ShortAttendanceRemarkForm(request.POST)
            context_data['form'] = form
        return render(request, 'short_attendance_remark.html', context_data)


def report(request):
    context = {}
    month = date.today().month
    user = request.user.id
    manager = Employee.objects.get(user_id=user)
    userlist = Employee.objects.filter(manager_id=manager.employee_assigned_id)
    userid = [user.user_id for user in userlist]
    userlist = User.objects.filter(id__in=userid, is_active=True)
    context['weekreport'] = weekwisereport(month, userlist)
    current_week_no = current_week()
    context['leavereport'] = leavereportweeklybasedonuser(month, userlist, current_week_no)
    context['current_week_no'] = current_week_no
    context['startdate'] = weekdetail(current_week_no, month)
    context['enddate'] = context['startdate'] + timedelta(5)
    no_of_avaliable_week = len(context['weekreport'])
    context['current_month_week_details'] = current_month_week_details(no_of_avaliable_week, month)
    context['month'] = month
    context['month_in_english'] = month_in_english(month)
    context['week_in_english'] = "Week " + str(current_week_no)
    context['team_data'] = "My Team"
    context['next_week'] = next_week_detail(no_of_avaliable_week, current_week_no, month)
    if month == 1:
        previous_month_detail = weekwisereport(12, userlist)
    else:
        previous_month_detail = weekwisereport(month-1, userlist)
    context['previous_week'] = previous_week_detail(len(previous_month_detail), current_week_no, month)
    return render(request, 'leavereport.html', context)


def next_week_detail(no_of_avaliable_week, current_week_no, month):
    week_detail = [0, 0]
    if current_week_no == no_of_avaliable_week and month == 12:
        week_detail[0] = 1
        week_detail[1] = 1
    elif current_week_no == no_of_avaliable_week:
        week_detail[0] = 1
        week_detail[1] = month + 1
    else:
        week_detail[0] = current_week_no + 1
        week_detail[1] = month
    return week_detail


def previous_week_detail(no_of_avaliable_week, current_week_no, month):
    week_detail = [0, 0]
    if current_week_no == 1 and month == 1:
        week_detail[0] = 1
        week_detail[1] = 12
    elif current_week_no == 1:
        week_detail[0] = no_of_avaliable_week
        week_detail[1] = month - 1
    else:
        week_detail[0] = current_week_no - 1
        week_detail[1] = month
    return week_detail


def current_month_week_details(no_of_week, month):
    weeks_detail = []
    week_detail = [0, 0]
    for val in range(1, no_of_week+1):
        week_detail[0] = weekdetail(val, month)
        week_detail[1] = week_detail[0] + timedelta(5)
        weeks_detail.append(week_detail)
        week_detail = [0, 0]
    return weeks_detail


def month_in_english(month):
    month_list = ['', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
                  'September', 'October', 'November', 'December']
    return month_list[month]


def leavereportweeklybasedonuser(month, userlist, week):
    weekreport = []
    userdata = []
    for user in userlist:
        userdata.append(user.first_name + " " + user.last_name)
        userdata.append(userweeklyleavereport(user, week, month))
        weekreport.append(userdata)
        userdata = []
    return weekreport


def userweeklyleavereport(user, week, month):
    leavelist = []
    startdate = weekdetail(week, month)
    enddate = startdate + timedelta(5)
    for single_date in daterange(startdate, enddate):
        leavelist.append(leavecheck(user, single_date))
    return leavelist


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


def weekdetail(week, month):
    currentmontdetail = monthrange(date.today().year, month)
    daysinpreviousmonth = currentmontdetail[0]
    startdate = date(year=date.today().year,
                                 month=month,
                                 day=1+7*(week-1)) - timedelta(daysinpreviousmonth)
    return startdate


def weekwisereport(month, userlist):
    # import ipdb;ipdb.set_trace()
    weekreport = []
    weekreportdetail = {}
    currentmontdetail = monthrange(date.today().year, month)
    if month == 1:
        previousmontdetail = monthrange(date.today().year, 12)
    else:
        previousmontdetail = monthrange(date.today().year, month - 1)

    previousmonthdays = previousmontdetail[1]
    dayscount = currentmontdetail[1]
    available = 0
    unavailable = 0
    holiday = 0
    for val in range(0, currentmontdetail[0]):
        if month == 1:
            datecheck = date(year=date.today().year-1, month=12, day=previousmonthdays - val)
        else:
            datecheck = date(year=date.today().year, month=month - 1, day=previousmonthdays - val)
        for user in userlist:
            check = leavecheck(user, datecheck)
            if check == 0:
                available += 1
            elif check == 1:
                available += .5
                unavailable += .5
            elif check == 2:
                unavailable += 1
            else:
                holiday += 1
    if currentmontdetail[0] == 6:
        weekreportdetail['available'] = available
        weekreportdetail['unavailable'] = unavailable
        weekreportdetail['holiday'] = holiday
        weekreport.append(weekreportdetail)
        available = 0
        unavailable = 0
        holiday = 0
        weekreportdetail = {}

    for val in range(1, dayscount+1):
        date1 = date(year=date.today().year, month=month, day=val)
        if date1.strftime("%A") == 'Saturday':
            weekreportdetail['available'] = available
            weekreportdetail['unavailable'] = unavailable
            weekreportdetail['holiday'] = holiday
            weekreport.append(weekreportdetail)
            available = 0
            unavailable = 0
            holiday = 0
            weekreportdetail = {}

        elif date1.strftime("%A") == 'Sunday':
            pass
        elif val == dayscount+1:
            weekreportdetail['available'] = available
            weekreportdetail['unavailable'] = unavailable
            weekreportdetail['holiday'] = holiday
            weekreport.append(weekreportdetail)
            available = 0
            unavailable = 0
            holiday = 0
            weekreportdetail = {}


        else:
            for user in userlist:
                check = leavecheck(user, date1)
                if check == 0:
                    available += 1
                elif check == 1:
                    available += .5
                    unavailable += .5
                elif check == 2:
                    unavailable += 1
                else:
                    holiday += 1

    return weekreport


def leavecheck(user, date):
    leaveapplied = LeaveApplications.objects.filter(user=user.id,
                                                    from_date__lte=date,
                                                    to_date__gte=date,
                                                    status__in=['open', 'approved']).exclude(leave_type=11)
    holiday = Holiday.objects.all().values('date')

    if len(leaveapplied) > 1:
        flag = 2
    elif leaveapplied and leaveapplied[0].from_date < date and leaveapplied[0].to_date > date:
        flag = 2
    elif leaveapplied and\
                    leaveapplied[0].from_date == date and\
                    leaveapplied[0].to_date > date and\
                    leaveapplied[0].from_session == 'session_first':
        flag = 2
    elif leaveapplied and\
                    leaveapplied[0].from_date < date and\
                    leaveapplied[0].to_date == date and\
                    leaveapplied[0].to_session == 'session_second':
        flag = 2
    elif leaveapplied and\
                    leaveapplied[0].from_date == date and\
                    leaveapplied[0].to_date == date and\
                    leaveapplied[0].from_session == 'session_first'and\
            leaveapplied[0].to_session == 'session_second':
        flag = 2
    elif leaveapplied:
        flag = 1
    elif date in [datedata['date'] for datedata in holiday]:
        flag = 3
    else:
        flag = 0
    return flag


def monthwisedata(request):
    month = int(request.GET.get('month'))
    context = {}
    user = request.user.id
    team = request.GET.get('team')
    if team == 'peers':
        manager_detail = Employee.objects.get(user_id=user)
        user = Employee.objects.get(employee_assigned_id=manager_detail.manager.employee_assigned_id).user_id
    manager = Employee.objects.get(user_id=user)
    userlist = Employee.objects.filter(manager_id=manager.employee_assigned_id)
    userid = [user.user_id for user in userlist]
    userlist = User.objects.filter(id__in=userid, is_active=True)
    current_week_no = current_week()
    context['weekreport'] = weekwisereport(month, userlist)
    context['startdate'] = weekdetail(current_week_no, month)
    context['enddate'] = context['startdate'] + timedelta(5)
    context['team'] = team
    return render(request, 'monthlyreport.html', context)


def weekwisedata(request):
    context = {}
    week = int(request.GET.get('week'))
    month = int(request.GET.get('month'))
    user = request.user.id
    team = request.GET.get('team')
    context['team_data'] = "My Team"
    if team == 'peers':
        manager_detail = Employee.objects.get(user_id=user)
        user = Employee.objects.get(employee_assigned_id=manager_detail.manager.employee_assigned_id).user_id
        context['team_data'] = "My Peers"
    manager = Employee.objects.get(user_id=user)
    userlist = Employee.objects.filter(manager_id=manager.employee_assigned_id)
    userid = [user.user_id for user in userlist]
    userlist = User.objects.filter(id__in=userid, is_active=True)
    context['weekreport'] = weekwisereport(month, userlist)
    context['leavereport'] = leavereportweeklybasedonuser(month, userlist, week)
    no_of_avaliable_week = len(context['weekreport'])
    context['current_month_week_details'] = current_month_week_details(no_of_avaliable_week, month)
    context['startdate'] = weekdetail(week, month)
    context['enddate'] = context['startdate'] + timedelta(5)
    context['month'] = month
    context['team'] = team
    context['month_in_english'] = month_in_english(month)
    context['next_week'] = next_week_detail(no_of_avaliable_week, week, month)
    if month == 1:
        previous_month_detail = weekwisereport(12, userlist)
    else:
        previous_month_detail = weekwisereport(month-1, userlist)
    context['previous_week'] = previous_week_detail(len(previous_month_detail), week, month)
    context['current_week_no'] = week
    context['week_in_english'] = "Week " + str(week)
    return render(request, 'weeklyreport.html', context)


def current_week():
    today = date.today()
    month_detail = monthrange(today.year, today.month)
    week = today.day + month_detail[0]
    week /= 7
    week += 1
    return week




def adminleavecancel(request):
    user_id=request.user.id
    leave_id = request.GET.get('leaveid')
    leavecount = request.GET.get('leavecount')
    status = request.GET.get('status')
    leave = LeaveApplications.objects.get(id = leave_id)
    leave_year_date = leave.from_date.year
    leaveSummary = LeaveSummary.objects.get(leave_type=leave.leave_type, user=leave.user_id, year=leave_year_date)
    onetimeLeave = ['maternity_leave', 'paternity_leave', 'bereavement_leave']
    if leave.leave_type.leave_type in leaveWithoutBalance:
        leavededuct = float(leavecount)

    elif leave.leave_type.leave_type in onetimeLeave:
        leaveSummary.balance = float(leavecount)
        leavededuct = 0

    else:
        leaveSummary.balance = float(leaveSummary.balance) + float(leavecount)
        leavededuct = float(leavecount)

    if int(status) == 1:
        leaveSummary.applied = float(leaveSummary.applied) - float(leavededuct)
    else:
        leaveSummary.approved = float(leaveSummary.approved) - float(leavededuct)
    leaveSummary.save()
    leave.status = 'cancelled'
    leave.status_action_on = date.today()
    leave.status_action_by = User.objects.get(id=user_id)
    leave.status_comments = "Leave cancelled by admin"
    leave.update()
    candidate = User.objects.get(id=leave.user_id)
    ApproveLeaveCancelEmailSendTask.delay(candidate,
                                          leave.leave_type.leave_type,
                                          leave.status,
                                          leave.from_date,
                                          leave.to_date,
                                          leave.from_session,
                                          leave.to_session,
                                          leave.days_count,
                                          leave.reason,
                                          request.user)
    data1 = "leave cancelled"
    json_data = json.dumps(data1)
    return HttpResponse(json_data, content_type="application/json")


def balance_based_on_year(request):
    date = str(request.GET.get('from_date'))
    user = request.GET.get('user')
    leaveSelected = request.GET.get('leaveSelected')
    leaveType = LeaveType.objects.get(leave_type=leaveSelected)
    leaveSummary = LeaveSummary.objects.get(user=user, year=date[:4], leave_type=leaveType.id)
    json_data = json.dumps(leaveSummary.balance)
    return HttpResponse(json_data, content_type="application/json")


def short_leave_against_cancellation(from_date, to_date, user):
    '''
    :param from_date: From date of cancel leave
    :param to_date: To date of cancel leave
    :return: updates the short attendance flag.
    '''
    short_leaves = ShortAttendance.objects.filter(for_date__gte=from_date,
                                                  for_date__lte=to_date,
                                                  user_id=user,
                                                  active=False)
    for leave in short_leaves:
        leave.active = True
        leave.save()

