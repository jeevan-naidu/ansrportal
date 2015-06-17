import logging
logger = logging.getLogger('MyANSRSource')
from django.contrib.auth.decorators import login_required
from MyANSRSource.forms import TeamMemberPerfomanceReportForm, \
    ProjectPerfomanceReportForm, UtilizationReportForm
from MyANSRSource.models import TimeSheetEntry, ProjectChangeInfo, \
    ProjectMilestone, ProjectTeamMember, ProjectManager
from django.shortcuts import render
from datetime import timedelta, datetime
from django.db.models import Sum, Count
from employee.models import Employee
from django.core.servers.basehttp import FileWrapper
from django.http import HttpResponse
import mimetypes
import xlsxwriter
import os
import string


@login_required
def TeamMemberReport(request):
    report = {}
    form = TeamMemberPerfomanceReportForm()
    grdTotal = ''
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
                fresh = 2
                if 'status' in request.POST:
                    heading = ['Project Code', 'Project Name', 'Book',
                               'Chapter', 'Task / Activity', 'Total Hours',
                               'Total Productivity', 'Avg. Productivity',
                               'Min. Productivity', 'Max. Productivity',
                               'Median Productivity', 'Norm', 'Status']
                    return generateExcel(request, report, heading, grdTotal)
            else:
                fresh = 0
            form = TeamMemberPerfomanceReportForm(initial={
                'startDate': reportData.cleaned_data['startDate'],
                'endDate': reportData.cleaned_data['endDate'],
                'member': reportData.cleaned_data['member']
            })
        else:
            logger.error(reportData.errors)
            fresh = 1
    return render(request,
                  'MyANSRSource/reportmember.html',
                  {'form': form, 'data': report, 'fresh': fresh,
                   'grandTotal': grdTotal
                   })


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
            tsData = TimeSheetEntry.objects.filter(
                project=cProject
            ).values(
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
def ProjectPerfomanceReport(request):
    data = {}
    fresh = 1
    iidleTotal, iothersTotal, eidleTotal, eothersTotal = 0, 0, 0, 0
    form = UtilizationReportForm(user=request.user)
    reportMonth, reportYear = 0, 0
    if request.method == 'POST':
        reportData = UtilizationReportForm(request.POST,
                                           user=request.user)
        if reportData.is_valid():
            reportMonth = reportData.cleaned_data['month']
            reportYear = reportData.cleaned_data['year']
            reportbu = reportData.cleaned_data['bu']
            tsData = TimeSheetEntry.objects.filter(
                wkstart__year=reportYear,
                wkstart__month=reportMonth,
                project__internal=True,
                project__bu=reportbu,
                project__projectId__isnull=False
            ).values(
                'project__customer__name', 'project__projectId',
                'project__name', 'project__projectType__description',
                'project__bu__name', 'project__startDate',
                'project__endDate', 'project__totalValue',
                'project__plannedEffort'
            ).order_by('project__bu__name').distinct()
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
            ).order_by('project__bu__name').distinct()
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
    return render(request,
                  'MyANSRSource/reportutilize.html',
                  {'form': form, 'data': data, 'fresh': fresh,
                   'iiTotal': iidleTotal, 'ioTotal': iothersTotal,
                   'eiTotal': eidleTotal, 'eoTotal': eothersTotal,
                   'month': reportMonth, 'year': reportYear})


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
            )
        else:
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
def generateExcel(request, report, heading, grdTotal):
    if len(report):
        dateObj = datetime.now().date()
        timeObj = datetime.now().time()
        fileName = "{0}-{1}-{2}_{3}_{4}_{5}.xlsx".format(dateObj.day,
                                                         dateObj.month,
                                                         dateObj.year,
                                                         timeObj.hour,
                                                         timeObj.minute,
                                                         timeObj.second)
        workbook = xlsxwriter.Workbook(fileName, {'constant_memory': True})
        worksheet = workbook.add_worksheet('MyANSRSOURCE Report')
        header = workbook.add_format({
            'bold': True,
            'font_name': 'Droid Sans',
            'font_size': 11,
            'align': 'center',
            'valign': 'vcenter',
        })
        content = workbook.add_format({
            'font_name': 'Droid Sans',
            'font_size': 11,
            'align': 'center',
            'valign': 'vcenter',
        })
        alp = list(string.ascii_uppercase)
        counter = 0
        cellNumber = ['{0}1'.format(eachId) for eachId in alp[:len(heading)]]
        for eachRec in cellNumber:
            worksheet.write(eachRec, heading[counter], header)
            counter += 1
        generateContent(request, header, report, worksheet, content,
                        alp, grdTotal)
        worksheet.autofilter('{0}:{1}'.format(cellNumber[0], cellNumber[-1]))
        workbook.close()
        return generateDownload(request, fileName)
    else:
        return {}


@login_required
def generateContent(request, header, report, worksheet,
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
