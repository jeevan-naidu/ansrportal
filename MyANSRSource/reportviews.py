import logging
logger = logging.getLogger('MyANSRSource')
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from MyANSRSource.forms import TeamMemberPerfomanceReportForm, \
    ProjectPerfomanceReportForm, UtilizationReportForm, BTGForm, \
    BTGReportForm, InvoiceForm
from MyANSRSource.models import TimeSheetEntry, ProjectChangeInfo, \
    ProjectMilestone, ProjectTeamMember, ProjectManager, Project, \
    BTGReport
from CompanyMaster.models import BusinessUnit
from django.contrib.auth.decorators import permission_required
from django.shortcuts import render
from datetime import timedelta, datetime
from django.db.models import Sum, Count
from employee.models import Employee
from django.core.servers.basehttp import FileWrapper
from dateutil import relativedelta as rdelta
from django.http import HttpResponse
import mimetypes
import numpy
import xlsxwriter
import os
import string


days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday',
        'sunday']


@login_required
@permission_required('MyANSRSource.create_project')
def BalanceToGo(request):
    form = BTGForm(user=request.user)
    data = BTGReport.objects.filter(member=request.user).values(
        'btgMonth', 'btgYear', 'btg', 'project__projectId', 'project__name'
    )
    if request.method == 'POST':
        savedForm = BTGForm(request.POST, user=request.user)
        if savedForm.is_valid():
            old = BTGReport.objects.filter(
                project=savedForm.cleaned_data['project'],
                btgYear=savedForm.cleaned_data['year'],
                btgMonth=savedForm.cleaned_data['month']
            ).values('id')
            if old:
                balancetogo = BTGReport.objects.get(id=old[0]['id'])
                balancetogo.btg = savedForm.cleaned_data['btg']
                balancetogo.member = request.user
                balancetogo.save()
            else:
                balancetogo = BTGReport()
                balancetogo.project = savedForm.cleaned_data['project']
                balancetogo.member = request.user
                balancetogo.btg = savedForm.cleaned_data['btg']
                balancetogo.btgYear = savedForm.cleaned_data['year']
                balancetogo.btgMonth = savedForm.cleaned_data['month']
                balancetogo.save()
    return render(request, 'MyANSRSource/reportbtg.html',
                  {'form': form, 'data': data})


@login_required
@permission_required('MyANSRSource.create_project')
def Invoice(request):
    form = InvoiceForm(user=request.user)
    data = BTGReport.objects.filter(member=request.user).values(
        'btgMonth', 'btgYear', 'currMonthIN',
        'project__projectId', 'project__name'
    )
    if request.method == 'POST':
        savedForm = InvoiceForm(request.POST, user=request.user)
        if savedForm.is_valid():
            old = BTGReport.objects.filter(
                project=savedForm.cleaned_data['project'],
                btgYear=savedForm.cleaned_data['year'],
                btgMonth=savedForm.cleaned_data['month']
            ).values('id')
            if old:
                balancetogo = BTGReport.objects.get(id=old[0]['id'])
                balancetogo.currMonthIN = savedForm.cleaned_data[
                    'currMonthIN'
                ]
                balancetogo.member = request.user
                balancetogo.save()
            else:
                balancetogo = BTGReport()
                balancetogo.project = savedForm.cleaned_data['project']
                balancetogo.member = request.user
                balancetogo.currMonthIN = savedForm.cleaned_data['currMonthIN']
                balancetogo.btgYear = savedForm.cleaned_data['year']
                balancetogo.btgMonth = savedForm.cleaned_data['month']
                balancetogo.save()
    return render(request, 'MyANSRSource/reportinvoice.html',
                  {'form': form, 'data': data})


