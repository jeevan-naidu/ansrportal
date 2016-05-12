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
from validations import leaveValidation, leave_calculation, oneTimeLeaveValidation
import employee

AllowedFileTypes = ['jpg', 'csv','png', 'pdf', 'xlsx', 'xls', 'docx', 'doc', 'jpeg', 'eml']

def LeaveTransaction(request):
    month = request.GET.get('month')
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    year = date.today().year
    monthselected1 = date(year, months.index(month)+2,1)
    monthselected2 = date(year, months.index(month)+1,1)
    Leave_transact=LeaveApplications.objects.filter(Q(from_date__lt = monthselected1) & Q(from_date__gte = monthselected2), ~Q(status = 'cancelled'), user=request.user.id,leave_type__leave_type=request.GET.get('leave') ).values('id','leave_type__leave_type', 'from_date', 'from_session', 'to_date', 'to_session','due_date','status')
    for val in range(0, len(Leave_transact)):
        count = leave_calculation(Leave_transact[val]['from_date'], Leave_transact[val]['to_date'], Leave_transact[val]['from_session'], Leave_transact[val]['to_session'], Leave_transact[val]['leave_type__leave_type'])
        Leave_transact[val]['due_date'] = count
    count = 0
    data1 = "<tr class=""><th>No</th><th>From</th><th>To</th><th>Days</th></tr>"
    for leave in Leave_transact:
        count=count+1
        data1 =data1+ '<tr class="success"><td>{0}<br><a \
         onclick ="showDetails({1})" role="button" data-toggle="modal" title="View Details">Details</a>\
         </td><td>{2}<br>{3}</td><td>{4}, <br>{5}</td><td>{6}<br>\
         <div id="modal-leave-cancel" >'.format(
        count,
        leave['id'],
        leave['from_date'],
        leave['from_session'],
        leave['to_date'],
        leave['to_session'],
        leave['due_date'],
        )
        if leave['status'] == 'open':
            data1 = data1 + '<a  role="button" onclick="CancelLeave({0},{1})" >cancel</a></div>\
            </td></tr>'.format(leave['id'],leave['due_date'],)
        else:
            data1 = data1 + '</div></td></tr>'
    json_data = json.dumps(data1)
    return HttpResponse(json_data, content_type="application/json")

def LeaveCancel(request):
    user_id=request.user.id
    leave_id = request.GET.get('leaveid')
    leavecount = request.GET.get('leavecount')
    leave = LeaveApplications.objects.get(id = leave_id)
    leaveSummary = LeaveSummary.objects.get(type=leave.leave_type, user=user_id)
    leaveSummary.balance = float(leaveSummary.balance) + float(leavecount)
    leaveSummary.applied = float(leaveSummary.applied) - float(leavecount)
    leaveSummary.save()
    leave.status = 'cancelled'
    leave.update()
    data1 = "leave cancelled"
    json_data = json.dumps(data1)
    return HttpResponse(json_data, content_type="application/json")

def LeaveDetails(request):
    leave_id = request.GET.get('leaveid')
    leaveTypeDictionary = dict(LEAVE_TYPES_CHOICES)
    leaveSessionDictionary = dict(SESSION_STATUS)
    leave = LeaveApplications.objects.get(id = leave_id)
    data = '<div id="detail_leave"><table class="table" id=""><thead><tr><th><b>PROPERTY<b></th><th><b>DETAILS<b></th></tr></thead>\
  <tbody><tr><th scope="row">Leave Type</th><td>{0}</td></tr>\
  <tr><th scope="row">From date and session</th><td>{1},{2}</td></tr>\
  <tr><th scope="row">To date and session</th><td>{3},{4}</td></tr>\
  <tr><th scope="row">manager</th><td>{5}</td></tr>\
  <tr><th scope="row">reason</th><td>{6}</td></tr>\
  <tr><th scope="row">status</th><td>{7}</td></tr>\
  <tr><th scope="row">status action on</th><td>{8}</td></tr>\
  <tr><th scope="row">status action by</th><td>{9}</td></tr>\
  <tr><th scope="row">Attachment</th><td>{10}</td></tr>\
  </tbody></table></div>'.format(
  leaveTypeDictionary[leave.leave_type.leave_type],
  leave.from_date,
  leaveSessionDictionary[leave.from_session],
  leave.to_date,
  leaveSessionDictionary[leave.to_session],
  leave.apply_to,
  leave.reason,
  leave.status,
  leave.status_action_on,
  leave.status_action_by,
  leave.atachement
  )
    json_data = json.dumps(data)
    return HttpResponse(json_data, content_type="application/json")

# Create your views here.
def Dashboard(request):
    myReportee = employee.models.Employee.objects.filter(manager=request.user.employee)
    isManager = 0
    if myReportee:
        isManager = 1
    leave_summary=LeaveSummary.objects.filter(user=request.user.id).values('type__leave_type', 'applied', 'approved', 'balance')
    context={'leave_summary':leave_summary, 'isManager':isManager }
    return render(request, 'User.html', context)


