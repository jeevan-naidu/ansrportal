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
from datetime import timedelta, datetime, date
from django.db.models import Sum, Avg, Min, Max
from employee.models import Employee
from django.core.servers.basehttp import FileWrapper
from dateutil import relativedelta as rdelta
from django.db.models import Q
from django.http import HttpResponse
from calendar import monthrange
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
    report, newReport, minProd, maxProd, avgProd = {}, {}, {}, {}, {}
    projectH, nonProjectH = [], []
    member, startDate, endDate = '', '', ''
    form = TeamMemberPerfomanceReportForm()
    grdTotal = ''
    fresh = 1
    plannedHours = 0
    if request.method == 'POST':
        reportData = TeamMemberPerfomanceReportForm(request.POST)
        if reportData.is_valid():
            valuesList = ['teamMember__username',
                          'project__projectId', 'project__name',
                          'project__book__name', 'task__name',
                          'chapter__name', 'activity__name', 'hold']
            orderbyList = ['project__projectId', 'project__name', 'hold']
            startWeekData = getUnwantedValue(
                request,
                reportData.cleaned_data['member'],
                reportData.cleaned_data['startDate'],
                'Start',
                valuesList)
            endWeekData = getUnwantedValue(request,
                                           reportData.cleaned_data['member'],
                                           reportData.cleaned_data['endDate'],
                                           'End', valuesList)
            weekStart = getDate(request,
                                reportData.cleaned_data['startDate'],
                                'Start')
            weekEnd = getDate(request,
                              reportData.cleaned_data['endDate'],
                              'End')
            tm = ProjectTeamMember.objects.filter(
                member=reportData.cleaned_data['member'],
                startDate__gte=weekStart,
                endDate__lte=weekEnd,
            ).values('plannedEffort')
            plannedHours = sum([eachRec['plannedEffort'] for eachRec in tm])

            report = TimeSheetEntry.objects.filter(
                teamMember=reportData.cleaned_data['member'],
                wkstart__gte=weekStart,
                wkend__lte=weekEnd,
            ).values(*valuesList).annotate(
                monday=Sum('mondayH'),
                tuesday=Sum('tuesdayH'),
                wednesday=Sum('wednesdayH'),
                thursday=Sum('thursdayH'),
                friday=Sum('fridayH'),
                saturday=Sum('saturdayH'),
                sunday=Sum('sundayH')
            ).order_by(*orderbyList)
            for eachData in report:
                eachData['total'] = sum([eachData[eachDay] for eachDay in days])
            if len(startWeekData) or len(endWeekData):
                newReport = getMemberExactTsHours(request, startWeekData,
                                                  endWeekData, report)
            else:
                newReport = report
            ts = TimeSheetEntry.objects.filter(
                teamMember=reportData.cleaned_data['member'],
                wkstart__gte=weekStart,
                wkend__lte=weekEnd,
            ).values(*valuesList)
            avgProd = getAvgProd(request, ts, orderbyList)
            minProd = getMinProd(request, ts, orderbyList)
            maxProd = getMaxProd(request, ts, orderbyList)
            if len(newReport):
                for eachData in newReport:
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
                nonProjectTotal = sum(
                    [eachData
                     ['total']
                     for eachData in
                     newReport if eachData['chapter__name'] == ' -  '])
                projectTotal = sum(
                    [eachData
                     ['total']
                     for eachData in
                     newReport if eachData['chapter__name'] != ' -  '])
                grdTotal = {'nTotal': nonProjectTotal, 'pTotal': projectTotal}
                fresh = 2
                if 'generate' in request.POST:
                    sheetName = ['TeamMember Perfomance']
                    fileName = u'{0}_{1}_{2}.xlsx'.format(
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
            for eachRec in newReport:
                if eachRec['project__name'] != ' - ':
                    projectH.append(eachRec)
                else:
                    nonProjectH.append(eachRec)
        else:
            logger.error(reportData.errors)
            fresh = 1
    return render(request,
                  'MyANSRSource/reportsinglemember.html',
                  {'form': form, 'data': newReport, 'fresh': fresh,
                   'minProd': minProd, 'maxProd': maxProd, 'avgProd': avgProd,
                   'project': projectH, 'nonProject': nonProjectH,
                   'grandTotal': grdTotal, 'startDate': startDate,
                   'endDate': endDate, 'member': member,
                   'pH': plannedHours})


@login_required
@permission_required('MyANSRSource.create_project')
def SingleProjectReport(request):
    basicData = {}
    crData, tsData, msData, taskData, topPerformer = [], [], [], [], []
    minTaskData, maxTaskData, avgTaskData = [], [], []
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
                     'revisedTotal', 'closed', 'closedOn',
                     'updatedOn').order_by('updatedOn')
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
            orderbyList = ['task__name']
            ts = TimeSheetEntry.objects.filter(
                project=cProject).values('task__name')
            avgTaskData = getAvgProd(request, ts, orderbyList)
            minTaskData = getMinProd(request, ts, orderbyList)
            maxTaskData = getMaxProd(request, ts, orderbyList)
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
                    cUser = User.objects.get(
                        pk=memberData[max_member]['teamMember__id'])
                    eId = Employee.objects.filter(
                        user=cUser).values('employee_assigned_id')
                    d['top'] = u"{0} {1} ({2})".format(
                        memberData[max_member]['teamMember__first_name'],
                        memberData[max_member]['teamMember__last_name'],
                        eId[0]['employee_assigned_id']
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
                    eachTsData['balance'] = eachTsData[
                        'planned'] - eachTsData['actual']
                    try:
                        eachTsData['deviation'] = round(
                            (eachTsData['actual'] -
                             eachTsData['planned']) *
                            100 /
                            eachTsData['planned'])
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
                fileName = u'{0}_{1}.xlsx'.format(
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
                   'minTaskData': minTaskData, 'maxTaskData': maxTaskData,
                   'avgTaskData': avgTaskData,
                   'topPerformer': topPerformer, 'taskData': taskData,
                   'actualTotal': actualTotal, 'plannedTotal': plannedTotal,
                   'deviation': deviation, 'balanceTotal': balanceTotal,
                   'red': red, 'closed': closed}
                  )


