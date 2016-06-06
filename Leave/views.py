from django.shortcuts import render
from django.views.generic import View
from django.views.generic.list import ListView
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from forms import *
from django.conf import settings
from models import *
from django.db.models import Q
import json
from datetime import date
from validations import leaveValidation, leave_calculation, oneTimeLeaveValidation, newJoineeValidation, compOffAvailibilityCheck
import employee
import calendar
from calendar import monthrange
from django.shortcuts import render
# from datetime import datetime, date
from decimal import *
from datetime import date,timedelta
from django.utils import timezone
from django.views.generic.list import ListView
from django.views.generic import TemplateView
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages
from forms import LeaveListViewForm
from Leave.models import LeaveApplications, APPLICATION_STATUS, LEAVE_TYPES_CHOICES, SESSION_STATUS, BUTTON_NAME
from CompanyMaster.models import *
from django.contrib.auth.models import User
from export_xls.views import export_xlwt
import datetime
from datetime import date
from employee.models import Employee
import logging
import xlwt
from django.template.defaultfilters import slugify
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.core.exceptions import PermissionDenied
from django.core.mail import EmailMessage
logger = logging.getLogger('MyANSRSource')

AllowedFileTypes = ['jpg', 'csv','png', 'pdf', 'xlsx', 'xls', 'docx', 'doc', 'jpeg', 'eml']
leaveTypeDictionary = dict(LEAVE_TYPES_CHOICES)
leaveSessionDictionary = dict(SESSION_STATUS)
leaveWithoutBalance = ['loss_of_pay', 'comp_off_earned', 'pay_off', 'work_from_home']

def LeaveTransaction(request):
    statusType = request.GET.get('type')
    statusDict = {  'Approved':'approved' , 'Rejected':'rejected', 'Cancelled':'cancelled', 'Open':'open'}
    Leave_transact=LeaveApplications.objects.filter(status = statusDict[statusType] , user=request.user.id,
    leave_type__leave_type=request.GET.get('leave') ).values('id','leave_type__leave_type', 'from_date', 'from_session', 'to_date',
    'to_session','days_count','status')
    # for val in range(0, len(Leave_transact)):
    #     count = leave_calculation(Leave_transact[val]['from_date'], Leave_transact[val]['to_date'], Leave_transact[val]['from_session'],
    #      Leave_transact[val]['to_session'], Leave_transact[val]['leave_type__leave_type'])
    #     Leave_transact[val]['due_date'] = count
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
        if leave['status'] == 'open':
            data1 = data1 + '<a  role="button" onclick="CancelLeave({0},{1})" >cancel</a></div>\
            </td></tr>'.format(leave['id'],leave['days_count'],)
        else:
            data1 = data1 + '</div></td></tr>'
    json_data = json.dumps(data1)
    return HttpResponse(json_data, content_type="application/json")

def LeaveCancel(request):
    user_id=request.user.id
    leave_id = request.GET.get('leaveid')
    leavecount = request.GET.get('leavecount')
    leave = LeaveApplications.objects.get(id = leave_id)
    leaveSummary = LeaveSummary.objects.get(leave_type=leave.leave_type, user=user_id)
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
    manager = managerCheck(user_id)
    # mailTrigger(request.user, manager, leave.leave_type.leave_type, leave.from_date, leave.to_date, leave.from_session,
    #leave.to_session, leave.reason, 'cancel')
    data1 = "leave cancelled"
    json_data = json.dumps(data1)
    return HttpResponse(json_data, content_type="application/json")


def LeaveDetails(request):
    leave_id = request.GET.get('leaveid')
    leave = LeaveApplications.objects.get(id = leave_id)
    if leave.atachement:
        atachmentURL = leave.atachement.url
    else:
        atachmentURL = ''
    data = '<div id="detail_leave"><table class="table" id=""><thead><tr><th><b>PROPERTY<b></th><th><b>DETAILS<b></th></tr></thead>\
  <tbody><tr><th scope="row">Leave Type</th><td>{0}</td></tr>\
  <tr><th scope="row">From date and session</th><td>{1},{2}</td></tr>\
  <tr><th scope="row">To date and session</th><td>{3},{4}</td></tr>\
  <tr><th scope="row">manager</th><td>{5}</td></tr>\
  <tr><th scope="row">reason</th><td>{6}</td></tr>\
  <tr><th scope="row">status</th><td>{7}</td></tr>\
  <tr><th scope="row">status action on</th><td>{8}</td></tr>\
  <tr><th scope="row">status action by</th><td>{9}</td></tr>\
  <tr><th scope="row">Attachment</th><td><a href="{10}">{11}</a></td></tr>\
  </tbody></table></div>'.format(
  leaveTypeDictionary[leave.leave_type.leave_type],
  leave.from_date,
  leaveSessionDictionary[leave.from_session],
  leave.to_date,
  leaveSessionDictionary[leave.to_session],
  leave.apply_to.first_name,
  leave.reason,
  leave.status,
  leave.status_action_on,
  leave.status_action_by.first_name,
  atachmentURL,
  atachmentURL
  )
    json_data = json.dumps(data)
    return HttpResponse(json_data, content_type="application/json")