@login_required
@permission_required('MyANSRSource.create_project')
def SingleTeamMemberReport(request):
    report = {}
    projectH, nonProjectH = [], []
    member, startDate, endDate = '', '', ''
    form = TeamMemberPerfomanceReportForm()
    grdTotal = ''
    fresh = 1
    plannedHours = 0
    if request.method == 'POST':
        reportData = TeamMemberPerfomanceReportForm(request.POST)
        if reportData.is_valid():
            start = reportData.cleaned_data['startDate'].weekday()
            end = 6 - reportData.cleaned_data['endDate'].weekday()
            wkstartDate = reportData.cleaned_data['startDate'] - timedelta(
                days=start)
            wkendDate = reportData.cleaned_data['endDate'] + timedelta(
                days=end)
            tm = ProjectTeamMember.objects.filter(
                member=reportData.cleaned_data['member'],
                startDate__gte=reportData.cleaned_data['startDate'],
                endDate__lte=reportData.cleaned_data['endDate'],
            ).values('plannedEffort')
            plannedHours = sum([eachRec['plannedEffort'] for eachRec in tm])
            report = TimeSheetEntry.objects.filter(
                teamMember=reportData.cleaned_data['member'],
                wkstart__gte=wkstartDate,
                wkend__lte=wkendDate,
            ).values(
                'teamMember__username',
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
                       ).order_by('project__projectId',
                                  'project__name', 'hold')
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
                    eachData['medianProd'] = numpy.median(units)
                    if eachData['chapter__name'] == ' -  ':
                        eachData['totalValue'] = ' -  '
                        eachData['minProd'] = ' -  '
                        eachData['maxProd'] = ' -  '
                        eachData['avgProd'] = ' -  '
                        eachData['medianProd'] = ' -  '
                nonProjectTotal = sum([
                    eachData['totalHours'] for eachData in report if eachData['chapter__name'] == ' -  '
                ])
                projectTotal = sum([
                    eachData['totalHours'] for eachData in report if eachData['chapter__name'] != ' -  '
                ])
                grdTotal = {'nTotal': nonProjectTotal,
                            'pTotal': projectTotal}
                fresh = 2
                if 'generate' in request.POST:
                    sheetName = ['TeamMember Perfomance']
                    fileName = '{0}_{1}_{2}.xlsx'.format(
                        reportData.cleaned_data['member'],
                        reportData.cleaned_data['startDate'],
                        reportData.cleaned_data['endDate']
                    )
                    heading = ['Project Code', 'Project Name', 'Book',
                               'Chapter', 'Task / Activity', 'Total Hours',
                               'Total Productivity', 'Avg. Productivity',
                               'Min. Productivity', 'Max. Productivity',
                               'Median Productivity', 'Norm', 'Status']
                    return generateExcel(request, report, sheetName,
                                         heading, grdTotal, fileName)
            else:
                fresh = 0
            startDate = reportData.cleaned_data['startDate']
            endDate = reportData.cleaned_data['endDate']
            member = reportData.cleaned_data['member']
            form = TeamMemberPerfomanceReportForm(initial={
                'startDate': reportData.cleaned_data['startDate'],
                'endDate': reportData.cleaned_data['endDate'],
                'member': reportData.cleaned_data['member']
            })
            for eachRec in report:
                if eachRec['project__name'] != ' - ':
                    projectH.append(eachRec)
                else:
                    nonProjectH.append(eachRec)
        else:
            logger.error(reportData.errors)
            fresh = 1
    return render(request,
                  'MyANSRSource/reportsinglemember.html',
                  {'form': form, 'data': report, 'fresh': fresh,
                   'project': projectH, 'nonProject': nonProjectH,
                   'grandTotal': grdTotal, 'startDate': startDate,
                   'endDate': endDate, 'member': member,
                   'pH': plannedHours})


