from django.shortcuts import render
from django.views.generic import View
from Reports.forms import MilestoneReportsForm
# Create your views here.

class MilestoneReportsView(View):
    ''' MilestoneReportsView '''
    
    
    def get(self, request):
        
        context_data = {'form':None}
        form = MilestoneReportsForm()
        context_data['form'] = form
        return render(request, 'milestone_reports.html', context_data)
    
    def post(self, request):
        pass