# Create your views here.
def Dashboard(request):
    user_id = request.user.id
    leave_summary=LeaveSummary.objects.filter(user=user_id).values('leave_type__leave_type', 'applied', 'approved', 'balance')
    gender = Employee.objects.filter(user_id = user_id).values('gender')
    newuser = newJoineeValidation(user_id)
    genderFlag = True
    genderMale = False
    if not newuser:
        genderFlag =False
    if gender[0]['gender']=='M':
        genderMale =True
    manager = managerCheck(request.user.id)
    if manager:
        mangerfirstname = manager.first_name
    else:
        mangerfirstname = ''
    context={'leave_summary':leave_summary,'gender':genderFlag,'male':genderMale, 'manager': mangerfirstname }
    return render(request, 'User.html', context)


class ApplyLeaveView(View):
    ''' add or edit leave '''


    def get(self, request):
        #context_data = {'add':True, 'record_added':False, 'form':None}
        context_data={'add' : True, 'record_added' : False, 'form' : None, 'success_msg' : None, 'html_data' : None, 'errors' : [],
        'leave_type_check' : None, 'leave':None}
        try:
            leavetype=request.GET.get('leavetype')
            onetime_leave = ['maternity_leave', 'paternity_leave', 'bereavement_leave', 'comp_off_earned', 'comp_off_avail', 'pay_off']
            count_not_required = ['comp_off_earned','pay_off','work_from_home','loss_of_pay']
            form = LeaveForm(leavetype)
            context_data['form'] = form
            leave_count = LeaveSummary.objects.filter(leave_type__leave_type= leavetype, user_id= request.user.id)
            if leavetype:
                context_data['leave'] = 'data'
            if leavetype in onetime_leave:
                context_data['leave_type_check'] = 'OneTime'

            if leavetype not in count_not_required and leave_count:
                context_data['leave_count'] = leave_count[0].balance

            return render(request, 'leave_apply.html', context_data)
        except:
            form = LeaveForm('None')
            context_data['form'] = form
            return render(request, 'leave_apply.html', context_data)


    def post(self, request):
        leave_form=LeaveForm(request.POST['leave'], request.POST)
        response_data = {}
        context_data = {'add' : True, 'record_added' : False, 'form' : None, 'success_msg' : None, 'html_data' : None, 'errors' : [], 'leave_type_check' : None }


        attachment = request.FILES.get('leave_attachment', "")
        if attachment:
            if request.FILES['leave_attachment'].name.split(".")[-1] not in AllowedFileTypes:
                context_data['errors'].append('Attachment : File type not allowed. Please select a valid file type and then submit again')

        #validations of leave

        if leave_form.is_valid() and not context_data['errors']:
            duedate = date.today()
            leave_selected = leave_form.cleaned_data['leave']
            onetime_leave = ['maternity_leave', 'paternity_leave', 'bereavement_leave', 'comp_off_earned', 'comp_off_avail', 'pay_off']
            if leave_selected in onetime_leave:
                context_data['leave_type_check'] = 'OneTime'
            user_id=request.user.id
            reason=leave_form.cleaned_data['Reason']
            manager = managerCheck(user_id)
            if leave_selected in onetime_leave:
                validate = oneTimeLeaveValidation(leave_form, user_id)
                fromdate = leave_form.cleaned_data['fromDate']
                todate = validate['todate']
                fromsession = 'session_first'
                tosession = 'session_second'
                if leave_selected in ['comp_off_earned', 'pay_off']:
                    duedate = validate['due_date']


            else:
                validate=leaveValidation(leave_form, user_id, attachment)
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

                leavesummry = LeaveSummary.objects.filter(leave_type=leaveType, user=user_id)
                if leavesummry:
                    leavesummry_temp = leavesummry[0]
                else:
                    user = User.objects.get(id=user_id)
                    leavesummry_temp = LeaveSummary.objects.create(user=user, leave_type=leaveType, applied=0, approved=0, balance=0,
                                                               year=date.today().year)

                if leavesummry_temp.balance and float(leavesummry_temp.balance) >= leavecount:
                    if leave_form.cleaned_data['leave'] == 'comp_off_avail' and compOffAvailibilityCheck(fromdate, user_id):
                        context_data['errors'].append( 'for this time period there is no comp off ')
                        context_data['form'] = leave_form
                        return render(request, 'leave_apply.html', context_data)

                    leavesummry_temp.applied = float(leavesummry_temp.applied) + leavecount
                    leavesummry_temp.balance = float(leavesummry_temp.balance) - leavecount

                    if attachment:
                         LeaveApplications(leave_type=leaveType, from_date=fromdate, to_date=todate, from_session=fromsession, to_session=tosession,
                         days_count=leavecount, reason=reason, atachement=attachment).saveas(user_id)
                         leavesummry_temp.save()
                        #  mailTrigger(request.user, manager, leave_selected, fromdate, todate, fromsession, tosession, reason, 'save')
                    else:
                         LeaveApplications(leave_type=leaveType, from_date=fromdate, to_date=todate, from_session=fromsession, to_session=tosession,
                         days_count=leavecount, reason=reason).saveas(user_id)
                         leavesummry_temp.save()
                        #  mailTrigger(request.user, manager, leave_selected, fromdate, todate, fromsession, tosession, reason, 'save')

                    context_data['success']= 'leave saved'
                    context_data['record_added'] = 'True'
                else:
                    if leave_form.cleaned_data['leave'] in ['comp_off_earned','work_from_home','pay_off','loss_of_pay']:
                        leavesummry_temp.applied = float(leavesummry_temp.applied) + leavecount

                        if attachment:
                             LeaveApplications(leave_type=leaveType, from_date=fromdate, to_date=todate, from_session=fromsession, to_session=tosession,
                             days_count=leavecount, reason=reason, atachement=attachment, due_date= duedate).saveas(user_id)
                             leavesummry_temp.save()
                            #  mailTrigger(request.user, manager, leave_selected, fromdate, todate, fromsession, tosession, reason, 'save')
                        else:
                             LeaveApplications(leave_type=leaveType, from_date=fromdate, to_date=todate, from_session=fromsession, to_session=tosession,
                             days_count=leavecount, reason=reason, due_date= duedate).saveas(user_id)
                             leavesummry_temp.save()
                            #  mailTrigger(request.user, manager, leave_selected, fromdate, todate, fromsession, tosession, reason, 'save')

                        context_data['success']= 'leave saved'
                        context_data['record_added'] = 'True'
                    else:
                        context_data['errors'].append( 'Sorry you are not having this type of leave ')
                        context_data['form'] = leave_form

                    # return render(request, 'leave_apply.html', context_data)
                if context_data['errors']:
                    return render(request, 'leave_apply.html', context_data)
                else:
                    context_data['success_msg'] = "Your leave has been submitted successfully."
                    template = render(request, 'leave_apply.html', context_data)
                    context_data['html_data'] = template.content
                    return JsonResponse(context_data)

        else:
            context_data['form'] = leave_form

        return render(request, 'leave_apply.html', context_data)

