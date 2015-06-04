import logging
logger = logging.getLogger('MyANSRSource')
from django.contrib.auth.decorators import login_required
from MyANSRSource.forms import TeamMemberPerfomanceReportForm, \
    ProjectPerfomanceReportForm, UtilizationReportForm
from MyANSRSource.models import TimeSheetEntry, ProjectChangeInfo, \
    ProjectMilestone, ProjectTeamMember
from django.shortcuts import render
from datetime import timedelta
from django.db.models import Sum, Count
from employee.models import Employee


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
                'chapter__name', 'activity__name', 'hold'
            ).annotate(dcount=Count('project__projectId'),
                       mondayh=Sum('mondayH'),
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
                       sundayq=Sum('sundayQ')
                       ).order_by('project__projectId', 'hold')
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
                    if eachData['chapter__name'] is None:
                        eachData['chapter__name'] = ' -  '
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
    pEffort = 0
    fresh = 1
    actualHours, actualTotal, plannedTotal, deviation = 0, 0, 0, 0
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
            ).values('description', 'financial', 'milestoneDate',
                     'amount', 'closed')
            tsData = TimeSheetEntry.objects.filter(project=cProject).values(
                'teamMember',
            ).annotate(mondayh=Sum('mondayH'),
                       tuesdayh=Sum('tuesdayH'),
                       wednesdayh=Sum('wednesdayH'),
                       thursdayh=Sum('thursdayH'),
                       fridayh=Sum('fridayH'),
                       saturdayh=Sum('saturdayH'),
                       sundayh=Sum('sundayH')
                       )
            if len(msData):
                for eachRec in msData:
                    if eachRec['financial']:
                        eachRec['financial'] = 'Yes'
                    else:
                        eachRec['financial'] = 'No'
                    if eachRec['closed'] is True:
                        eachRec['closed'] = 'Yes'
                    else:
                        eachRec['closed'] = 'No'
            if len(tsData):
                for eachTsData in tsData:
                    eachTsData['actual'] = eachTsData['mondayh'] + \
                        eachTsData['tuesdayh'] + \
                        eachTsData['wednesdayh'] + \
                        eachTsData['thursdayh'] + \
                        eachTsData['fridayh'] + \
                        eachTsData['saturdayh'] + \
                        eachTsData['sundayh']
                    emp = Employee.objects.get(user=eachTsData['teamMember'])
                    eachTsData['teamMember'] = emp.user.username
                    eachTsData['designation'] = emp.designation.name
                    effort = ProjectTeamMember.objects.filter(
                        project=cProject,
                        member=emp.user
                    ).values('plannedEffort')
                    pEffort = 0
                    if len(effort):
                        for eachEffort in effort:
                            pEffort = pEffort + eachEffort['plannedEffort']
                    eachTsData['planned'] = pEffort
                    try:
                        eachTsData[
                            'deviation'] = round(
                                eachTsData['actual'] / pEffort * 100)
                    except ZeroDivisionError:
                        eachTsData['deviation'] = 0
                try:
                    actualTotal = sum(
                        [eachTsData['actual'] for eachTsData in tsData])
                except ZeroDivisionError:
                    actualTotal = 0
                try:
                    plannedTotal = sum(
                        [eachTsData['planned'] for eachTsData in tsData])
                except ZeroDivisionError:
                    plannedTotal = 0
                try:
                    deviation = round(actualTotal / plannedTotal * 100)
                except ZeroDivisionError:
                    deviation = 0
    return render(request,
                  'MyANSRSource/reportproject.html',
                  {'form': form, 'basicData': basicData, 'fresh': fresh,
                   'crData': crData, 'tsData': tsData, 'msData': msData,
                   'actual': actualHours, 'actualTotal': actualTotal,
                   'plannedTotal': plannedTotal, 'deviation': deviation}
                  )


