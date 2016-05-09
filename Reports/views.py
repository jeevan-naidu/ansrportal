from django.shortcuts import render
from django.views.generic import View
from Reports.forms import MilestoneReportsForm
from MyANSRSource.models import ProjectMilestone
from django.forms.fields import DateField
import csv
from django.http import HttpResponse
import datetime
date_instance = DateField()


class MilestoneReportsView(View):
    ''' MilestoneReportsView '''

    def get(self, request):
        
        context_data = {'form':None}
        form = MilestoneReportsForm()
        context_data['form'] = form
        return render(request, 'milestone_reports.html', context_data)

    def post(self, request):

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
                                                                )
            elif request.POST.get('project', '') and closed != " " and financial == " ":
                # Project - Yes, closed - either True or False, financial - any
                MilestoneList = ProjectMilestone.objects.filter(project=request.POST['project'],
                                                                milestoneDate__gte=from_date,
                                                                milestoneDate__lte=to_date,
                                                                closed=closed
                                                                )

            elif request.POST.get('project', '') and financial != " " and closed == " ":
                # Project - Yes, closed - any, financial - either True or False
                MilestoneList = ProjectMilestone.objects.filter(project=request.POST['project'],
                                                                milestoneDate__gte=from_date,
                                                                milestoneDate__lte=to_date,
                                                                financial=financial
                                                                )
            elif request.POST.get('project', '') and financial != " " and closed != " ":
                # Project - Yes, closed - any, financial - either True or False
                MilestoneList = ProjectMilestone.objects.filter(project=request.POST['project'],
                                                                milestoneDate__gte=from_date,
                                                                milestoneDate__lte=to_date,
                                                                financial=financial,
                                                                closed=closed
                                                                )

            elif not request.POST.get('project', '') and closed != " " and financial != " ":
                # Project - Yes, closed - either True or False, financial - any
                MilestoneList = ProjectMilestone.objects.filter(milestoneDate__gte=from_date,
                                                                milestoneDate__lte=to_date,
                                                                financial=financial,
                                                                closed=closed
                                                                )

            elif not request.POST.get('project', '') and closed != " " and financial == " ":
                # Project - any, closed - Teither True or False, financial - any
                MilestoneList = ProjectMilestone.objects.filter(milestoneDate__gte=from_date,
                                                                milestoneDate__lte=to_date,
                                                                closed=closed
                                                                )

            elif not request.POST.get('project', '') and financial != " " and closed == " ":
                # Project - any, financial - either True or False, closed - any
                MilestoneList = ProjectMilestone.objects.filter(milestoneDate__gte=from_date,
                                                                milestoneDate__lte=to_date,
                                                                financial=financial,
                                                                )
            elif not request.POST.get('project', '') and closed == " " and financial == " ":
                # Project - any, financial - any, closed - any
                MilestoneList = ProjectMilestone.objects.filter(milestoneDate__gte=from_date,
                                                                milestoneDate__lte=to_date,
                                                                )

            response = HttpResponse(content_type='text/csv')
            filename = "MilestoneReports_" + request.POST['from_date'] + "_to_" + request.POST['to_date'] + ".csv"
            response['Content-Disposition'] = 'attachment; filename="' + filename + '"'

            writer = csv.writer(response)
            writer.writerow(['Project Id', 'Project Name', 'Milestone Date', 'Description', 'Amount', 'Closed Status',
                             'Is Financial', 'Closed On', 'Updated On'])
            for obj in MilestoneList:
                writer.writerow([obj.project.projectId, obj.project.name, obj.milestoneDate, obj.description,
                                 obj.amount, obj.closed, obj.financial, obj.closedon, obj.updatedOn])
            if MilestoneList:
                return response
            else:
                context_data['errors'] = "No Milestones found"
        return render(request, 'milestone_reports.html', context_data)