class ApplyLeaveView(View):
    ''' add or edit leave '''


    def get(self, request):
        #context_data = {'add':True, 'record_added':False, 'form':None}
        context_data={'add' : True, 'record_added' : False, 'form' : None, 'success_msg' : None, 'html_data' : None, 'errors' : []}
        try:
            leavetype=request.GET.get('leavetype')
            form = LeaveForm(leavetype)
            context_data['form'] = form
            leave_count = LeaveSummary.objects.filter(type__leave_type= leavetype)
            if leave_count:
                context_data['leave_count'] = leave_count[0].balance

            return render(request, 'leave_apply.html', context_data)
        except:
            form = LeaveForm('None')
            context_data['form'] = form
            return render(request, 'leave_apply.html', context_data)


    def post(self, request):
        leave_form=LeaveForm(request.POST['leave'], request.POST)
        response_data = {}
        context_data = {'add' : True, 'record_added' : False, 'form' : None, 'success_msg' : None, 'html_data' : None, 'errors' : [] }
        attachment = request.FILES.get('leave_attachment', "")
        if attachment:
            if request.FILES['leave_attachment'].name.split(".")[-1] not in AllowedFileTypes:
                context_data['errors'].append('Attachment : File type not allowed. Please select a valid file type and then submit again')

        #validations of leave

        if leave_form.is_valid() and not context_data['errors']:
            onetime_leave = ['maternity_leave', 'paternity_leave', 'bereavement_leave', 'comp_off_apply', 'comp_off_avail', 'pay_off']
            leave_selected = leave_form.cleaned_data['leave']
            user_id=request.user.id
            if leave_selected in onetime_leave:
                validate = oneTimeLeaveValidation(leave_form, user_id)
                todate = validate['todate']
                fromsession = 'session_first'
                tosession = 'session_second'
            else:
                validate=leaveValidation(leave_form, user_id, attachment)
                todate = leave_form.cleaned_data['toDate']
                fromsession = leave_form.cleaned_data['from_session']
                tosession = leave_form.cleaned_data['to_session']

            if validate['errors']:
                context_data['errors'].append(validate['errors'])
                context_data['form'] = leave_form
            else:
                leavecount = validate['success']
                leaveType=LeaveType.objects.get(leave_type= leave_form.cleaned_data['leave'])

                leavesummry = LeaveSummary.objects.filter(type=leaveType, user=user_id)
                if leavesummry:
                    leavesummry_temp = leavesummry[0]
                else:
                    user = User.objects.get(id=user_id)
                    leavesummry_temp = LeaveSummary(user=user, year='2016', type = leaveType,applied = 0,approved=0 , balance=0 )
                    leavesummry_temp.save()
                if leavesummry_temp.balance and float(leavesummry_temp.balance) >= leavecount:
                    leavesummry_temp.applied = float(leavesummry_temp.applied) + leavecount
                    leavesummry_temp.balance = float(leavesummry_temp.balance) - leavecount
                    leavesummry_temp.save()
                    if attachment:
                        LeaveApplications(leave_type=leaveType, from_date=leave_form.cleaned_data['fromDate'], to_date=todate, from_session=fromsession, to_session=tosession, reason=leave_form.cleaned_data['Reason'], atachement=attachment).saveas(user_id)
                    else:
                        LeaveApplications(leave_type=leaveType, from_date=leave_form.cleaned_data['fromDate'], to_date=todate, from_session=fromsession, to_session=tosession, reason=leave_form.cleaned_data['Reason']).saveas(user_id)

                    context_data['success']= 'leave saved'
                    context_data['record_added'] = 'True'
                else:
                    if leave_form.cleaned_data['leave'] in ['comp_off_apply','work_from_home','pay_off','loss_of_pay']:
                        leavesummry_temp.applied = float(leavesummry_temp.applied) + leavecount
                        leavesummry_temp.save()
                        if attachment:
                            LeaveApplications(leave_type=leaveType, from_date=leave_form.cleaned_data['fromDate'], to_date=todate, from_session=fromsession, to_session=tosession, reason=leave_form.cleaned_data['Reason'], atachement=attachment).saveas(user_id)
                        else:
                            LeaveApplications(leave_type=leaveType, from_date=leave_form.cleaned_data['fromDate'], to_date=todate, from_session=fromsession, to_session=tosession, reason=leave_form.cleaned_data['Reason']).saveas(user_id)
                        context_data['success']= 'leave saved'
                        context_data['record_added'] = 'True'
                    else:
                        context_data['errors'].append( 'Sorry you are not having this type of leave ')
                        context_data['form'] = leave_form

                    return render(request, 'leave_apply.html', context_data)
                context_data['success_msg'] = "Your leave has been submitted successfully."
                template = render(request, 'leave_apply.html', context_data)
                context_data['html_data'] = template.content

                return JsonResponse(context_data)

        else:
            context_data['form'] = leave_form

        return render(request, 'leave_apply.html', context_data)