@login_required
def UtilizationReport(request):
    data = {}
    fresh = 1
    form = UtilizationReportForm()
    if request.method == 'POST':
        reportData = UtilizationReportForm(request.POST)
        if reportData.is_valid():
            reportMonth = reportData.cleaned_data['reportMonth'].month
            reportYear = reportData.cleaned_data['reportMonth'].year
            internalIdle = GenerateReport(request, reportMonth, reportYear,
                                          idle=True, internal=True)
            internalOthers = GenerateReport(request, reportMonth, reportYear,
                                           idle=False, internal=True)
            externalIdle = GenerateReport(request, reportMonth, reportYear,
                                          idle=True, internal=False)
            externalOthers = GenerateReport(request, reportMonth, reportYear,
                                            idle=False, internal=False)
            nonProd = TimeSheetEntry.objects.filter(
                wkstart__year=reportYear,
                wkstart__month=reportMonth,
                project__projectId__isnull=True
            ).values(
                'teamMember__username'
            ).annotate(
                monday=Sum('mondayH'),
                tuesday=Sum('tuesdayH'),
                wednesday=Sum('wednesdayH'),
                thursday=Sum('thursdayH'),
                friday=Sum('fridayH'),
                saturday=Sum('saturdayH'),
                sunday=Sum('sundayH'),
            ).order_by('teamMember__username')
            data = {'internalIdle': calcTotal(request, internalIdle)[0],
                    'internalIdleTotal': calcTotal(request, internalIdle)[1],
                    'intenalOthers': calcTotal(request, internalOthers)[0],
                    'internalOthersTotal': calcTotal(request, internalOthers)[1],
                    'externalIdle': calcTotal(request, externalIdle)[0],
                    'externalIdleTotal': calcTotal(request, externalIdle)[1],
                    'externalOthers': calcTotal(request, externalOthers)[0],
                    'externalOthersTotal': calcTotal(request, externalOthers)[1],
                    'nonProd': calcTotal(request, nonProd)[0],
                    'nonProdTotal': calcTotal(request, nonProd)[1]}
            fresh = 0
    return render(request,
                  'MyANSRSource/reportutilize.html',
                  {'form': form, 'data': data, 'fresh': fresh})


@login_required
def GenerateReport(request, reportMonth, reportYear, idle, internal):
    ts = TimeSheetEntry.objects.filter(
        wkstart__year=reportYear,
        wkstart__month=reportMonth,
        project__projectId__isnull=False,
        project__internal=internal)
    if idle:
        return ts.filter(
            task__name='Idle'
        ).values(
            'project__projectId', 'project__name'
        ).annotate(
            monday=Sum('mondayH'),
            tuesday=Sum('tuesdayH'),
            wednesday=Sum('wednesdayH'),
            thursday=Sum('thursdayH'),
            friday=Sum('fridayH'),
            saturday=Sum('saturdayH'),
            sunday=Sum('sundayH'),
        ).order_by('project__projectId')
    else:
        return ts.exclude(
            task__name='Idle'
        ).values(
            'project__projectId', 'project__name'
        ).annotate(
            monday=Sum('mondayH'),
            tuesday=Sum('tuesdayH'),
            wednesday=Sum('wednesdayH'),
            thursday=Sum('thursdayH'),
            friday=Sum('fridayH'),
            saturday=Sum('saturdayH'),
            sunday=Sum('sundayH'),
        ).order_by('project__projectId')


@login_required
def calcTotal(request, data):
    if len(data):
        grandTotal = 0
        for eachTsData in data:
            eachTsData['total'] = eachTsData['monday'] + \
                eachTsData['tuesday'] + \
                eachTsData['wednesday'] + \
                eachTsData['thursday'] + \
                eachTsData['friday'] + \
                eachTsData['saturday'] + \
                eachTsData['sunday']
        grandTotal = sum([eachRec['total'] for eachRec in data])
        return [data, grandTotal]
    else:
        return [{}, 0]
