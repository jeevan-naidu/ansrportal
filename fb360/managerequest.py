# Log file management
import logging
logger = logging.getLogger('MyANSRSource')

# FB360 models and forms import
from .forms import SurveyForm, DecideOnRequestForm
from .models import Respondent, FB360, STATUS
from . import helper

# Decorator imports
from django.contrib.auth.decorators import login_required

# Internal imports
from django.contrib.formtools.wizard.views import SessionWizardView
from django.http import HttpResponseRedirect


# Form Wizard initialization
FORMS = [
    ("Select Survey", SurveyForm),
    ("Decide on request", DecideOnRequestForm),
]
TEMPLATES = {
    "Select Survey": "MyANSRSource/fb360/decideSurveyList.html",
    "Decide on request": "MyANSRSource/fb360/decideOnRequest.html",
}


class DecideOnRequestWizard(SessionWizardView):

    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    # Filtering out surveys which i have got requests from
    def get_form(self, step=None, data=None, files=None):
        form = super(DecideOnRequestWizard, self).get_form(step, data, files)
        step = step if step else self.steps.current
        if step == 'Select Survey':
            resp = Respondent.objects.filter(
                employee=self.request.user,
                status=STATUS[0][0]
            ).values('initiator__survey')
            surveyIds = [eachResp['initiator__survey'] for eachResp in resp]
            form.fields['survey'].queryset = FB360.objects.filter(
                id__in=surveyIds,
            )
        return form

    # Returns List of pending requests
    # along with deciding action eligible or not
    def get_context_data(self, form, **kwargs):
        context = super(DecideOnRequestWizard, self).get_context_data(
            form=form, **kwargs)
        if self.steps.current == 'Decide on request':
            if self.get_cleaned_data_for_step('Select Survey') is not None:
                surveyObj = self.get_cleaned_data_for_step(
                    'Select Survey')['survey']
                eligible = helper.IsPageActionEligible('Accept',
                                                       surveyObj)
            context.update(
                {'accept_eligible': eligible,
                 'data': GetMyRequestList(self.request, surveyObj)
                 })
        return context

    def done(self, form_list, **kwargs):
        if self.request.method == 'POST':
            for i in range(1, int(self.request.POST.get('totalValue')) + 1):
                choice = "choice" + str(i)
                rowid = "rowid" + str(i)
                if choice in self.request.POST:
                    myPeerObj = Respondent.objects.get(
                        id=int(self.request.POST.get(rowid))
                    )
                    helper.UpdateRequestStatus(myPeerObj,
                                               self.request.POST.get(choice))
        return HttpResponseRedirect('/fb360/decide-action/')

decide_request = DecideOnRequestWizard.as_view(FORMS)


@login_required
def WrappedDecideOnRequestView(request):
    return decide_request(request)


# Helpers for reportee request screens
@login_required
def GetMyRequestList(request, surveyObj):
    """
    Returns List of my pending requests for selected survey.
    """
    myRequests = Respondent.objects.filter(
        employee=request.user,
        status=STATUS[0][0],
        initiator__survey=surveyObj
    )

    if myRequests:
        return helper.ConstructList(request,
                                    [eachReq.initiator
                                     for eachReq in myRequests])
    else:
        return None