def mailTrigger(user, manager, leave_selected, fromdate, todate, fromsession, tosession, reason, flag):
    fromdate = str(fromdate)+' Session: '+leaveSessionDictionary[fromsession]
    todate = str(todate)+' Session: '+leaveSessionDictionary[tosession]
    if flag == 'save':
        msg_html = render_to_string('email_templates/apply_leave.html', {'registered_by': user.first_name, 'leaveType':leaveTypeDictionary[leave_selected],
         'fromdate':fromdate, 'todate':todate})

        mail_obj = EmailMessage('New Leave applied - Leave Type - ' + leaveTypeDictionary[leave_selected], msg_html, settings.EMAIL_HOST_USER, [user.email],
        cc=['vivek.pradhan@ansrsource.com','shalini.bhagat@ansrsource.com'])
    elif flag == 'cancel':
        msg_html = render_to_string('email_templates/cancel_leave.html', {'registered_by': user.first_name, 'leaveType':leaveTypeDictionary[leave_selected],
        'fromdate':fromdate, 'todate':todate})

        mail_obj = EmailMessage('Leave canceled - Leave Type - ' + leaveTypeDictionary[leave_selected], msg_html, settings.EMAIL_HOST_USER, [user.email],
         cc=['vivek.pradhan@ansrsource.com','shalini.bhagat@ansrsource.com'])

    mail_obj.content_subtype = 'html'
    email_status = mail_obj.send()

    if email_status < 1:
        # TODO  - mail not sent, log this error
        pass

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
    leave_allowed_on_holiday = ['sabbatical', 'pay_off', 'comp_off_earned']
    holiday = Holiday.objects.all().values('date')
    holiday_in_leave = 0
    if leave_list:
        for obj in leave_list:

            if obj.leave_type.leave_type not in leave_allowed_on_holiday:
                for leave in holiday:
                    if leave['date'] >= obj.from_date and leave['date'] <= obj.to_date and leave['date'].strftime("%A") not in ("Saturday", "Sunday"):
                        holiday_in_leave = holiday_in_leave + 1

                daygenerator = (obj.from_date + timedelta(x + 1) for x in xrange(-1, (obj.to_date - obj.from_date).days))
                leavecount = sum(1 for day in daygenerator if day.weekday() < 5) - holiday_in_leave
                leave_days[obj.id] = leavecount
            else:
                leavecount = (obj.to_date - obj.from_date).days + 1
                leave_days[obj.id] = leavecount
            if obj.from_session=='session_second' and obj.from_date.strftime("%A") not in ("Saturday", "Sunday"):
                leavecount=leavecount-.5
                leave_days[obj.id] = leavecount
            elif obj.to_session == 'session_first' and obj.to_date.strftime("%A") not in ("Saturday", "Sunday"):
                leavecount=leavecount-.5
                leave_days[obj.id] = leavecount

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
        if self.request.user.groups.filter(name='myansrsourcePM').exists():
            if 'all' in self.kwargs:
                context['leave_list'] = LeaveApplications.objects.filter(apply_to=self.request.user)
            else:
                context['leave_list'] = LeaveApplications.objects.filter(apply_to=self.request.user,
                                                                         status='open').order_by("status", "-from_date")
            context['users'] = Employee.objects.filter\
                (manager__user=self.request.user).order_by('manager__user__username')

        elif self.request.user.groups.filter(name='myansrsourceHR').exists() or self.request.user.is_superuser:
            if 'all' in self.kwargs:
                context['leave_list'] = leave_list_all(None, False)

            else:
                context['leave_list'] = LeaveApplications.objects.filter(status='open').order_by("-from_date")
            context['users'] = Employee.objects.filter(user__is_active=True).order_by('manager__user__username')

        else:
            raise PermissionDenied

        context['APPLICATION_STATUS'] = APPLICATION_STATUS
        context['LEAVE_TYPES_CHOICES'] = LEAVE_TYPES_CHOICES
        context['SESSION_STATUS'] = SESSION_STATUS
        context['BUTTON_NAME'] = BUTTON_NAME
        context['leave_days'] = total_leave_days(context['leave_list'])

        context['months_choices'] = months_choices
        context['apply_to'] = Employee.objects.exclude(manager__user__first_name__isnull=True).\
            values_list('manager__user__username', 'manager__user__id').distinct()
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

        if not request.POST.get('apply_to') and self.request.user.groups.filter(name='myansrsourcePM').exists():
            apply_to = self.request.user

        if request.POST.get('users'):
            employee = request.POST.get('users')
        else:
            employee = ''
        form = LeaveListViewForm(request.POST)

        try:
            if status != '' and from_date != '' and to_date != '' and apply_to != '' and employee != '':
                leave_list = LeaveApplications.objects.filter(status=status, apply_to=apply_to,
                                                              from_date__range=[from_date, to_date], user=employee)  # all chosen

            if status != '' and from_date == '' and to_date == '' and apply_to == '' and employee == '':
                leave_list = LeaveApplications.objects.filter(status=status)  # only status

            if status == '' and from_date != '' and to_date != '' and apply_to == '' and employee == '':
                leave_list = LeaveApplications.objects.filter(from_date__range=[from_date, to_date])  # only date

            if status == '' and from_date == '' and to_date == ''and apply_to != '' and employee == '':
                leave_list = LeaveApplications.objects.filter(apply_to=apply_to)  # only apply_to

            if status == '' and from_date == '' and to_date == ''and apply_to == '' and employee != '':
                leave_list = LeaveApplications.objects.filter(user=employee)  # only user

            if status != '' and from_date == '' and to_date == ''and apply_to != '' and employee == '':
                leave_list = LeaveApplications.objects.filter(status=status, apply_to=apply_to)  # status and apply_to

            if status != '' and from_date == '' and to_date == ''and apply_to == '' and employee != '':
                leave_list = LeaveApplications.objects.filter(status=status, user=employee)  # status and user

            if status == '' and from_date == '' and to_date == ''and apply_to != '' and employee != '':
                leave_list = LeaveApplications.objects.filter(user=employee, apply_to=apply_to)  # user and apply_to

            if status != '' and from_date != '' and to_date != ''and apply_to == '' and employee == '':
                leave_list = LeaveApplications.objects.filter(status=status,
                                                              from_date__range=[from_date, to_date])  # status, date

            if status == '' and from_date != '' and to_date != ''and apply_to == '' and employee != '':
                leave_list = LeaveApplications.objects.filter(user=employee,
                                                              from_date__range=[from_date, to_date])  # user, date

            if status != '' and from_date != '' and to_date != ''and apply_to == '' and employee != '':
                leave_list = LeaveApplications.objects.filter(status=status, user=employee,
                                                              from_date__range=[from_date, to_date])  # status,user, date

            if status != '' and from_date != '' and to_date != ''and apply_to != '' and employee == '':
                leave_list = LeaveApplications.objects.filter(status=status, apply_to=apply_to,
                                                              from_date__range=[from_date, to_date])  # status,apply_to, date

            if status != '' and from_date == '' and to_date == ''and apply_to != '' and employee != '':
                leave_list = LeaveApplications.objects.filter(status=status, user=employee,
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
                if self.request.user.groups.filter(name='myansrsourcePM').exists():
                    leave_list_export = leave_list_all(self.request.user, False)
                elif self.request.user.groups.filter(name='myansrsourceHR').exists() or self.request.user.is_superuser:
                    leave_list_export = leave_list_all(self.request.user, True)
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

        if not leave_list and 'leave_list' in self.request.session:
            del self.request.session['leave_list']

        if 'leave_list' in self.request.session:
            leave_list = self.request.session['leave_list']

        return render(self.request, self.template_name, {'leave_list': leave_list,
                                                         'APPLICATION_STATUS': APPLICATION_STATUS,
                                                         'LEAVE_TYPES_CHOICES': LEAVE_TYPES_CHOICES,
                                                         'SESSION_STATUS': SESSION_STATUS,
                                                         'BUTTON_NAME': BUTTON_NAME, 'leave_days': leave_days,
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
    try:
        leave_status = LeaveSummary.objects.get(user=leave_application.user, leave_type=leave_application.leave_type,
                                                year=date.today().year)

    except:
        leave_status = LeaveSummary.objects.create(user=leave_application.user, leave_type=leave_application.leave_type,
                                                   year=date.today().year)

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
            com_off_apply = LeaveSummary.objects.get(leave_type__leave_type='comp_off_avail',user=leave_application.user.id)
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
        leave_status.applied -= Decimal(leave_days)
        leave_status.applied = str(leave_status.applied)
        if is_com_off not in leaveWithoutBalance:
            leave_status.balance += Decimal(leave_days)
            leave_status.balance = str(leave_status.balance)

    leave_status.save()

    try:
        leave_application.save()
        msg_html = render_to_string('email_templates/leave_status.html',
                                    {'registered_by': leave_application.user.first_name,
                                     'status': leave_application.status,
                                     'from_date': leave_application.from_date,
                                     'to_date': leave_application.to_date,
                                     'comment': leave_application.status_comments,
                                     'action_taken_by': request.user.username})

        mail_obj = EmailMessage('Leave Application Status',
                                msg_html, settings.EMAIL_HOST_USER, [leave_application.user.email],
                                cc=[leave_application.apply_to.email])

        mail_obj.content_subtype = 'html'
        email_status = mail_obj.send()
        if email_status == 0:
                    logger.error(
                        "Unable To send Mail To The Authorities For"
                        "The Following Leave Applicant : {0} Date time : {1} ".format(
                         leave_application.user.first_name, timezone.make_aware(datetime.datetime.now(),
                                                                                timezone.get_default_timezone())))
                    return "failed"

        return True
    except Exception, e:
        logger.error(e)
        return False


class LeaveManageView(LeaveListView):

    def get_context_data(self, **kwargs):
        context = super(LeaveManageView, self).get_context_data(**kwargs)
        if self.request.user.groups.filter(name='myansrsourcePM').exists():
            context['all'] = LeaveApplications.objects.filter(apply_to=self.request.user)
            context['open'] = context['leave_list'].filter(status='open', apply_to=self.request.user)

        elif self.request.user.groups.filter(name='myansrsourceHR').exists() or self.request.user.is_superuser:
            context['all'] = LeaveApplications.objects.all()
            context['open'] = context['leave_list'].filter(status='open')

        return context

    def post(self, request, *args, **kwargs):
        save_failed = reject_failed = cancel_failed = save_email = reject_email = cancel_email = 0
        save_status = False
        if request.POST.getlist('approve'):
            for approve_obj in request.POST.getlist('approve'):
                print approve_obj
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
