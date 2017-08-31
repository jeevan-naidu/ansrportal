from django.shortcuts import render
from django.views.generic import View
from MyANSRSource.models import Project
from CompanyMaster.models import BusinessUnit
from forms import UploadSalesforceDataForm, SalesforceDataForm
from models import SalesforceData
from django.contrib import messages
import csv
import re
import datetime
from django.conf import settings
from django.core.exceptions import PermissionDenied


def CheckAccessPermissions(request):
    if not not request.user.groups.filter(name=settings.SALESFORCE_ADMIN_GROUP_NAME).exists() or \
            not request.user.groups.filter(name=settings.MANAGER).exists():
        raise PermissionDenied("Sorry, you don't have permission to access this feature")


class UploadSalesforceDataView(View):
    """ """

    def get(self, request):
        # CheckAccessPermissions(request)
        context_data = {'add': True, 'record_added': False, 'form': None, 'salesforce_data_list': []}
        form = UploadSalesforceDataForm()
        context_data['salesforce_data_list'] = SalesforceData.objects.all().order_by('-created_date')
        context_data['form'] = form
        return render(request, 'upload_salesforce_data.html', context_data)

    def post(self, request):
        # CheckAccessPermissions(request)
        context_data = {'record_added': False, 'form': None, 'errors_list': [], 'errors': False,
                        'salesforce_data_list': [], 'exception_type': None, 'exception': None, 'error_at_line': None}
        context_data['salesforce_data_list'] = SalesforceData.objects.all().order_by('-created_date')

        form = UploadSalesforceDataForm(request.POST, request.FILES)
        context_data['form'] = form

        if form.is_valid():
            data_file = request.FILES.get('salesforce_data_file', '')

            db_columns_list = ['opportunity_number', 'opportunity_name', 'business_unit', 'client_rep',
                               'account_name', 'amount', 'probability_(%)', 'expected_project_start_date',
                               'expected_project_end_date', 'estimated_close_date', 'stage']

            reader = csv.reader(data_file, delimiter=';')
            headers_list = reader.next()
            headers_list = [i.lower().replace(" ", "_") for i in headers_list]

            for index, row in enumerate(reader):
                try:
                    temp_var = re.findall("[a-zA-Z]|[0-9]", row[
                        0])  # to check for empty rows in csv,empty row will not contain any characters so exlude it
                    if temp_var:
                        row_dict = dict(zip(headers_list, row))

                        estimate_start_date = row_dict.get('expected_project_start_date', None)
                        if estimate_start_date:
                            estimate_start_date = datetime.datetime.strptime(estimate_start_date, '%m/%d/%Y').date()
                        else:
                            estimate_start_date = None

                        estimate_end_date = row_dict.get('expected_project_end_date', None)
                        if estimate_end_date:
                            estimate_end_date = datetime.datetime.strptime(estimate_end_date, '%m/%d/%Y').date()
                        else:
                            estimate_end_date = None

                        try:
                            obj = SalesforceData.objects.get(
                                opportunity_number=int(row_dict.get('opportunity_number', '').strip()))
                        except:
                            obj = SalesforceData()
                            obj.opportunity_number = int(row_dict.get('opportunity_number', '').strip())

                        obj.opportunity_name = row_dict.get('opportunity_name', '').strip()
                        obj.business_unit = row_dict.get('business_unit', '').strip()
                        obj.customer_contact = row_dict.get('client_rep', '').strip()
                        obj.account_name = row_dict.get('account_name', '').strip()
                        obj.value = row_dict.get('amount', '').strip()
                        obj.probability = row_dict.get('probability_(%)', '').strip()
                        obj.estimate_start_date = estimate_start_date
                        obj.estimate_end_date = estimate_end_date
                        obj.status = row_dict.get('stage', '').strip()
                        obj.save()
                except Exception as e:

                    context_data['errors'] = True
                    context_data['errors_list'].append("\n\nLine:" + str(index + 2) + " - Exception: " +
                                                       str(e))
                    context_data['error_at_line'] = index + 2
                    # return render(request, 'upload_salesforce_data.html', context_data)

        return render(request, 'upload_salesforce_data.html', context_data)


def contract_details(request):
    if request.method == 'GET':
        context = {"form": ""}
        form = SalesforceDataForm()
        context["form"] = form
        return render(request, 'contract_details.html', context)
    if request.method == 'POST':
        context = {"form": ""}
        user = request.user
        form = SalesforceDataForm(request.POST)
        if form.is_valid():
            opportunity_number = form.cleaned_data['opportunity_number']
            opportunity_name = form.cleaned_data['opportunity_name']
            value = form.cleaned_data['value']
            # estimate_start_date = form.cleaned_data['estimate_start_date']
            # estimate_end_date = form.cleaned_data['estimate_end_date']
            planned_start_date = form.cleaned_data['planned_start_date']
            planned_end_date = form.cleaned_data['planned_end_date']
            customer_contact = form.cleaned_data['customer_contact']
            account_name = form.cleaned_data['account_name']
            # if estimate_start_date > estimate_end_date:
            #     messages.error(request, 'Sorry, Estimated End date is greater than estimated start date')
            #     context['form'] = SalesforceDataForm(request.POST)
            #     return render(request, "contract_details.html", context)
            if planned_start_date > planned_end_date:
                messages.error(request, 'Sorry, Planned End date is greater than planned start date')
                context['form'] = SalesforceDataForm(request.POST)
                return render(request, "contract_details.html", context)
            if opportunity_name.isdigit():
                messages.error(request, 'Sorry, opportunity name cannot be only number')
                context['form'] = SalesforceDataForm(request.POST)
                return render(request, "contract_details.html", context)
            SalesforceData(user_id=user.id,
                           opportunity_number=opportunity_number,
                           # business_unit = business_unit,
                           opportunity_name=opportunity_name,
                           value=value,
                           # estimate_start_date=estimate_start_date,
                           # estimate_end_date=estimate_end_date,
                           planned_start_date=planned_start_date,
                           planned_end_date=planned_end_date,
                           customer_contact=customer_contact,
                           account_name=account_name).save()
            messages.success(request, 'Thanks')
            context['form'] = SalesforceDataForm()
            return render(request, 'contract_details.html', context)
        else:
            context['form'] = SalesforceDataForm(request.POST)
            context['form_errors'] = form.errors
        return render(request, 'contract_details.html', context)