@login_required
@permission_required('MyANSRSource.create_project')
def SingleProjectReport(request):
    basicData = {}
    crData, tsData, msData, taskData, topPerformer = [], [], [], [], []
    pEffort = 0
    fresh = 1
    actualTotal, plannedTotal, balanceTotal, deviation = 0, 0, 0, 0
    red, closed = False, False
    form = ProjectPerfomanceReportForm(user=request.user)
    if request.method == 'POST':
        fresh = 0
        reportData = ProjectPerfomanceReportForm(request.POST,
                                                 user=request.user)
        if reportData.is_valid():
            cProject = reportData.cleaned_data['project']
            if cProject.closed:
                closed = cProject.closed
            basicData = {
                'code': cProject.projectId,
                'name': cProject.name,
                'startDate': cProject.startDate,
                'endDate': cProject.endDate,
                'plannedEffort': cProject.plannedEffort,
                'totalValue': cProject.totalValue,
                'salesForceNumber': cProject.salesForceNumber,
                'signed': cProject.signed,
                'po': cProject.po
            }
            crData = ProjectChangeInfo.objects.filter(
                project=cProject
            ).values('crId', 'reason', 'endDate', 'revisedEffort',
                     'revisedTotal', 'closed', 'closedOn').order_by('endDate')
            if basicData['endDate'] < datetime.now().date() \
                    and cProject.closed is False:
                red = True
            msData = ProjectMilestone.objects.filter(
                project=cProject
            ).values('description', 'financial', 'milestoneDate',
                     'amount', 'closed').order_by('milestoneDate')
            taskData = TimeSheetEntry.objects.filter(
                project=cProject
            ).values(
                'task__name'
            ).annotate(monday=Sum('mondayQ'),
                       tuesday=Sum('tuesdayQ'),
                       wednesday=Sum('wednesdayQ'),
                       thursday=Sum('thursdayQ'),
                       friday=Sum('fridayQ'),
                       saturday=Sum('saturdayQ'),
                       sunday=Sum('sundayQ')
                       ).order_by('task__name')
            taskNames = TimeSheetEntry.objects.filter(
                project=cProject
            ).values('task__name',
                     'task__norm').order_by('task__name').distinct()
            for eachTaskName in taskNames:
                d = {}
                memberData = TimeSheetEntry.objects.filter(
                    task__name=eachTaskName['task__name']
                ).values(
                    'teamMember__first_name',
                    'teamMember__last_name',
                    'teamMember__id'
                ).annotate(monday=Sum('mondayQ'),
                           tuesday=Sum('tuesdayQ'),
                           wednesday=Sum('wednesdayQ'),
                           thursday=Sum('thursdayQ'),
                           friday=Sum('fridayQ'),
                           saturday=Sum('saturdayQ'),
                           sunday=Sum('sundayQ')
                           ).order_by('teamMember__first_name',
                                      'teamMember__last_name',
                                      'teamMember__id')
                d['taskName'] = eachTaskName['task__name']
                d['norm'] = eachTaskName['task__norm']
                if len(memberData):
                    for eachRec in memberData:
                        eachRec['total'] = 0
                        for eachDay in days:
                            eachRec['total'] += eachRec[eachDay]
                    totals = [eachRec['total'] for eachRec in memberData]
                    max_member = totals.index(max(totals))
                    d['top'] = "{0} {1} ({2})".format(
                        memberData[max_member]['teamMember__first_name'],
                        memberData[max_member]['teamMember__last_name'],
                        memberData[max_member]['teamMember__id']
                    )
                topPerformer.append(d)
            for eachData in taskData:
                units = []
                for k, v in eachData.iteritems():
                    if k != 'task__name':
                        units.append(v)
                eachData['min'] = min(units)
                eachData['max'] = max(units)
                eachData['avg'] = round(sum(units) / len(units), 2)
                eachData['median'] = numpy.median(units)
            tsData = TimeSheetEntry.objects.filter(
                project=cProject
            ).values(
                'teamMember',
                'teamMember__first_name',
                'teamMember__last_name'
            ).annotate(mondayh=Sum('mondayH'),
                       tuesdayh=Sum('tuesdayH'),
                       wednesdayh=Sum('wednesdayH'),
                       thursdayh=Sum('thursdayH'),
                       fridayh=Sum('fridayH'),
                       saturdayh=Sum('saturdayH'),
                       sundayh=Sum('sundayH')
                       ).order_by('teamMember__first_name',
                                  'teamMember__last_name')
            if len(basicData):
                if basicData['signed']:
                    basicData['signed'] = 'Yes'
                else:
                    basicData['signed'] = 'No'
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
                    eachTsData['balance'] = eachTsData['planned'] - eachTsData['actual']
                    try:
                        eachTsData[
                            'deviation'] = round((
                                eachTsData['actual'] - eachTsData['planned']) * 100 / eachTsData['planned'])
                    except ZeroDivisionError:
                        eachTsData['deviation'] = 0
                    except:
                        eachTsData['deviation'] = 0
                try:
                    actualTotal = sum(
                        [eachTsData['actual'] for eachTsData in tsData])
                except ZeroDivisionError:
                    actualTotal = 0
                try:
                    balanceTotal = sum(
                        [eachTsData['balance'] for eachTsData in tsData])
                except ZeroDivisionError:
                    balanceTotal = 0
                try:
                    plannedTotal = sum(
                        [eachTsData['planned'] for eachTsData in tsData])
                except ZeroDivisionError:
                    plannedTotal = 0
                try:
                    deviation = round((
                        (actualTotal - plannedTotal) * 100
                    ) / plannedTotal)
                except ZeroDivisionError:
                    deviation = 0
            form = ProjectPerfomanceReportForm(
                user=request.user,
                initial={'project': cProject}
            )
            if 'generate' in request.POST:
                fileName = '{0}_{1}.xlsx'.format(
                    datetime.now().date(),
                    datetime.now().time()
                )
                fileName = fileName.replace("  ", "_")
                report = [basicData, crData, msData, tsData, taskData]
                sheetName = ['Basic Information',
                             'Change Requests',
                             'Milestones',
                             'TM Perfomance',
                             'Productivity']
                heading = [
                    ['Project Name', 'Start Date', 'End Date', 'Planned Effort',
                     'Total Value', 'salesForceNumber', 'Signed', 'P.O.'],
                    ['CR#', 'Reason', 'End Date', 'Revised Effort',
                     'Revised Total'],
                    ['Milestone Name', 'Milestone Date', 'Financial', 'Value',
                     'Completed'],
                    ['Member Name', 'Designation', 'Planned Effort',
                     'Actual Effort', 'Deviation(%)'],
                    ['Task Name', 'Norm', 'Actual']
                ]
                grdTotal = [plannedTotal, actualTotal, deviation]
                return generateExcel(request, report, sheetName,
                                     heading, grdTotal, fileName)
    return render(request,
                  'MyANSRSource/reportsingleproject.html',
                  {'form': form, 'basicData': basicData, 'fresh': fresh,
                   'crData': crData, 'tsData': tsData, 'msData': msData,
                   'topPerformer': topPerformer, 'taskData': taskData,
                   'actualTotal': actualTotal, 'plannedTotal': plannedTotal,
                   'deviation': deviation, 'balanceTotal': balanceTotal,
                   'red': red, 'closed': closed}
                  )