@login_required
@permission_required('MyANSRSource.create_project')
def TeamMemberPerfomanceReport(request):
    # common variable initilization
    users, totals, fresh = {}, {}, 0
    buName, currReportMonth, reportYear = '', '', ''
    valuesList = ['project__customer__name', 'project__projectId',
                  'project__name', 'project__projectType__description',
                  'project__bu__name']
    orderbyList = ['teamMember__first_name', 'teamMember__last_name']
    form = UtilizationReportForm(user=request.user)
    if request.method == 'POST':
        reportData = UtilizationReportForm(request.POST,
                                           user=request.user)
        if reportData.is_valid():
            # Get user input value
            reportMonth = reportData.cleaned_data['month']
            reportYear = reportData.cleaned_data['year']
            bu = reportData.cleaned_data['bu']

            # Change Month Number to Month Name
            currReportMonth = datetime(1900, int(reportMonth), 1).strftime('%B')

            # Creating date range from month and year (User Input)
            lastDay = monthrange(int(reportYear), int(reportMonth))[1]
            startDate = date(int(reportYear), int(reportMonth), 1)
            endDate = date(int(reportYear), int(reportMonth), lastDay)

            # Finding the weekstart and weekend for generated date range
            start = getDate(request, startDate, 'Start')
            end = getDate(request, endDate, 'End')

            # Getting BU object from user input
            if bu == '0':
                reportbu = BusinessUnit.objects.all().values_list('id')
                buName = 'All'
            else:
                reportbu = BusinessUnit.objects.filter(id=bu).values_list('id')
                for eachData in BusinessUnit.objects.filter(id=bu).values('name'):
                    buName = eachData['name']

            # Getting eachUser information in line with selected BU
            users = User.objects.filter(is_active=True,
                                        is_superuser=False).values(
                'id',
                'first_name',
                'last_name'
                ).order_by('first_name', 'last_name')
            if len(users) == 0:
                fresh = 2
            for eachUser in users:
                fresh = 1
                try:
                    emp = Employee.objects.get(user__id=eachUser['id'])
                    eachUser['fullName'] = u"{0} {1}({2})".format(
                        eachUser['first_name'], eachUser['last_name'],
                        emp.employee_assigned_id)
                    eachUser['ts'] = TimeSheetEntry.objects.filter(
                        wkstart__gte=start,
                        wkend__lte=end,
                        project__bu__id__in=reportbu,
                        teamMember__id=eachUser['id']
                    ).values(*valuesList).annotate(
                        monday=Sum('mondayH'),
                        tuesday=Sum('tuesdayH'),
                        wednesday=Sum('wednesdayH'),
                        thursday=Sum('thursdayH'),
                        friday=Sum('fridayH'),
                        saturday=Sum('saturdayH'),
                        sunday=Sum('sundayH'))
                    if len(eachUser['ts']):
                        wkStrtWeek = getDate(request, start, 'Start')
                        wkEndWeek = getDate(request, end, 'Start')
                        for eachTS in eachUser['ts']:
                            eachTS['fullName'] = eachUser['fullName']
                            eachTS['total'] = sum([
                                eachTS[eachDay] for eachDay in days])
                            eachTS['leads'] = ProjectManager.objects.filter(
                                project__projectId=eachTS['project__projectId']
                            ).values('user__username')
                            eachTS['dates'] = ProjectTeamMember.objects.filter(
                                project__projectId=eachTS['project__projectId'],
                                member__id=eachUser['id']
                            ).values('project',
                                     'startDate',
                                     'endDate').annotate(
                                effort=Sum('plannedEffort')
                            )
                            eachTS['MonthHours'] = 0
                            if len(eachTS['dates']):
                                mh = getPlannedMonthHours(startDate, endDate,
                                                          eachTS['dates'][0]['startDate'],
                                                          eachTS['dates'][0]['endDate'],
                                                          eachTS['dates'][0]['effort'])
                                eachTS['MonthHours'] = mh
                            ptm = TimeSheetEntry.objects.filter(
                                wkend__lt=wkStrtWeek + timedelta(days=6),
                                project__bu__id__in=reportbu,
                                teamMember__id=eachUser['id'],
                                project__projectId=eachTS['project__projectId']
                            ).values('project__projectId').annotate(
                                monday=Sum('mondayH'),
                                tuesday=Sum('tuesdayH'),
                                wednesday=Sum('wednesdayH'),
                                thursday=Sum('thursdayH'),
                                friday=Sum('fridayH'),
                                saturday=Sum('saturdayH'),
                                sunday=Sum('sundayH'))
                            if len(ptm):
                                for eachptm in ptm:
                                    eachTS['ptm'] = sum(
                                        [eachptm[eachDay] for eachDay in days])
                            else:
                                eachTS['ptm'] = 0
                            startData = TimeSheetEntry.objects.filter(
                                wkstart=wkStrtWeek,
                                wkend=wkStrtWeek + timedelta(days=6),
                                project__bu__id__in=reportbu,
                                teamMember__id=eachUser['id'],
                                project__projectId=eachTS['project__projectId']
                            ).values('project__projectId').annotate(
                                monday=Sum('mondayH'),
                                tuesday=Sum('tuesdayH'),
                                wednesday=Sum('wednesdayH'),
                                thursday=Sum('thursdayH'),
                                friday=Sum('fridayH'),
                                saturday=Sum('saturdayH'),
                                sunday=Sum('sundayH'))
                            if len(startData):
                                for eachData in startData:
                                    total = sum([
                                        eachData[eachDay] for eachDay in days[
                                            :startDate.weekday()]
                                    ])
                                    eachTS['total'] = eachTS['total'] - total
                                    if eachTS['ptm']:
                                        eachTS['ptm'] = eachTS['ptm'] + total
                            endData = TimeSheetEntry.objects.filter(
                                wkstart=wkEndWeek,
                                wkend=wkEndWeek + timedelta(days=6),
                                project__bu__id__in=reportbu,
                                teamMember__id=eachUser['id'],
                                project__projectId=eachTS['project__projectId']
                            ).values('project__projectId').annotate(
                                monday=Sum('mondayH'),
                                tuesday=Sum('tuesdayH'),
                                wednesday=Sum('wednesdayH'),
                                thursday=Sum('thursdayH'),
                                friday=Sum('fridayH'),
                                saturday=Sum('saturdayH'),
                                sunday=Sum('sundayH'))
                            if len(endData):
                                for eachData in endData:
                                    endRange = endDate.weekday() + 1
                                    endtotal = sum([
                                        eachData[eachDay] for eachDay in days[
                                            endRange:]
                                    ])
                                    eachTS['total'] = eachTS['total'] - endtotal
                            eachTS['ptd'] = eachTS['total'] + eachTS['ptm']
                except:
                    eachUser['ts'] = []
            totals['ptm'], totals['total'], totals['ptd'] = 0, 0, 0
            totals['MonthHours'], totals['plannedTotal'] = 0, 0
            for eachUser in users:
                if len(eachUser['ts']):
                    totals['ptm'] += sum([eachRec['ptm']
                                         for eachRec in eachUser['ts']])
                    totals['total'] += sum([eachRec['total']
                                           for eachRec in eachUser['ts']])
                    totals['ptd'] += sum([eachRec['ptd']
                                         for eachRec in eachUser['ts']])
                    totals[
                        'MonthHours'] += sum([eachRec['MonthHours'] for eachRec in eachUser['ts']])
                    for eachTS in eachUser['ts']:
                        if len(eachTS['dates']):
                            totals[
                                'plannedTotal'] += sum([eachDate['effort'] for eachDate in eachTS['dates']])
            form = UtilizationReportForm(initial={
                'month': reportData.cleaned_data['month'],
                'year': reportData.cleaned_data['year'],
                'bu': reportData.cleaned_data['bu']
            }, user=request.user)
            if 'generate' in request.POST:
                fileName = u'Project-Perfomance{0}_{1}.xlsx'.format(
                    datetime.now().date(),
                    datetime.now().time()
                )
                fileName = fileName.replace("  ", "_")
                sheetName = ['Team-Member Perfomance Summary']
                heading = ['Member Name', 'Project Name', 'Lead(s)', 'Customer Name',
                           'BU', 'StartDate', 'EndDate', 'PlannedHours',
                           'Planned Hours for Month', 'PTM Billed Hours',
                           'Billed Hours for Month', 'PTD']
                return generateExcel(request, users, sheetName,
                                     heading, totals, fileName)
    return render(request,
                  'MyANSRSource/reportmembersummary.html',
                  {'form': form, 'data': users, 'bu': buName,
                   'month': currReportMonth, 'year': reportYear,
                   'totals': totals, 'fresh': fresh})


