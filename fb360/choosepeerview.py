# Log file management
import logging
logger = logging.getLogger('MyANSRSource')

# FB360 models and forms import
from .forms import SurveyForm, PeerForm
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
    ("Choose Peer", PeerForm),
]
TEMPLATES = {
    "Select Survey": "MyANSRSource/fb360/peerSurveyList.html",
    "Choose Peer": "MyANSRSource/fb360/choosePeer.html",
}


class ChoosePeerWizard(SessionWizardView):

    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    # Filtering out surveys which i am eligible for
    def get_form(self, step=None, data=None, files=None):
        form = super(ChoosePeerWizard, self).get_form(step, data, files)
        step = step if step else self.steps.current
        if step == 'Select Survey':
            form.fields['survey'].queryset = FB360.objects.filter(
                eligible=self.request.user,
            )
        return form

    # Returns List of peers and their status
    # along with peer selection eligible or not
    def get_context_data(self, form, **kwargs):
        context = super(ChoosePeerWizard, self).get_context_data(
            form=form, **kwargs)
        if self.steps.current == 'Choose Peer':
            if self.get_cleaned_data_for_step('Select Survey') is not None:
                surveyObj = self.get_cleaned_data_for_step(
                    'Select Survey')['survey']
                eligible = helper.IsPageActionEligible('Request',
                                                       surveyObj)
            context.update(
                {'request_eligible': eligible,
                 'data': GetMyPeerList(
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
            if IsPeerEligible(self.request, eachResp, InitiatorObj) and \
                    IsPeerRequestExist(self.request, eachResp, InitiatorObj):
                respObj = Respondent()
                respObj.employee = eachResp
                respObj.initiator = InitiatorObj
                respObj.save()
        return HttpResponseRedirect('/fb360/choose-peer/')

choose_peer = ChoosePeerWizard.as_view(FORMS)


@login_required
def WrappedChoosePeerView(request):
    return choose_peer(request)


# Helper function specific for choose peer screen
@login_required
def GetMyPeerList(request, surveyObj):
    """
    Handler sends back peer list for logged in user for
    selected survey.
    Returns user's employee Id, firstname, lastname, email id and status
    """
    myObj = Initiator.objects.filter(
        employee=request.user,
        survey=surveyObj
    )
    """
    myObjAccepted = Respondent.objects.filter(~Q(status=STATUS[3][0]),
                                              respondent_type=RESPONDENT_TYPES[0][0],
                                              employee=request.user,
                                              initiator__survey=surveyObj)
    """
    if myObj:
        myPeerObj = Respondent.objects.filter(~Q(status=STATUS[3][0]),
                                              respondent_type=RESPONDENT_TYPES[0][0],
                                              initiator=myObj,
                                              initiator__survey=surveyObj)
        if myPeerObj:
            list1 = helper.ConstructList(request, myPeerObj)
            """
            list2 = helper.ConstructList(request,
                                         [eachObj.initiator
                                          for eachObj in myObjAccepted])
            """
            return list1
        else:
            return None
    else:
        return None


@login_required
def IsPeerEligible(request, eachPeer, empPeerObj):
    """
    Handler checks the current peer is eligible to be added or not.
    Eligible Criteria:
        Peer must not be None.
        Peer must not be already added to this employee in Approved / Pending
        state for selected survey.
        Peer cannot be self assigned.
        Peer cannot be my manager.
        Peer cannot be my additional manager
        If i am a manager, i can't add my reportee as peer
    Returns 0 -> Not Eligible or  1 -> Is Eligible
    """
    if eachPeer != request.user:
        try:
            if request.user.employee.manager != eachPeer.employee:
                myAddManagerObj = Respondent.objects.filter(
                    employee=eachPeer,
                    initiator=empPeerObj,
                    initiator__survey=empPeerObj.survey,
                    respondent_type=RESPONDENT_TYPES[3][0],
                    status__in=(STATUS[0][0], STATUS[1][0])
                )
                if len(myAddManagerObj):
                    return 0
                else:
                    myPeerObj = Respondent.objects.filter(
                        employee=eachPeer,
                        initiator=empPeerObj,
                        initiator__survey=empPeerObj.survey,
                        respondent_type=RESPONDENT_TYPES[0][0]
                    )
                    if myPeerObj:
                        if myPeerObj.filter(status__in=(STATUS[3][0],
                                                        STATUS[2][0])):
                            helper.UpdateRequestStatus(myPeerObj[0], STATUS[0][0])
                            return 0
                        else:
                            return 0
                    else:
                        if eachPeer.employee.manager == request.user.employee:
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
def IsPeerRequestExist(request, eachPeer, empPeerObj):
    """
    Handler checks the current peer has requested me
    Returns 0 -> Not Eligible or  1 -> Is Eligible
    """
    """
    req = Respondent.objects.filter(
        employee=request.user, initiator__survey=empPeerObj.survey,
        respondent_type=RESPONDENT_TYPES[0][0]
    ).values(
        'initiator__employee'
    )
    """
    if eachPeer.id in Respondent.objects.filter(initiator=empPeerObj).values('employee__id'):
        return 0
    else:
        return 1