@login_required
@permission_required('MyANSRSource.create_project')
def TeamMemberPerfomanceReport(request):
    report, final_report, totals = {}, {}, {}
    buName, currReportMonth, reportYear = '', '', ''
    form = UtilizationReportForm(user=request.user)
    if request.method == 'POST':
        reportData = UtilizationReportForm(request.POST,
                                           user=request.user)
        if reportData.is_valid():
            reportMonth = reportData.cleaned_data['month']
            currReportMonth = datetime(1900, int(reportMonth), 1).strftime('%B')
            reportYear = reportData.cleaned_data['year']
            bu = reportData.cleaned_data['bu']
            if bu == '0':
                reportbu = BusinessUnit.objects.all().values_list('id')
                buName = 'All'
            else:
                reportbu = BusinessUnit.objects.filter(id=bu).values_list('id')
                for eachData in BusinessUnit.objects.filter(id=bu).values('name'):
                    buName = eachData['name']
            tsData = TimeSheetEntry.objects.filter(
                wkstart__year=reportYear,
                wkstart__month=reportMonth,
                project__bu__id__in=reportbu,
            ).values(
                'project__customer__name', 'project__projectId',
                'project__name', 'project__projectType__description',
                'project__bu__name', 'teamMember__first_name',
                'teamMember__last_name', 'teamMember__id'
            ).order_by('teamMember__first_name',
                       'teamMember__last_name').distinct()
            if tsData:
                data = GenerateReport(request, reportMonth, reportYear,
                                      tsData, idle=None)
                if data:
                    for eachRec in data:
                        correctPTM = 0
                        for v in eachRec['PTMBilledHours'].values():
                            correctPTM += v
                        eachRec['correctPTM'] = correctPTM
                    report = calcTotal(request, data)
            else:
                data = {}
                report = {}
            for eachRec in report:
                eachRec['PTD'] = eachRec['correctPTM'] + eachRec['others'][0]['otherstotal']
            totals['sumTotalPlanned'] = sum([eachRec['totalPlanned'] for eachRec in report])
            totals['monthRecTotal'] = sum([eachRec['monthRec'] for eachRec in report])
            totals['PTMTotal'] = sum([eachRec['correctPTM'] for eachRec in report])
            totals['sumOthersTotal'] = sum([eachRec['others'][0]['otherstotal'] for eachRec in report])
            totals['PTDTotal'] = sum([eachRec['PTD'] for eachRec in report])
            form = UtilizationReportForm(initial={
                'month': reportData.cleaned_data['month'],
                'year': reportData.cleaned_data['year'],
                'bu': reportData.cleaned_data['bu']
            }, user=request.user)
    return render(request,
                  'MyANSRSource/reportmembersummary.html',
                  {'form': form, 'data': report, 'bu': buName,
                   'month': currReportMonth, 'year': reportYear,
                   'totals': totals})


@login_required
@permission_required('MyANSRSource.create_project')
def ProjectPerfomanceReport(request):
    data = {}
    fresh = 1
    iidleTotal, iothersTotal, eidleTotal, eothersTotal = 0, 0, 0, 0
    form = UtilizationReportForm(user=request.user)
    buName, currReportMonth, reportYear = 0, 0, 0
    if request.method == 'POST':
        reportData = UtilizationReportForm(request.POST,
                                           user=request.user)
        if reportData.is_valid():
            reportMonth = reportData.cleaned_data['month']
            currReportMonth = datetime(1900, int(reportMonth), 1).strftime('%B')
            reportYear = reportData.cleaned_data['year']
            bu = reportData.cleaned_data['bu']
            if bu == '0':
                reportbu = BusinessUnit.objects.all().values_list('id')
                buName = 'All'
            else:
                reportbu = BusinessUnit.objects.filter(id=bu).values_list('id')
                for eachData in BusinessUnit.objects.filter(id=bu).values('name'):
                    buName = eachData['name']
            tsData = TimeSheetEntry.objects.filter(
                wkstart__year=reportYear,
                wkstart__month=reportMonth,
                project__internal=True,
                project__bu__id__in=reportbu,
                project__projectId__isnull=False
            ).values(
                'project__customer__name', 'project__projectId',
                'project__name', 'project__projectType__description',
                'project__bu__name', 'project__startDate',
                'project__endDate', 'project__totalValue',
                'project__plannedEffort'
            ).order_by('project__projectId',
                       'project__name').distinct()
            if tsData:
                internalIdle = GenerateReport(request, reportMonth, reportYear,
                                              tsData, idle=True)
                internalOthers = GenerateReport(request, reportMonth,
                                                reportYear, internalIdle,
                                                idle=False)
            else:
                internalOthers = {}
            tsData = TimeSheetEntry.objects.filter(
                wkstart__year=reportYear,
                wkstart__month=reportMonth,
                project__internal=False,
                project__bu=reportbu,
                project__projectId__isnull=False
            ).values(
                'project__customer__name', 'project__projectId',
                'project__name', 'project__projectType__description',
                'project__bu__name', 'project__startDate',
                'project__endDate', 'project__totalValue',
                'project__plannedEffort'
            ).order_by('project__projectId',
                       'project__name').distinct()
            if tsData:
                externalIdle = GenerateReport(request, reportMonth, reportYear,
                                              tsData, idle=True)
                externalOthers = GenerateReport(request, reportMonth,
                                                reportYear, externalIdle,
                                                idle=False)
            else:
                externalOthers = {}
            data = {'internal': calcTotal(request, internalOthers),
                    'external': calcTotal(request, externalOthers),
                    }
            if len(data['internal']):
                for eachD in data['internal']:
                    for eachRec in eachD['idle']:
                        if 'idletotal' in eachRec:
                            iidleTotal += eachRec['idletotal']
                    for eachRec in eachD['others']:
                        if 'otherstotal' in eachRec:
                            iothersTotal += eachRec['otherstotal']
            if len(data['external']):
                for eachD in data['external']:
                    for eachRec in eachD['idle']:
                        if 'idletotal' in eachRec:
                            eidleTotal += eachRec['idletotal']
                    for eachRec in eachD['others']:
                        if 'otherstotal' in eachRec:
                            eothersTotal += eachRec['otherstotal']
            fresh = 0
            form = UtilizationReportForm(initial={
                'month': reportData.cleaned_data['month'],
                'year': reportData.cleaned_data['year'],
                'bu': reportData.cleaned_data['bu']
            }, user=request.user)
    return render(request,
                  'MyANSRSource/reportprojectsummary.html',
                  {'form': form, 'data': data, 'fresh': fresh, 'bu': buName,
                   'iiTotal': iidleTotal, 'ioTotal': iothersTotal,
                   'eiTotal': eidleTotal, 'eoTotal': eothersTotal,
                   'month': currReportMonth, 'year': reportYear})


