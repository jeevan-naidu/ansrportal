import logging
logger = logging.getLogger('MyANSRSource')
from django.contrib.auth.decorators import login_required
from MyANSRSource.forms import TeamMemberPerfomanceReportForm
from MyANSRSource.models import TimeSheetEntry
from django.shortcuts import render


@login_required
def TeamMemberReport(request):
    report = {}
    form = TeamMemberPerfomanceReportForm()
    name = ''
    fresh = 1
    if request.method == 'POST':
        reportData = TeamMemberPerfomanceReportForm(request.POST)
        if reportData.is_valid():
            report = TimeSheetEntry.objects.filter(
                teamMember=reportData.cleaned_data['member'],
                wkstart__gte=reportData.cleaned_data['startDate'],
                wkend__lte=reportData.cleaned_data['endDate'],
            ).values(
                'teamMember__username', 'project__maxProductivityUnits',
                'project__projectId', 'project__name',
                'project__book__name', 'task__name',
                'mondayQ', 'tuesdayQ', 'wednesdayQ',
                'thursdayQ', 'fridayQ', 'saturdayQ',
                'sundayQ',
                'mondayH', 'tuesdayH', 'wednesdayH',
                'thursdayH', 'fridayH', 'saturdayH',
                'sundayH'
            )
            days = ['monday', 'tuesday', 'wednesday',
                    'thursday', 'friday', 'saturday',
                    'sunday']
            if len(report):
                for eachData in report:
                    eachData['totalHours'], eachData['totalValue'] = 0, 0
                    eachData['avgProd'], eachData['minProd'] = 0, 0
                    eachData['maxProd'], eachData['medianProd'] = 0, 0
                    units = []
                    for k, v in eachData.iteritems():
                        if k in ['{0}H'.format(eachDay) for eachDay in days]:
                            eachData['totalHours'] += v
                        if k in ['{0}Q'.format(eachDay) for eachDay in days]:
                            units.append(v)
                            eachData['totalValue'] += v
                    eachData['maxProd'] = max(units)
                    eachData['minProd'] = min(units)
                    eachData['avgProd'] = round(sum(units) / len(units), 2)
                    eachData['medianProd'] = units[len(units) // 2]
                    name = report[0]['teamMember__username']
                    fresh = 2
            else:
                fresh = 0
        else:
            logging.error(reportData.errors)
            fresh = 1
    return render(request,
                  'MyANSRSource/reportmember.html',
                  {'form': form, 'data': report,
                   'member': name, 'fresh': fresh
                   }
                  )
