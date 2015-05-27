import logging
logger = logging.getLogger('MyANSRSource')
from django.contrib.auth.decorators import login_required
from MyANSRSource.forms import TeamMemberPerfomanceReportForm, \
    ProjectPerfomanceReportForm
from MyANSRSource.models import TimeSheetEntry, ProjectChangeInfo, \
    ProjectMilestone
from django.shortcuts import render
from datetime import timedelta
from django.db.models import Sum


@login_required
def TeamMemberReport(request):
    report = {}
    form = TeamMemberPerfomanceReportForm()
    name, wkstart, wkend, grdTotal = '', '', '', 0
    fresh = 1
    if request.method == 'POST':
        reportData = TeamMemberPerfomanceReportForm(request.POST)
        if reportData.is_valid():
            start = reportData.cleaned_data['startDate'].weekday()
            end = 6 - reportData.cleaned_data['endDate'].weekday()
            wkstartDate = reportData.cleaned_data['startDate'] - timedelta(
                days=start)
            wkendDate = reportData.cleaned_data['endDate'] + timedelta(
                days=end)
            report = TimeSheetEntry.objects.filter(
                teamMember=reportData.cleaned_data['member'],
                wkstart__gte=wkstartDate,
                wkend__lte=wkendDate,
            ).values(
                'teamMember__username', 'project__maxProductivityUnits',
                'project__projectId', 'project__name',
                'project__book__name', 'task__name',
                'chapter__name', 'activity__name', 'wkstart', 'wkend'
            ).annotate(mondayh=Sum('mondayH'),
                       tuesdayh=Sum('tuesdayH'),
                       wednesdayh=Sum('wednesdayH'),
                       thursdayh=Sum('thursdayH'),
                       fridayh=Sum('fridayH'),
                       saturdayh=Sum('saturdayH'),
                       sundayh=Sum('sundayH'),
                       mondayq=Sum('mondayQ'),
                       tuesdayq=Sum('tuesdayQ'),
                       wednesdayq=Sum('wednesdayQ'),
                       thursdayq=Sum('thursdayQ'),
                       fridayq=Sum('fridayQ'),
                       saturdayq=Sum('saturdayQ'),
                       sundayq=Sum('sundayQ')).order_by(
                'project__projectId')
            days = ['monday', 'tuesday', 'wednesday',
                    'thursday', 'friday', 'saturday',
                    'sunday']
            if len(report):
                for eachData in report:
                    if eachData['project__projectId'] is None:
                        eachData['project__projectId'] = ' - '
                    if eachData['project__name'] is None:
                        eachData['project__name'] = ' - '
                    if eachData['project__book__name'] is None:
                        eachData['project__book__name'] = ' - '
                    if eachData['task__name'] is None:
                        eachData['task__name'] = ''
                    if eachData['activity__name'] is None:
                        eachData['activity__name'] = ''
                    if eachData['project__maxProductivityUnits'] is None:
                        eachData['project__maxProductivityUnits'] = ' - '
                    eachData['totalHours'], eachData['totalValue'] = 0, 0
                    eachData['avgProd'], eachData['minProd'] = 0, 0
                    eachData['maxProd'], eachData['medianProd'] = 0, 0
                    units = []
                    for k, v in eachData.iteritems():
                        if k in ['{0}h'.format(eachDay) for eachDay in days]:
                            eachData['totalHours'] += v
                        if k in ['{0}q'.format(eachDay) for eachDay in days]:
                            units.append(v)
                            eachData['totalValue'] += v
                    eachData['maxProd'] = max(units)
                    eachData['minProd'] = min(units)
                    eachData['avgProd'] = round(sum(units) / len(units), 2)
                    eachData['medianProd'] = units[len(units) // 2]
                grdTotal = sum([eachData['totalHours'] for eachData in report])
                name = report[0]['teamMember__username']
                wkstart = wkstartDate
                wkend = wkendDate
                fresh = 2
            else:
                fresh = 0
        else:
            logging.error(reportData.errors)
            fresh = 1
    return render(request,
                  'MyANSRSource/reportmember.html',
                  {'form': form, 'data': report, 'member': name,
                   'fresh': fresh, 'wkstart': wkstart, 'wkend': wkend,
                   'grandTotal': grdTotal
                   }
                  )


@login_required
def ProjectReport(request):
    basicData = {}
    crData = []
    tsData = []
    msData = []
    fresh = 1
    actualHours = 0
    deviation = 0
    form = ProjectPerfomanceReportForm(user=request.user)
    if request.method == 'POST':
        fresh = 0
        reportData = ProjectPerfomanceReportForm(request.POST,
                                                 user=request.user)
        if reportData.is_valid():
            cProject = reportData.cleaned_data['project']
            basicData = {
                'name': cProject.name,
                'startDate': cProject.startDate,
                'endDate': cProject.endDate,
                'plannedEffort': cProject.plannedEffort,
                'totalValue': cProject.totalValue
            }
            crData = ProjectChangeInfo.objects.filter(
                project=cProject
            ).values('crId', 'reason', 'endDate', 'po', 'revisedEffort',
                     'revisedTotal', 'salesForceNumber', 'closed',
                     'closedOn', 'signed')
            msData = ProjectMilestone.objects.filter(
                project=cProject
            ).values('description', 'financial', 'amount', 'closed')
            tsData = TimeSheetEntry.objects.filter(project=cProject).values(
                'wkstart', 'wkend', 'teamMember__username',
                'mondayH', 'tuesdayH', 'wednesdayH',
                'thursdayH', 'fridayH', 'saturdayH', 'sundayH'
            )
            if len(msData):
                for eachRec in msData:
                    if eachRec['financial']:
                        eachRec['financial'] = 'Y'
                    else:
                        eachRec['financial'] = 'N'
                    if eachRec['closed'] is True:
                        eachRec['closed'] = 'Yes'
                    else:
                        eachRec['closed'] = 'No'
            if len(tsData):
                for eachTsData in tsData:
                    eachTsData['total'] = eachTsData['mondayH'] + \
                        eachTsData['tuesdayH'] + \
                        eachTsData['wednesdayH'] + \
                        eachTsData['thursdayH'] + \
                        eachTsData['fridayH'] + \
                        eachTsData['saturdayH'] + \
                        eachTsData['sundayH']
                    actualHours = actualHours + eachTsData['total']
                deviation = basicData['plannedEffort'] - actualHours
    return render(request,
                  'MyANSRSource/reportproject.html',
                  {'form': form, 'basicData': basicData, 'fresh': fresh,
                   'crData': crData, 'tsData': tsData, 'msData': msData,
                   'actual': actualHours, 'deviation': deviation}
                  )