@login_required
@permission_required('MyANSRSource.create_project')
def RevenueRecognitionReport(request):
    btg = BTGReportForm()
    data = RR(request, datetime.now().month, datetime.now().year)
    if request.method == 'POST':
        reportData = BTGReportForm(request.POST)
        if reportData.is_valid():
            reportMonth = reportData.cleaned_data['month']
            reportYear = reportData.cleaned_data['year']
            data = RR(request, reportMonth, reportYear)
    return render(request, 'MyANSRSource/reportrevenue.html',
                  {'data': data,
                   'form': btg})


@login_required
@permission_required('MyANSRSource.create_project')
def RR(request, month, year):
    data = BTGReport.objects.filter(
        btgMonth=month,
        btgYear=year
    ).values(
        'project__projectId', 'project__name', 'project__totalValue',
        'project__plannedEffort', 'project__startDate', 'project__endDate'
    )
    if len(data):
        for eachMem in data:
            mem = ProjectManager.objects.filter(
                project__projectId=eachMem['project__projectId']
            ).values('user__username')
            eachMem['tl'] = mem
            eachMem['effort'] = getRREffort(
                request, month, year,
                eachMem['project__projectId']
            )
            eachMem['prevEffort'] = getRREffort(
                request, int(month)-1, year,
                eachMem['project__projectId']
            )
            if eachMem['effort'] and eachMem['prevEffort']:
                eachMem['PTDEffort'] = eachMem['effort'][0]['total'] + \
                    eachMem['prevEffort'][0]['total']
            else:
                eachMem['effort'] = 0
                eachMem['prevEffort'] = 0
                eachMem['PTDEffort'] = 0
            eachMem['plannedBTG'] = eachMem[
                'project__plannedEffort'] - eachMem['PTDEffort']
            eachMem['BTG'] = eachMem[
                'project__plannedEffort'] - eachMem['PTDEffort']
            eachMem['currentData'] = getEntryData(request, month, year,
                                                  eachMem[
                                                      'project__plannedEffort'],
                                                  size=1)
            eachMem['prevData'] = getEntryData(request, int(month) - 1,
                                               year, eachMem[
                                                   'project__plannedEffort'],
                                               size=2)
            if eachMem['currentData']:
                eachMem['projectedTE'] = eachMem['currentData'][0]['btg']
                eachMem['invoiceCurr'] = eachMem['currentData'][0]['currMonthIN']
            else:
                eachMem['projectedTE'] = 0
                eachMem['invoiceCurr'] = 0
            try:
                eachMem['RRCurrentMonth'] = (eachMem['PTDEffort'] / eachMem['projectedTE']) * eachMem['project__totalValue']
            except ZeroDivisionError:
                eachMem['RRCurrentMonth'] = 0
            if eachMem['currentData']:
                eachMem['invoiceLast'] = eachMem['prevData'][0]['currMonthIN']
            else:
                eachMem['invoiceLast'] = 0
            eachMem['invoicePTD'] = eachMem['invoiceLast'] + eachMem['invoiceCurr']
            eachMem['invoicePTD'] = eachMem['invoiceLast'] + eachMem['invoiceCurr']
            eachMem['currAcruval'] = eachMem['RRCurrentMonth'] - eachMem['invoiceCurr']
            eachMem['ptdAcruval'] = eachMem['RRCurrentMonth'] - eachMem['invoiceCurr']
            eachMem['currAcruval'] = eachMem['invoicePTD']
            if eachMem['PTDEffort'] - eachMem['project__plannedEffort']:
                eachMem['status'] = 'Overrun'
            else:
                eachMem['status'] = 'Underrun'
    else:
        data = {}
    return data


@login_required
@permission_required('MyANSRSource.create_project')
def getEntryData(request, cmonth, cyear, projectId, size):
    if size == 1:
        return BTGReport.objects.filter(
            btgMonth=cmonth,
            btgYear=cyear,
            project__projectId=projectId
        ).values('currMonthIN')
    else:
        return BTGReport.objects.filter(
            btgMonth=cmonth,
            btgYear=cyear,
            project__projectId=projectId
        ).values('currMonthIN', 'btg')


