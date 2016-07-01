from django.shortcuts import render
from django.views.generic import View
from Reports.forms import MilestoneReportsForm
from MyANSRSource.models import ProjectMilestone
from django.forms.fields import DateField
import csv
from django.http import HttpResponse
import datetime
from django.core.exceptions import PermissionDenied
from django.conf import settings
from django.utils import timezone

date_instance = DateField()


class MilestoneReportsView(View):
    ''' MilestoneReportsView '''

    def get(self, request):

        if not request.user.groups.filter(name=settings.MILESTONE_REPORTS_ADMIN_GROUP_NAME).exists():
            raise PermissionDenied("Sorry, you don't have permission to access this feature")

        context_data = {'form':None}
        form = MilestoneReportsForm()
        context_data['form'] = form
        return render(request, 'milestone_reports.html', context_data)

    def post(self, request):

        if not request.user.groups.filter(name=settings.MILESTONE_REPORTS_ADMIN_GROUP_NAME).exists():
            raise PermissionDenied("Sorry, you don't have permission to access this feature")

        form = MilestoneReportsForm(request.POST)
        context_data = {'form': form, 'errors': ""}

        if form.is_valid():

            from_date = request.POST['from_date'].replace("/", "")
            to_date = request.POST['to_date'].replace("/", "")
            from_date = datetime.datetime.strptime(from_date, "%m%d%Y").date()
            to_date = datetime.datetime.strptime(to_date, "%m%d%Y").date()

            if request.POST['milestone_type'] == 'financial':
                financial = True
            elif request.POST['milestone_type'] == 'non_financial':
                financial = False
            else:
                financial = " "

            if request.POST['milestone_status'] == 'completed':
                closed = True
            elif request.POST['milestone_status'] == 'not_completed':
                closed = False
            else:
                closed = " "

            if request.POST.get('project', '') and closed == " " and financial == " ":
                # Project - Yes, closed - Any, financial - any
                MilestoneList = ProjectMilestone.objects.filter(project=request.POST['project'],
                                                                milestoneDate__gte = from_date,
                                                                milestoneDate__lte = to_date,
                                                                ).order_by('milestoneDate')
            elif request.POST.get('project', '') and closed != " " and financial == " ":
                # Project - Yes, closed - either True or False, financial - any
                MilestoneList = ProjectMilestone.objects.filter(project=request.POST['project'],
                                                                milestoneDate__gte=from_date,
                                                                milestoneDate__lte=to_date,
                                                                closed=closed
                                                                ).order_by('milestoneDate')

            elif request.POST.get('project', '') and financial != " " and closed == " ":
                # Project - Yes, closed - any, financial - either True or False
                MilestoneList = ProjectMilestone.objects.filter(project=request.POST['project'],
                                                                milestoneDate__gte=from_date,
                                                                milestoneDate__lte=to_date,
                                                                financial=financial
                                                                ).order_by('milestoneDate')
            elif request.POST.get('project', '') and financial != " " and closed != " ":
                # Project - Yes, closed - any, financial - either True or False
                MilestoneList = ProjectMilestone.objects.filter(project=request.POST['project'],
                                                                milestoneDate__gte=from_date,
                                                                milestoneDate__lte=to_date,
                                                                financial=financial,
                                                                closed=closed
                                                                ).order_by('milestoneDate')

            elif not request.POST.get('project', '') and closed != " " and financial != " ":
                # Project - Yes, closed - either True or False, financial - any
                MilestoneList = ProjectMilestone.objects.filter(milestoneDate__gte=from_date,
                                                                milestoneDate__lte=to_date,
                                                                financial=financial,
                                                                closed=closed
                                                                ).order_by('milestoneDate')

            elif not request.POST.get('project', '') and closed != " " and financial == " ":
                # Project - any, closed - Teither True or False, financial - any
                MilestoneList = ProjectMilestone.objects.filter(milestoneDate__gte=from_date,
                                                                milestoneDate__lte=to_date,
                                                                closed=closed
                                                                ).order_by('milestoneDate')

            elif not request.POST.get('project', '') and financial != " " and closed == " ":
                # Project - any, financial - either True or False, closed - any
                MilestoneList = ProjectMilestone.objects.filter(milestoneDate__gte=from_date,
                                                                milestoneDate__lte=to_date,
                                                                financial=financial,
                                                                ).order_by('milestoneDate')
            elif not request.POST.get('project', '') and closed == " " and financial == " ":
                # Project - any, financial - any, closed - any
                MilestoneList = ProjectMilestone.objects.filter(milestoneDate__gte=from_date,
                                                                milestoneDate__lte=to_date,
                                                                ).order_by('milestoneDate')

            response = HttpResponse(content_type='text/csv')
            filename = "MilestoneReports_" + request.POST['from_date'] + "_to_" + request.POST['to_date'] + ".csv"
            response['Content-Disposition'] = 'attachment; filename="' + filename + '"'

            writer = csv.writer(response)
            writer.writerow(['Project Id', 'Project Name', "Leads/PM's", 'Milestone Date', 'Description', 'Amount',
                             'Closed Status', 'Is Financial', 'Customer Contact', 'Closed On', 'Updated On'])
            for obj in MilestoneList:
                
                leads_list = ",".join(i.first_name + " " + i.last_name for i in obj.project.projectManager.all())
                writer.writerow([obj.project.projectId, obj.project.name, leads_list, obj.milestoneDate, obj.description,
                                 obj.amount, obj.closed, obj.financial, obj.project.customerContact, obj.closedon, obj.updatedOn])
            if MilestoneList:
                return response
            else:
                context_data['errors'] = "No Milestones found"
        return render(request, 'milestone_reports.html', context_data)


