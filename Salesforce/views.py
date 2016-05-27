from django.shortcuts import render
from django.views.generic import View
from forms import UploadSalesforceDataForm
from models import SalesforceData
# Create your views here.
import csv
import re
import datetime


class UploadSalesforceDataView(View):
    """ """

    def get(self, request):

        context_data = {'add': True, 'record_added': False, 'form': None}
        form = UploadSalesforceDataForm()
        context_data['form'] = form
        return render(request, 'upload_salesforce_data.html', context_data)

    def post(self, request):
        
        context_data = {'record_added': False, 'form': None, 'errors': False, 'exception_type': None, 'exception': None, 'error_at_line': None}
        import ipdb;ipdb.set_trace()
        data_file = request.FILES.get('salesforce_data_file', '')
        
        db_columns_list = ['opportunity_number', 'opportunity_name', 'business_unit', 'client_rep',
                           'account_name', 'amount', 'probability_(%)', 'expected_project_start_date',
                           'expected_project_end_date', 'estimated_close_date', 'stage']
        
        reader  = csv.reader(data_file , delimiter = ';')
        headers_list = reader.next()
        headers_list = [i.lower().replace(" ", "_") for i in headers_list]
        
        for index, row in enumerate(reader):
            try:
                temp_var = re.findall("[a-zA-Z]|[0-9]", row[0])  # to check for empty rows in csv,empty row will not contain any characters so exlude it
                if temp_var:
                    row_dict = dict(zip(headers_list, row))
                    
                    start_date = row_dict['expected_project_start_date']
                    start_date = datetime.datetime.strptime(start_date, '%m/%d/%Y').date()
                    end_date = row_dict['expected_project_end_date']
                    end_date = datetime.datetime.strptime(end_date, '%m/%d/%Y').date()
                    
                    
                    try:
                        obj = SalesforceData.objects.get(opportunity_number=int(row_dict['opportunity_number']))
                    except:
                        obj = SalesforceData()
                        obj.opportunity_number = int(row_dict['opportunity_number'])
                    
                    obj.opportunity_name = row_dict['opportunity_name']
                    obj.business_unit = row_dict['business_unit']
                    obj.customer_contact = row_dict['client_rep']
                    obj.account_name = row_dict['account_name']
                    obj.value = row_dict['amount']
                    obj.probability = row_dict['probability_(%)']
                    obj.start_date = start_date
                    obj.end_date = end_date
                    obj.status = row_dict['stage']
                    obj.save()
            except Exception as e:
                context_data['exception_type'] = type(e)
                context_data['exception'] = e.args
                context_data['errors'] = True
                context_data['error_at_line'] = index
        
        return render(request, 'upload_salesforce_data.html', context_data)
            
           
            