@login_required
@permission_required('MyANSRSource.create_project')
def getRREffort(request, month, year, projectId):
    ts = TimeSheetEntry.objects.filter(
        wkstart__year=year,
        wkstart__month=month,
        project__projectId=projectId
    ).values(
        'project__projectId'
    ).annotate(
        monday=Sum('mondayH'),
        tuesday=Sum('tuesdayH'),
        wednesday=Sum('wednesdayH'),
        thursday=Sum('thursdayH'),
        friday=Sum('fridayH'),
        saturday=Sum('saturdayH'),
        sunday=Sum('sundayH'),
    )
    if ts:
        for eachTsData in ts:
            eachTsData['total'] = eachTsData['monday'] + \
                eachTsData['tuesday'] + \
                eachTsData['wednesday'] + \
                eachTsData['thursday'] + \
                eachTsData['friday'] + \
                eachTsData['saturday'] + eachTsData['sunday']
    return ts


@login_required
def calcPTM(request, tsData):
    for eachData in tsData:
        data = TimeSheetEntry.objects.filter(
            project__bu=request.POST.get('bu'),
            project__projectId=eachData['project__projectId']
        ).values(
            'project__projectId'
        ).annotate(
            monday=Sum('mondayH'),
            tuesday=Sum('tuesdayH'),
            wednesday=Sum('wednesdayH'),
            thursday=Sum('thursdayH'),
            friday=Sum('fridayH'),
            saturday=Sum('saturdayH'),
            sunday=Sum('sundayH'),
        )
        if data:
            for eachTsData in data:
                eachTsData['PTM'] = eachTsData['monday'] + \
                    eachTsData['tuesday'] + \
                    eachTsData['wednesday'] + \
                    eachTsData['thursday'] + \
                    eachTsData['friday'] + \
                    eachTsData['saturday'] + \
                    eachTsData['sunday']
                diff = eachTsData['PTM'] - eachData['others'][0]['otherstotal']
                if diff:
                    eachData['correctPTM'] = diff
                else:
                    eachData['correctPTM'] = 0
        else:
            eachData['correctPTM'] = 0
    return tsData


@login_required
def GenerateReport(request, reportMonth, reportYear, tsData, idle):
    for eachData in tsData:
        eachData['lead'] = ProjectManager.objects.filter(
            project__projectId=eachData['project__projectId']
        ).values('user__username')
        ts = TimeSheetEntry.objects.filter(
            wkstart__year=reportYear,
            wkstart__month=reportMonth,
            project__projectId=eachData['project__projectId'])
        if idle:
            eachData['idle'] = ts.filter(
                task__name='Idle'
            ).values(
                'project__projectId'
            ).annotate(
                monday=Sum('mondayH'),
                tuesday=Sum('tuesdayH'),
                wednesday=Sum('wednesdayH'),
                thursday=Sum('thursdayH'),
                friday=Sum('fridayH'),
                saturday=Sum('saturdayH'),
                sunday=Sum('sundayH'),
            ).order_by('teamMember__id')
        elif idle is False:
            eachData['others'] = ts.exclude(
                task__name='Idle'
            ).values(
                'project__projectId'
            ).annotate(
                monday=Sum('mondayH'),
                tuesday=Sum('tuesdayH'),
                wednesday=Sum('wednesdayH'),
                thursday=Sum('thursdayH'),
                friday=Sum('fridayH'),
                saturday=Sum('saturdayH'),
                sunday=Sum('sundayH'),
            )
        else:
            ts = TimeSheetEntry.objects.filter(
                wkstart__year=reportYear,
                wkstart__month=reportMonth,
                project__projectId=eachData['project__projectId'],
                teamMember__id=eachData['teamMember__id'])
            totalts = TimeSheetEntry.objects.filter(
                project__projectId=eachData['project__projectId'],
                teamMember__id=eachData['teamMember__id'])
            cUser = User.objects.filter(id=eachData['teamMember__id'])
            empId = Employee.objects.filter(user=cUser).values(
                'employee_assigned_id')
            if len(empId):
                eachData['empId'] = Employee.objects.filter(
                    user=cUser).values(
                        'employee_assigned_id')[0]['employee_assigned_id']
            else:
                eachData['empId'] = 000
            dates = ProjectTeamMember.objects.filter(
                project__projectId=eachData['project__projectId'],
                member=cUser
            ).values('startDate', 'endDate', 'plannedEffort')
            if len(dates):
                eachData['startDate'] = dates[0]['startDate']
                eachData['endDate'] = dates[0]['endDate']
                if eachData['startDate'] and eachData['endDate']:
                    diff = (eachData['endDate'] - eachData['startDate']).days
                    eachData['totalPlanned'] = dates[0]['plannedEffort']
                    eachData['monthRec'] = 0
                    if diff > 0:
                        rd = rdelta.relativedelta(
                            eachData['endDate'],
                            eachData['startDate']
                        )
                        if rd.months > 0:
                            if eachData['totalPlanned'] > 0:
                                eachData['monthRec'] = eachData['totalPlanned'] / rd.months
            else:
                eachData['totalPlanned'] = 0
                eachData['monthRec'] = 0
            eachData['others'] = ts.values(
                'project__projectId'
            ).annotate(
                monday=Sum('mondayH'),
                tuesday=Sum('tuesdayH'),
                wednesday=Sum('wednesdayH'),
                thursday=Sum('thursdayH'),
                friday=Sum('fridayH'),
                saturday=Sum('saturdayH'),
                sunday=Sum('sundayH')
            )
            totalTsValue = totalts.values(
                'project__projectId'
            ).annotate(
                monday=Sum('mondayH'),
                tuesday=Sum('tuesdayH'),
                wednesday=Sum('wednesdayH'),
                thursday=Sum('thursdayH'),
                friday=Sum('fridayH'),
                saturday=Sum('saturdayH'),
                sunday=Sum('sundayH')
            )
            d = {}
            for eachDay in days:
                d[eachDay] = totalTsValue[0][eachDay] - eachData['others'][0][eachDay]
            eachData['PTMBilledHours'] = d
    return tsData