@login_required
@permission_required('MyANSRSource.create_project')
def ProjectPerfomanceReport(request):
    fresh = 1,
    data = {}
    iidleTotal, iothersTotal, eidleTotal, eothersTotal = 0, 0, 0, 0
    form = UtilizationReportForm(user=request.user)
    buName, currReportMonth, reportYear = 0, 0, 0
    if request.method == 'POST':
        reportData = UtilizationReportForm(request.POST,
                                           user=request.user)
        if reportData.is_valid():
            reportMonth = reportData.cleaned_data['month']
            reportYear = reportData.cleaned_data['year']
            bu = reportData.cleaned_data['bu']

            # Change Month Number to Month Name
            currReportMonth = datetime(1900, int(reportMonth), 1).strftime('%B')

            # Creating date range from month and year (User Input)
            lastDay = monthrange(int(reportYear), int(reportMonth))[1]
            startDate = date(int(reportYear), int(reportMonth), 1)
            endDate = date(int(reportYear), int(reportMonth), lastDay)

            # Finding the weekstart and weekend for generated date range
            start = getDate(request, startDate, 'Start')
            end = getDate(request, endDate, 'End')

            if bu == '0':
                reportbu = BusinessUnit.objects.all().values_list('id')
                buName = 'All'
            else:
                reportbu = BusinessUnit.objects.filter(id=bu).values_list('id')
                for eachData in BusinessUnit.objects.filter(id=bu).values('name'):
                    buName = eachData['name']

            eProjects = Project.objects.filter(
                Q(startDate__range=(startDate, endDate)) |
                Q(endDate__range=(startDate, endDate)), internal=False,
                bu__id__in=reportbu, projectId__isnull=False)
            iProjects = Project.objects.filter(
                Q(startDate__range=(startDate, endDate)) |
                Q(endDate__range=(startDate, endDate)), internal=True,
                bu__id__in=reportbu, projectId__isnull=False)
            externalData = getProjectData(request, startDate, endDate,
                                          eProjects, start, end)
            internalData = getProjectData(request, startDate, endDate,
                                          iProjects, start, end)
            if len(externalData):
                eothersTotal = sum([
                    eachData['billed'] for eachData in externalData
                ])
                eidleTotal = sum([
                    eachData['idle'] for eachData in externalData
                ])
            if len(internalData):
                iothersTotal = sum([
                    eachData['billed'] for eachData in internalData
                ])
                iidleTotal = sum([
                    eachData['idle'] for eachData in internalData
                ])
            data['external'] = externalData
            data['internal'] = internalData
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
def getProjectData(request, startDate, endDate, projects, start, end):
    report = []
    if len(projects):
        for eachProject in projects:
            data = {}
            data['pName'] = u"{0}:{1}".format(
                eachProject.projectId,
                eachProject.name
            )
            data['type'] = eachProject.projectType.description
            data['bu'] = eachProject.bu.name
            data['customer'] = eachProject.customer.name
            pm = ProjectManager.objects.filter(project=eachProject)
            if len(pm):
                data['pm'] = [eachPM.user.username for eachPM in pm]
            else:
                data['pm'] = []
            data['startDate'] = eachProject.startDate
            data['endDate'] = eachProject.endDate
            data['value'] = eachProject.totalValue
            data['pEffort'] = eachProject.plannedEffort
            data['billed'] = getEffort(request, startDate,
                                       endDate, start, end,
                                       eachProject, 'Billed')
            data['idle'] = getEffort(request, startDate,
                                     endDate, start, end,
                                     eachProject, 'Idle')
            report.append(data)
    return report


