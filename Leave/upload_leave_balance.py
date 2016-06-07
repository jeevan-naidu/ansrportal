from django.shortcuts import render
from django.views.generic import View
from forms import UploadLeaveBalanceForm
# Create your views here.
import csv
import re
import datetime
from django.conf import settings
from django.core.exceptions import PermissionDenied
from forms import UploadLeaveBalanceForm
from employee.models import Employee
from models import LeaveType, LeaveSummary

def CheckAccessPermissions(request):
    if not request.user.groups.filter(name=settings.LEAVE_UPLOAD_PERMISSIONS_GROUP_NAME).exists():
            raise PermissionDenied("Sorry, you don't have permission to access this feature")

class UploadLeaveBalanceView(View):
    """ """

    def get(self, request):
        CheckAccessPermissions(request)
        context_data = {'add': True, 'record_added': False, 'form': None, 'salesforce_data_list':[]}
        form = UploadLeaveBalanceForm()
        context_data['form'] = form
        return render(request, 'upload_leave_balance.html', context_data)

    def post(self, request):
        CheckAccessPermissions(request)
        context_data = {'record_added': False, 'form': None, 'errors_list':[], 'errors': False,
                        'salesforce_data_list': [],'exception_type': None, 'exception': None, 'error_at_line': None}
        
        form = UploadLeaveBalanceForm(request.POST, request.FILES)
        context_data['form'] = form
        
        if form.is_valid():
            data_file = request.FILES.get('leave_balance_file', '')
            
            LEAVE_TYPES_CHOICES = (('earned_leave', 'Earned Leave'), ('sick_leave', 'Sick Leave'), ('casual_leave', 'Casual Leave'),
                ('loss_of_pay', 'Loss Of Pay'), ('bereavement_leave', 'Bereavement Leave'), ('maternity_leave', 'Maternity Leave'),
                ('paternity_leave', 'Paternity Leave'), ('comp_off_earned', 'Comp Off Earned'),
                ('comp_off_avail', 'Comp Off Avail'),('pay_off', 'Pay Off'), ('work_from_home', 'Work From Home'),
                ('sabbatical', 'Sabbatical'))
            
       
            
            columns_list = ['emp_id', 'name', 'bereavement_leave', 'casual_leave',
             'earned_leave', 'loss_of_pay', 'maternity_leave',
             'paternity_leave', 'pay_off', 'sick_leave', 'work_from_home']
            
            reader  = csv.reader(data_file , delimiter = ';')
            headers_list = reader.next()
            headers_list = [i.lower().replace(" ", "_") for i in headers_list]
            
            for index, row in enumerate(reader):
                try:
                    user_obj = ""
                    temp_var = re.findall("[a-zA-Z]|[0-9]", row[0])  # to check for empty rows in csv,empty row will not contain any characters so exlude it
                    if temp_var:
                        row_dict = dict(zip(headers_list, row))
                        emp_id = int(row_dict.get('emp_id'))
                        try:
                            user_obj = Employee.objects.get(employee_assigned_id=emp_id).user
                        except:
                            print "Emp id not found: " + str(emp_id)
                        
                        if user_obj:
                            for i in range(2,11):
                                leave_type_obj = LeaveType.objects.get(leave_type=columns_list[i])
                                obj, created = LeaveSummary.objects.get_or_create(user=user_obj, leave_type=leave_type_obj)
                                value = str(row_dict[columns_list[i]])
                                if "-" in value:
                                    value = value.split("-")[1]
                                obj.balance = value
                                obj.save()

                except Exception as e:

                    context_data['errors'] = True
                    context_data['errors_list'].append("\n\nLine:" + str(index+2) + " - Exception: " +
                               str(e))
                    context_data['error_at_line'] = index + 2
                
        return render(request, 'upload_leave_balance.html', context_data)
            
           
            