@login_required
def calcTotal(request, data):
    if len(data):
        for eachRec in data:
            if 'idle' in eachRec:
                if len(eachRec['idle']):
                    for eachTsData in eachRec['idle']:
                        eachTsData['idletotal'] = eachTsData['monday'] + \
                            eachTsData['tuesday'] + \
                            eachTsData['wednesday'] + \
                            eachTsData['thursday'] + \
                            eachTsData['friday'] + \
                            eachTsData['saturday'] + \
                            eachTsData['sunday']
            if 'others' in eachRec:
                if len(eachRec['others']):
                    for eachTsData in eachRec['others']:
                        eachTsData['otherstotal'] = eachTsData['monday'] + \
                            eachTsData['tuesday'] + \
                            eachTsData['wednesday'] + \
                            eachTsData['thursday'] + \
                            eachTsData['friday'] + \
                            eachTsData['saturday'] + \
                            eachTsData['sunday']
        return data
    else:
        return {}


@login_required
def generateExcel(request, report, sheetName, heading, grdTotal, fileName):
    if len(report):
        workbook = xlsxwriter.Workbook(fileName, {'constant_memory': True})
        common = {'font_name': 'Droid Sans', 'font_size': 11,
                  'align': 'center', 'valign': 'vcenter'}
        headerFormat = common.copy()
        headerFormat['bold'] = True
        header = workbook.add_format(headerFormat)
        content = workbook.add_format(common)
        dateFormat = common.copy()
        dateFormat['num_format'] = 'mmmm dd, yyyy'
        dateformat = workbook.add_format(dateFormat)
        reportDateFormat = headerFormat.copy()
        reportDateFormat.update(dateFormat)
        reportDateformat = workbook.add_format(reportDateFormat)
        alp = list(string.ascii_uppercase)
        if len(sheetName) == 1:
            worksheet = workbook.add_worksheet(sheetName[0])
            generateSheetHeader(request, heading, header, alp, worksheet)
            generateMemberContent(request, header, report, worksheet, content,
                                  alp, grdTotal)
        else:
            counter = 0
            for eachName in sheetName:
                eachName = workbook.add_worksheet(eachName)
                if sheetName[0] == 'Basic Information':
                    generateSheetHeader(request, heading[counter], header,
                                        alp, eachName)
                    generateProjectContent(request, header, report[counter],
                                           eachName, content, alp, grdTotal,
                                           dateformat, reportDateformat)
                elif sheetName[0] == '':
                    generateSheetHeader(request, heading[counter], header,
                                        alp, eachName)
                    generateProjectPerfContent(request, header, report[counter],
                                               eachName, content, alp, grdTotal,
                                               dateformat, reportDateformat)
                counter += 1
        workbook.close()
        return generateDownload(request, fileName)
    else:
        return {}


@login_required
def generateSheetHeader(request, heading, header, alp, worksheet):
    counter = 0
    cellNumber = ['{0}1'.format(
        eachId) for eachId in alp[:len(heading)]]
    for eachRec in cellNumber:
        worksheet.write(eachRec, heading[counter], header)
        counter += 1
    worksheet.autofilter('{0}:{1}'.format(cellNumber[0],
                                          cellNumber[-1]))


@login_required
def generateMemberContent(request, header, report, worksheet,
                          content, alp, grdTotal):
    row = 1
    for eachRec in report:
        worksheet.write(row, 0, eachRec['project__projectId'], content)
        worksheet.write(row, 1, eachRec['project__name'], content)
        worksheet.write(row, 2, eachRec['project__book__name'], content)
        worksheet.write(row, 3, eachRec['chapter__name'], content)
        if eachRec['activity__name'] != '':
            worksheet.write(row, 4, eachRec['activity__name'], content)
        else:
            worksheet.write(row, 4, eachRec['task__name'], content)
        worksheet.write(row, 5, eachRec['totalHours'], content)
        worksheet.write(row, 6, eachRec['totalValue'], content)
        worksheet.write(row, 7, eachRec['avgProd'], content)
        worksheet.write(row, 8, eachRec['minProd'], content)
        worksheet.write(row, 9, eachRec['maxProd'], content)
        worksheet.write(row, 10, eachRec['medianProd'], content)
        if eachRec['hold']:
            worksheet.write(row, 12, 'Not Submitted', content)
        else:
            worksheet.write(row, 12, 'Submitted', content)
        row += 1
    msg0 = "Total Non-Project Hours(s) : {0}".format(grdTotal['nTotal'])
    msg1 = "Total Project Hours(s) : {0}".format(grdTotal['pTotal'])
    msg = msg0 + '  ' + msg1
    generateReportFooter(request, worksheet, alp[12], row+1,
                         header, msg)