@login_required
@permission_required('MyANSRSource.create_project')
def getEffort(request, startDate, endDate, start, end, eachProject, label):
    if label == 'Billed':
        allData = TimeSheetEntry.objects.filter(
            ~Q(task__taskType='I'),
            Q(project=eachProject),
            Q(wkstart__gte=start),
            Q(wkend__lte=end)
        ).values('project').annotate(
            monday=Sum('mondayH'),
            tuesday=Sum('tuesdayH'),
            wednesday=Sum('wednesdayH'),
            thursday=Sum('thursdayH'),
            friday=Sum('fridayH'),
            saturday=Sum('saturdayH'),
            sunday=Sum('sundayH')
        )
        startData = TimeSheetEntry.objects.filter(
            ~Q(task__taskType='I'),
            Q(project=eachProject),
            Q(wkstart=start),
            Q(wkend=start + timedelta(days=6))
        ).values('project').annotate(
            monday=Sum('mondayH'),
            tuesday=Sum('tuesdayH'),
            wednesday=Sum('wednesdayH'),
            thursday=Sum('thursdayH'),
            friday=Sum('fridayH'),
            saturday=Sum('saturdayH'),
            sunday=Sum('sundayH')
        )
        endData = TimeSheetEntry.objects.filter(
            ~Q(task__taskType='I'),
            Q(project=eachProject),
            Q(wkstart=end - timedelta(days=6)),
            Q(wkend=end)
        ).values('project').annotate(
            monday=Sum('mondayH'),
            tuesday=Sum('tuesdayH'),
            wednesday=Sum('wednesdayH'),
            thursday=Sum('thursdayH'),
            friday=Sum('fridayH'),
            saturday=Sum('saturdayH'),
            sunday=Sum('sundayH')
        )
    else:
        allData = TimeSheetEntry.objects.filter(
            Q(task__taskType='I'),
            Q(project=eachProject),
            Q(wkstart__gte=start),
            Q(wkend__lte=end)
        ).values('project').annotate(
            monday=Sum('mondayH'),
            tuesday=Sum('tuesdayH'),
            wednesday=Sum('wednesdayH'),
            thursday=Sum('thursdayH'),
            friday=Sum('fridayH'),
            saturday=Sum('saturdayH'),
            sunday=Sum('sundayH')
        )
        startData = TimeSheetEntry.objects.filter(
            Q(task__taskType='I'),
            Q(project=eachProject),
            Q(wkstart=start),
            Q(wkend=start + timedelta(days=6))
        ).values('project').annotate(
            monday=Sum('mondayH'),
            tuesday=Sum('tuesdayH'),
            wednesday=Sum('wednesdayH'),
            thursday=Sum('thursdayH'),
            friday=Sum('fridayH'),
            saturday=Sum('saturdayH'),
            sunday=Sum('sundayH')
        )
        endData = TimeSheetEntry.objects.filter(
            Q(task__taskType='I'),
            Q(project=eachProject),
            Q(wkstart=end - timedelta(days=6)),
            Q(wkend=end)
        ).values('project').annotate(
            monday=Sum('mondayH'),
            tuesday=Sum('tuesdayH'),
            wednesday=Sum('wednesdayH'),
            thursday=Sum('thursdayH'),
            friday=Sum('fridayH'),
            saturday=Sum('saturdayH'),
            sunday=Sum('sundayH')
        )
    finalTotal = 0
    if len(allData):
        finalTotal = sum(
            [eachData
             [eachDay]
             for eachDay in days for eachData in allData])
    if len(startData):
        total = sum(
            [eachData
             [eachDay]
             for eachDay in days
             [: startDate.weekday()] for eachData in startData])
        finalTotal = finalTotal - total
    if len(endData):
        weekday = endDate.weekday() + 1
        total = sum(
            [eachData
             [eachDay]
             for eachDay in days[weekday:] for eachData in endData])
        finalTotal = finalTotal - total
    return finalTotal


