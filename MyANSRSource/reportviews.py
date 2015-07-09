import logging
logger = logging.getLogger('MyANSRSource')
from django.contrib.auth.decorators import login_required
from MyANSRSource.forms import TeamMemberPerfomanceReportForm, \
    ProjectPerfomanceReportForm, UtilizationReportForm, BTGForm, \
    BTGReportForm
from MyANSRSource.models import TimeSheetEntry, ProjectChangeInfo, \
    ProjectMilestone, ProjectTeamMember, ProjectManager, Project
from django.contrib.auth.decorators import permission_required
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
@permission_required('MyANSRSource.create_project')
def TeamMemberReport(request):
    report = {}
    member, startDate, endDate = '', '', ''
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
                if 'status' in request.POST:
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
        else:
            logger.error(reportData.errors)
            fresh = 1
    return render(request,
                  'MyANSRSource/reportmember.html',
                  {'form': form, 'data': report, 'fresh': fresh,
                   'grandTotal': grdTotal, 'startDate': startDate,
                   'endDate': endDate, 'member': member
                   })


@login_required
@permission_required('MyANSRSource.create_project')
def ProjectReport(request):
    basicData = {}
    crData = []
    tsData = []
    msData = []
    pEffort = 0
    fresh = 1
    actualTotal, plannedTotal, deviation = 0, 0, 0
    form = ProjectPerfomanceReportForm(user=request.user)
    if request.method == 'POST':
        fresh = 0
        reportData = ProjectPerfomanceReportForm(request.POST,
                                                 user=request.user)
        if reportData.is_valid():
            cProject = reportData.cleaned_data['project']
            basicData = {
                'code': cProject.projectId,
                'name': cProject.name,
                'startDate': cProject.startDate,
                'endDate': cProject.endDate,
                'plannedEffort': cProject.plannedEffort,
                'totalValue': cProject.totalValue,
                'salesForceNumber': cProject.salesForceNumber,
                'signed': cProject.signed
            }
            crData = ProjectChangeInfo.objects.filter(
                project=cProject
            ).values('crId', 'reason', 'endDate', 'po', 'revisedEffort',
                     'revisedTotal', 'closed', 'closedOn')
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
                    deviation = round((
                        (actualTotal - plannedTotal) * 100
                    ) / plannedTotal)
                except ZeroDivisionError:
                    deviation = 0
            form = ProjectPerfomanceReportForm(
                user=request.user,
                initial={'project': cProject}
            )
            if 'status' in request.POST:
                fileName = '{0}_{1}.xlsx'.format(
                    datetime.now().date(),
                    datetime.now().time()
                )
                fileName = fileName.replace("  ", "_")
                report = [basicData, crData, msData, tsData]
                sheetName = ['Basic Information',
                             'Change Requests',
                             'Milestones',
                             'TM Perfomance']
                heading = [
                    ['Project Name', 'Start Date', 'End Date', 'Planned Effort',
                     'Total Value', 'salesForceNumber', 'Signed'],
                    ['CR#', 'Reason', 'End Date', 'P.O.', 'Revised Effort',
                     'Revised Total'],
                    ['Milestone Name', 'Milestone Date', 'Financial', 'Value',
                     'Completed'],
                    ['Member Name', 'Designation', 'Planned Effort',
                     'Actual Effort', 'Deviation(%)']
                ]
                grdTotal = [plannedTotal, actualTotal, deviation]
                return generateExcel(request, report, sheetName,
                                     heading, grdTotal, fileName)
    return render(request,
                  'MyANSRSource/reportproject.html',
                  {'form': form, 'basicData': basicData, 'fresh': fresh,
                   'crData': crData, 'tsData': tsData, 'msData': msData,
                   'actualTotal': actualTotal, 'plannedTotal': plannedTotal,
                   'deviation': deviation}
                  )


@login_required
@permission_required('MyANSRSource.create_project')
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
@permission_required('MyANSRSource.create_project')
def RevenueRecognitionReport(request):
    fresh = 1
    # cMonth = datetime.now().month
    btg = BTGReportForm()
    data = Project.objects.exclude(
        closed=True,
    ).values('projectId', 'name', 'totalValue',
             'plannedEffort', 'startDate', 'endDate')
    if len(data):
        for eachMem in data:
            # l = []
            mem = ProjectManager.objects.filter(
                project__projectId=eachMem['projectId']
            ).values('user__username')
            eachMem['tl'] = mem
        fresh = 0
    if request.method == 'POST':
        pass
    return render(request, 'MyANSRSource/reportrevenue.html',
                  {'fresh': fresh,
                   'data': data,
                   'form': btg})


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
        worksheet.write(row, 11, eachRec['project__maxProductivityUnits'],
                        content)
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
    else:
        row, msg = 1, ''
        for eachRec in report:
            if 'crId' in eachRec:
                worksheet.write(row, 0, eachRec['crId'], content)
                worksheet.write(row, 1, eachRec['reason'], content)
                worksheet.write(row, 2, eachRec['endDate'], dateformat)
                worksheet.write(row, 3, eachRec['po'], content)
                worksheet.write(row, 4, eachRec['revisedEffort'], content)
                worksheet.write(row, 5, eachRec['revisedTotal'], content)
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
def BalanceToGo(request):
    btgForm = BTGForm(user=request.user)
    return render(request,
                  'MyANSRSource/reportbtg.html',
                  {'form': btgForm})


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