@login_required
def generateProjectContent(request, header, report, worksheet,
                           content, alp, grdTotal, dateformat,
                           reportDateformat):
    if 'totalValue' in report:
        row = 1
        worksheet.write(row, 0, report['name'], content)
        worksheet.write(row, 1, report['startDate'], dateformat)
        worksheet.write(row, 2, report['endDate'], dateformat)
        worksheet.write(row, 3, report['plannedEffort'], content)
        worksheet.write(row, 4, report['totalValue'], content)
        worksheet.write(row, 5, report['salesForceNumber'], content)
        worksheet.write(row, 6, report['signed'], content)
        worksheet.write(row, 7, report['po'], content)
    else:
        row, msg = 1, ''
        for eachRec in report:
            if 'crId' in eachRec:
                worksheet.write(row, 0, eachRec['crId'], content)
                worksheet.write(row, 1, eachRec['reason'], content)
                worksheet.write(row, 2, eachRec['endDate'], dateformat)
                worksheet.write(row, 3, eachRec['revisedEffort'], content)
                worksheet.write(row, 4, eachRec['revisedTotal'], content)
                if eachRec['closed']:
                    msg = "Project Closed On : {0}".format(
                        eachRec['closedOn']
                    )
                    generateReportFooter(request, worksheet, alp[7], row+1,
                                         reportDateformat, msg)
            if 'financial' in eachRec:
                worksheet.write(row, 0, eachRec['description'], content)
                worksheet.write(row, 1, eachRec['milestoneDate'], dateformat)
                worksheet.write(row, 2, eachRec['financial'], content)
                worksheet.write(row, 3, eachRec['amount'], content)
                worksheet.write(row, 4, eachRec['closed'], content)
            row += 1

            if 'task__name' in eachRec:
                worksheet.write(row, 0, eachRec['task__name'], content)
                #worksheet.write(row, 1, eachRec['norm'], content)
            row += 1

        row, msg = 1, ''
        for eachRec in report:
            if 'deviation' in eachRec:
                worksheet.write(row, 0, eachRec['teamMember'], content)
                worksheet.write(row, 1, eachRec['designation'], content)
                worksheet.write(row, 2, eachRec['planned'], content)
                worksheet.write(row, 3, eachRec['actual'], content)
                worksheet.write(row, 4, eachRec['deviation'], content)
                msg0 = 'Total Planned Effort : {0} '.format(grdTotal[0])
                msg1 = 'Total Actual Effort : {0} '.format(grdTotal[1])
                msg2 = 'Deivation(%) : {0} '.format(grdTotal[2])
                msg = msg0 + '  ' + msg1 + '  ' + msg2
            row += 1
        generateReportFooter(request, worksheet, alp[4], row+1, header, msg)


@login_required
def generateReportFooter(request, worksheet, alpValue, rowValue, cFormat, msg):
    cellRange = 'A{1}:{0}{1}'.format(alpValue, rowValue)
    worksheet.merge_range(cellRange, '', cFormat)
    totalCell = 'A{0}'.format(rowValue)
    worksheet.write(totalCell, msg, cFormat)


@login_required
def generateProjectPerfContent(request, header, report, worksheet,
                               content, alp, grdTotal):
    row = 1
    for eachRec in report:
        worksheet.write(row, 0, eachRec['project__projectId'], content)
        worksheet.write(row, 1, eachRec['project__name'], content)
        worksheet.write(row, 2, eachRec['project__book__name'], content)
        worksheet.write(row, 3, eachRec['chapter__name'], content)
        if eachRec['activity__name'] != '':
            worksheet.write(row, 4, eachRec['activity__name'], content)
        else:
            worksheet.write(row, 4, eachRec['task__name'], content)
        worksheet.write(row, 5, eachRec['totalHours'], content)
        worksheet.write(row, 6, eachRec['totalValue'], content)
        worksheet.write(row, 7, eachRec['avgProd'], content)
        worksheet.write(row, 8, eachRec['minProd'], content)
        worksheet.write(row, 9, eachRec['maxProd'], content)
        worksheet.write(row, 10, eachRec['medianProd'], content)
        worksheet.write(row, 11, eachRec['project__maxProductivityUnits'],
                        content)
        if eachRec['hold']:
            worksheet.write(row, 12, 'Not Submitted', content)
        else:
            worksheet.write(row, 12, 'Submitted', content)
        row += 1
    cellRange = 'A{1}:{0}{1}'.format(alp[12], row+1)
    worksheet.merge_range(cellRange, '', header)
    totalCell = 'A{0}'.format(row+1)
    total = "Total Hour(s) : {0}".format(grdTotal)
    worksheet.write(totalCell, total, header)


@login_required
def generateDownload(request, fileName):
    wrapper = FileWrapper(open(fileName, 'r'))
    content_type = mimetypes.guess_type(fileName)[0]
    response = HttpResponse(wrapper, content_type=content_type)
    response['Content-Length'] = os.path.getsize(fileName)
    response['Content-Disposition'] = 'attachment; filename="{0}"'.format(
        fileName
    )
    os.system('rm {0}'.format(fileName))
    return response
