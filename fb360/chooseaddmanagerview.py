# Log file management
import logging
logger = logging.getLogger('MyANSRSource')

# FB360 models and forms import
from .forms import SurveyForm, AdditionalManagerForm
from .models import Initiator, Respondent, FB360, STATUS, RESPONDENT_TYPES
from . import helper

# Decorator imports
from django.contrib.auth.decorators import login_required

# Internal imports
from django.contrib.formtools.wizard.views import SessionWizardView
from django.db.models import Q
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect


# Form Wizard initialization
FORMS = [
    ("Select Survey", SurveyForm),
    ("Choose Additional Manager", AdditionalManagerForm),
]
TEMPLATES = {
    "Select Survey": "MyANSRSource/fb360/addManagerSurveyList.html",
    "Choose Additional Manager": "MyANSRSource/fb360/chooseAdditionalManager.html",
}


class ChooseAddManagerWizard(SessionWizardView):

    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    # Filtering out surveys which i am eligible for
    def get_form(self, step=None, data=None, files=None):
        form = super(ChooseAddManagerWizard, self).get_form(step, data, files)
        step = step if step else self.steps.current
        if step == 'Select Survey':
            form.fields['survey'].queryset = FB360.objects.filter(
                eligible=self.request.user,
            )
        return form

    # Returns List of peers and their status
    # along with peer selection eligible or not
    def get_context_data(self, form, **kwargs):
        context = super(ChooseAddManagerWizard, self).get_context_data(
            form=form, **kwargs)
        if self.steps.current == 'Choose Additional Manager':
            if self.get_cleaned_data_for_step('Select Survey') is not None:
                surveyObj = self.get_cleaned_data_for_step(
                    'Select Survey')['survey']
                eligible = helper.IsPageActionEligible('Request',
                                                       surveyObj)
            context.update(
                {'request_eligible': eligible,
                 'data': GetMyAddManagerList(
                     self.request, surveyObj
                 )})
        return context

    def done(self, form_list, **kwargs):
        request_data = [form.cleaned_data for form in form_list]

        # Logic to save the request
        InitiatorObj = Initiator()
        InitiatorObj.employee = self.request.user
        InitiatorObj.survey = request_data[0]['survey']
        try:
            InitiatorObj.save()
        except IntegrityError:
            InitiatorObj = Initiator.objects.get(employee=self.request.user,
                                                 survey=request_data[0]['survey'])
        for eachResp in request_data[1]['respondents']:
            if IsAddManagerEligible(self.request, eachResp, InitiatorObj) and \
                    IsAddManagerRequestExist(self.request, eachResp, InitiatorObj):
                respObj = Respondent()
                respObj.employee = eachResp
                respObj.initiator = InitiatorObj
                respObj.respondent_type = RESPONDENT_TYPES[3][0]
                respObj.save()
        return HttpResponseRedirect('/fb360/choose-additional-manager/')

choose_manager = ChooseAddManagerWizard.as_view(FORMS)


@login_required
def WrappedChooseAddManagerView(request):
    return choose_manager(request)


# Helper function specific for choose additional manager screen
@login_required
def GetMyAddManagerList(request, surveyObj):
    """
    Handler sends back additional manager list for logged in user for
    selected survey.
    Returns user's employee Id, firstname, lastname, email id and status
    """
    myObj = Initiator.objects.filter(
        employee=request.user,
        survey=surveyObj
    )
    if myObj:
        myPeerObj = Respondent.objects.filter(~Q(status=STATUS[3][0]),
                                              respondent_type=RESPONDENT_TYPES[3][0],
                                              initiator=myObj,
                                              initiator__survey=surveyObj)
        if myPeerObj:
            list1 = helper.ConstructList(request, myPeerObj)
            return list1
        else:
            return None
    else:
        return None


@login_required
def IsAddManagerEligible(request, eachManager, empPeerObj):
    """
    Handler checks the current additional manager nominee is eligible to be added or not.
    Eligible Criteria:
        Additional manager must not be None.
        Additional manager must not be already added to this employee in Approved / Pending
        state for selected survey.
        Additional manager cannot be self assigned.
        Additional manager cannot be my manager.
        I can't add my reportee as my additional manager
        I Can't add my peer as additional manager
    Returns 0 -> Not Eligible or  1 -> Is Eligible
    """
    if eachManager != request.user:
        try:
            if request.user.employee.manager != eachManager.employee:
                myPeerObj = Respondent.objects.filter(
                    employee=eachManager,
                    initiator=empPeerObj,
                    initiator__survey=empPeerObj.survey,
                    respondent_type=RESPONDENT_TYPES[0][0],
                    status__in=(STATUS[1][0], STATUS[2][0])
                )
                if len(myPeerObj):
                    return 0
                else:
                    myRespObj = Respondent.objects.filter(
                        employee=eachManager,
                        initiator=empPeerObj,
                        initiator__survey=empPeerObj.survey,
                        respondent_type=RESPONDENT_TYPES[3][0]
                    )
                    if myRespObj:
                        if myRespObj.filter(status__in=(STATUS[3][0],
                                                        STATUS[2][0])):
                            helper.UpdateRequestStatus(myRespObj[0], STATUS[0][0])
                            return 0
                        else:
                            return 0
                    else:
                        if eachManager.employee.manager == request.user.employee:
                            return 0
                        else:
                            return 1
            else:
                return 0
        except ObjectDoesNotExist:
            return 0
    else:
        return 0


@login_required
def IsAddManagerRequestExist(request, eachManager, empPeerObj):
    """
    Handler checks the current user has requested me as additional manager
    Returns 0 -> Not Eligible or  1 -> Is Eligible
    """
    req = Respondent.objects.filter(
        employee=request.user, initiator__survey=empPeerObj.survey,
        respondent_type=RESPONDENT_TYPES[3][0]
    ).values(
        'initiator__employee'
    )
    if eachManager.id in [eachReq['initiator__employee'] for eachReq in req]:
        return 0
    else:
        return 1