@login_required
@permission_required('MyANSRSource.create_project')
def getInternalData(request):
    pass


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
                eachMem['invoiceCurr'] = eachMem[
                    'currentData'][0]['currMonthIN']
            else:
                eachMem['projectedTE'] = 0
                eachMem['invoiceCurr'] = 0
            try:
                eachMem['RRCurrentMonth'] = (
                    eachMem['PTDEffort'] / eachMem['projectedTE']) * eachMem['project__totalValue']
            except ZeroDivisionError:
                eachMem['RRCurrentMonth'] = 0
            if eachMem['currentData']:
                eachMem['invoiceLast'] = eachMem['prevData'][0]['currMonthIN']
            else:
                eachMem['invoiceLast'] = 0
            eachMem['invoicePTD'] = eachMem[
                'invoiceLast'] + eachMem['invoiceCurr']
            eachMem['invoicePTD'] = eachMem[
                'invoiceLast'] + eachMem['invoiceCurr']
            eachMem['currAcruval'] = eachMem[
                'RRCurrentMonth'] - eachMem['invoiceCurr']
            eachMem['ptdAcruval'] = eachMem[
                'RRCurrentMonth'] - eachMem['invoiceCurr']
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
                if len(eachData['others']):
                    diff = eachTsData['PTM'] - \
                        eachData['others'][0]['otherstotal']
                else:
                    diff = eachTsData['PTM']
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
                                eachData['monthRec'] = eachData[
                                    'totalPlanned'] / rd.months
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
            if len(eachData['others']):
                for eachDay in days:
                    d[eachDay] = totalTsValue[0][
                        eachDay] - eachData['others'][0][eachDay]
            else:
                for eachDay in days:
                    d[eachDay] = 0
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
            if sheetName[0] == 'Team-Member Perfomance Summary':
                generateMemSumContent(request, header, report, worksheet, content,
                                      alp, grdTotal, dateformat)
            else:
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
    cellNumber = [u'{0}1'.format(
        eachId) for eachId in alp[:len(heading)]]
    for eachRec in cellNumber:
        worksheet.write(eachRec, heading[counter], header)
        counter += 1
    worksheet.autofilter(u'{0}:{1}'.format(cellNumber[0],
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
        worksheet.write(row, 5, eachRec['total'], content)
        worksheet.write(row, 6, eachRec['total'], content)
        worksheet.write(row, 7, eachRec['total'], content)
        worksheet.write(row, 8, eachRec['total'], content)
        worksheet.write(row, 9, eachRec['total'], content)
        worksheet.write(row, 10, '', content)
        if eachRec['hold']:
            worksheet.write(row, 12, 'Not Submitted', content)
        else:
            worksheet.write(row, 12, 'Submitted', content)
        row += 1
    msg0 = u"Total Non-Project Hours(s) : {0}".format(grdTotal['nTotal'])
    msg1 = u"Total Project Hours(s) : {0}".format(grdTotal['pTotal'])
    msg = msg0 + '  ' + msg1
    generateReportFooter(request, worksheet, alp[12], row+1,
                         header, msg)


@login_required
def generateMemSumContent(request, header, report, worksheet,
                          content, alp, grdTotal, dateformat):
    row = 1
    for eachData in report:
        if 'fullName' in eachData:
            worksheet.write(row, 0, eachData['fullName'], content)
        else:
            worksheet.write(row, 0, '', content)
        if len(eachData['ts']):
            for eachRec in eachData['ts']:
                worksheet.write(row, 1, eachRec['project__name'], content)
                leads = [eachLead['user__username'] for eachLead in eachRec['leads']]
                if len(leads):
                    lead = ",".join(leads)
                else:
                    lead = ''
                worksheet.write(row, 2, lead, content)
                worksheet.write(row, 3, eachRec['project__customer__name'], content)
                worksheet.write(row, 4, eachRec['project__bu__name'], content)
                if len(eachRec['dates']):
                    worksheet.write(row, 5, eachRec['dates'][0]['startDate'], dateformat)
                    worksheet.write(row, 6, eachRec['dates'][0]['endDate'], dateformat)
                    worksheet.write(row, 7, eachRec['dates'][0]['effort'], content)
                worksheet.write(row, 8, eachRec['MonthHours'], content)
                worksheet.write(row, 9, eachRec['ptm'], content)
                worksheet.write(row, 10, eachRec['total'], content)
                worksheet.write(row, 11, eachRec['ptd'], content)
        else:
            worksheet.write(row, 1, 'No Timesheet for this period', content)
        row += 1
    msg0 =  u'Total PTD' + str(grdTotal['ptd'])
    msg1 =  u'Total PTM' + str(grdTotal['ptm'])
    msg2 =  u'Total Billed Hours For Month' + str(grdTotal['total'])
    msg3 =  u'Total Planned Hours For Month' + str(grdTotal['MonthHours'])
    msg4 =  u'Total Planned Hours' + str(grdTotal['plannedTotal'])
    msg = msg0 + '  ' + msg1 + '  ' + msg2 + '  ' + msg3 + '  ' + msg4
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
                    msg = u"Project Closed On : {0}".format(
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
                msg0 = u'Total Planned Effort : {0} '.format(grdTotal[0])
                msg1 = u'Total Actual Effort : {0} '.format(grdTotal[1])
                msg2 = u'Deivation(%) : {0} '.format(grdTotal[2])
                msg = msg0 + '  ' + msg1 + '  ' + msg2
            row += 1
        generateReportFooter(request, worksheet, alp[4], row+1, header, msg)


@login_required
def generateReportFooter(request, worksheet, alpValue, rowValue, cFormat, msg):
    cellRange = u'A{1}:{0}{1}'.format(alpValue, rowValue)
    worksheet.merge_range(cellRange, '', cFormat)
    totalCell = u'A{0}'.format(rowValue)
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
    cellRange = u'A{1}:{0}{1}'.format(alp[12], row+1)
    worksheet.merge_range(cellRange, '', header)
    totalCell = u'A{0}'.format(row+1)
    total = u"Total Hour(s) : {0}".format(grdTotal)
    worksheet.write(totalCell, total, header)


@login_required
def generateDownload(request, fileName):
    wrapper = FileWrapper(open(fileName, 'r'))
    content_type = mimetypes.guess_type(fileName)[0]
    response = HttpResponse(wrapper, content_type=content_type)
    response['Content-Length'] = os.path.getsize(fileName)
    response['Content-Disposition'] = u'attachment; filename="{0}"'.format(
        fileName
    )
    os.system('rm {0}'.format(fileName))
    return response


@login_required
def getDate(request, date, label):
    dateWeekDay = date.weekday()
    if dateWeekDay:
        if label == 'Start':
            date = date - timedelta(days=dateWeekDay)
        else:
            dateWeekDay = 6 - dateWeekDay
            date = date + timedelta(days=dateWeekDay)
    return date


@login_required
def getUnwantedValue(request, member, date, label, valuesList):
    dateWeekDay = date.weekday()
    extraData = []
    if dateWeekDay:
        if label == 'Start':
            wkstartDate = date - timedelta(days=dateWeekDay)
            weekData = getOneWeekData(request, member, wkstartDate,
                                      wkstartDate + timedelta(days=6),
                                      valuesList)
            if len(weekData):
                extraData = getExtraValueForWeek(request, weekData,
                                                 dateWeekDay, 'Start')
        else:
            dateWeekDay1 = 6 - dateWeekDay
            wkendDate = date + timedelta(days=dateWeekDay1)
            weekData = getOneWeekData(request, member,
                                      wkendDate - timedelta(days=6),
                                      wkendDate, valuesList)
            if len(weekData):
                extraData = getExtraValueForWeek(request, weekData,
                                                 dateWeekDay + 1,
                                                 'End')
    return extraData


@login_required
def getExtraValueForWeek(request, weekData, dateWeekDay, label):
    for eachData in weekData:
        eachData['extra'] = 0
        if label == 'Start':
            for eachDay in days[:dateWeekDay]:
                eachData['extra'] += eachData[eachDay]
        else:
            for eachDay in days[dateWeekDay:]:
                eachData['extra'] += eachData[eachDay]
    return weekData


@login_required
def getOneWeekData(request, member, wkstartDate, wkendDate, valuesList):
    return TimeSheetEntry.objects.filter(
        teamMember=member,
        wkstart=wkstartDate,
        wkend=wkendDate
    ).values(*valuesList).annotate(
        monday=Sum('mondayH'),
        tuesday=Sum('tuesdayH'),
        wednesday=Sum('wednesdayH'),
        thursday=Sum('thursdayH'),
        friday=Sum('fridayH'),
        saturday=Sum('saturdayH'),
        sunday=Sum('sundayH'))


@login_required
def getMemberExactTsHours(request, start, end, report):
    for eachData in report:
        if len(start):
            for eachStart in start:
                if eachData['project__projectId'] == eachStart['project__projectId'] and \
                        eachData['project__book__name'] == eachStart['project__book__name'] and \
                        eachData['chapter__name'] == eachStart['chapter__name'] and \
                        eachData['teamMember__username'] == eachStart['teamMember__username'] and \
                        eachData['hold'] == eachStart['hold'] and \
                        eachData['task__name'] == eachStart['task__name'] and \
                        eachData['activity__name'] == eachStart['activity__name']:
                    total = eachData['total'] - eachStart['extra']
                    if total >= 0:
                        eachData['total'] = total
        if len(end):
            for eachEnd in end:
                if eachData['project__projectId'] == eachEnd['project__projectId'] and \
                        eachData['project__book__name'] == eachEnd['project__book__name'] and \
                        eachData['chapter__name'] == eachEnd['chapter__name'] and \
                        eachData['teamMember__username'] == eachEnd['teamMember__username'] and \
                        eachData['hold'] == eachEnd['hold'] and \
                        eachData['task__name'] == eachEnd['task__name'] and \
                        eachData['activity__name'] == eachEnd['activity__name']:
                    total = eachData['total'] - eachEnd['extra']
                    if total >= 0:
                        eachData['total'] = total
    return report


@login_required
def getMinProd(request, ts, orderbyList):
    newTs = ts.annotate(
        monday=Min('mondayQ'),
        tuesday=Min('tuesdayQ'),
        wednesday=Min('wednesdayQ'),
        thursday=Min('thursdayQ'),
        friday=Min('fridayQ'),
        saturday=Min('saturdayQ'),
        sunday=Min('sundayQ'),
    ).order_by(*orderbyList)
    for eachRec in newTs:
        eachRec['min'] = 0
        l = []
        for k, v in eachRec.iteritems():
            if k in days:
                l.append(v)
            if len(l):
                eachRec['min'] = min(l)
    return newTs


@login_required
def getMaxProd(request, ts, orderbyList):
    newTs = ts.annotate(
        monday=Max('mondayQ'),
        tuesday=Max('tuesdayQ'),
        wednesday=Max('wednesdayQ'),
        thursday=Max('thursdayQ'),
        friday=Max('fridayQ'),
        saturday=Max('saturdayQ'),
        sunday=Max('sundayQ'),
    ).order_by(*orderbyList)
    for eachRec in newTs:
        eachRec['max'] = 0
        l = []
        for k, v in eachRec.iteritems():
            if k in days:
                l.append(v)
            if len(l):
                eachRec['max'] = max(l)
    return newTs


@login_required
def getAvgProd(request, ts, orderbyList):
    newTs = ts.annotate(
        monday=Avg('mondayQ'),
        tuesday=Avg('tuesdayQ'),
        wednesday=Avg('wednesdayQ'),
        thursday=Avg('thursdayQ'),
        friday=Avg('fridayQ'),
        saturday=Avg('saturdayQ'),
        sunday=Avg('sundayQ'),
    ).order_by(*orderbyList)
    for eachRec in newTs:
        eachRec['avg'] = 0
        total = 0
        for k, v in eachRec.iteritems():
            if k in days:
                total += v
            eachRec['avg'] = round((total / 7), 2)
    return newTs


def getPlannedMonthHours(Rstart, Rend, Estart, Eend, effort):
    if Eend < Rstart:
        return 0
    elif Estart > Rend:
        return 0
    else:
        if Estart > Rstart:
            num = (Rend - Estart).days
        else:
            num = (Rend - Rstart).days
        deno = (Eend - Estart).days
        if num > deno:
            return effort
        else:
            return round(effort * (num / float(deno)), 2)
