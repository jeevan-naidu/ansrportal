# Log file management
import logging
logger = logging.getLogger('MyANSRSource')

# FB360 models and forms import
from .forms import SurveyForm, ChooseReporteeForm
from .models import Initiator, Respondent, FB360, STATUS, RESPONDENT_TYPES
from . import helper

# Employee model import
import employee

# Decorator imports
from django.contrib.auth.decorators import login_required
from .ismanager import is_manager

# Internal imports
from django.contrib.formtools.wizard.views import SessionWizardView
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User

# Exception handlers import
from django.db import IntegrityError


# Form Wizard initialization
FORMS = [
    ("Select Survey", SurveyForm),
    ("Choose Reportee", ChooseReporteeForm),
]
TEMPLATES = {
    "Select Survey": "MyANSRSource/fb360/reporteeSurveyList.html",
    "Choose Reportee": "MyANSRSource/fb360/chooseReportee.html",
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

    # Returns List of Reportee and their status
    # along with reportee selection eligible or not
    def get_context_data(self, form, **kwargs):
        context = super(ChoosePeerWizard, self).get_context_data(
            form=form, **kwargs)
        if self.steps.current == 'Choose Reportee':
            if self.get_cleaned_data_for_step('Select Survey') is not None:
                surveyObj = self.get_cleaned_data_for_step(
                    'Select Survey')['survey']
                eligible = helper.IsPageActionEligible('Choose',
                                                       surveyObj)
            context.update(
                {'choose_eligible': eligible,
                 'data': [
                     GetMyReporteeList(self.request, surveyObj),
                     GetMyReporteeFeedbackList(self.request, surveyObj)
                 ]})
        return context

    def done(self, form_list, **kwargs):
        request_data = [form.cleaned_data for form in form_list]

        if self.request.method == 'POST':
            if 'totalValue' in self.request.POST:
                init = Initiator.objects.filter(
                    employee=self.request.user,
                    survey=request_data[0]['survey'],
                )
                if init:
                    initObj = init[0]
                else:
                    initObj = Initiator()
                    initObj.survey = request_data[0]['survey']
                    initObj.employee = self.request.user
                    initObj.save()
                for i in range(1, int(self.request.POST.get('totalValue')) + 1):
                    choice = "choice" + str(i)
                    rowid = "rowid" + str(i)
                    if self.request.POST.get(choice) is not None:
                        try:
                            mgrReqObj = Respondent()
                            mgrReqObj.employee = User.objects.get(
                                pk=int(self.request.POST.get(rowid))
                            )
                            mgrReqObj.initiator = initObj
                            mgrReqObj.respondent_type = RESPONDENT_TYPES[1][0]
                            mgrReqObj.status = STATUS[0][0]
                            mgrReqObj.save()
                        except IntegrityError:
                            mgrReqObj = Respondent.objects.get(
                                employee__id=int(self.request.POST.get(rowid)),
                                initiator__survey=request_data[0]['survey'],
                                respondent_type=RESPONDENT_TYPES[1][0]
                            )
                            helper.UpdateRequestStatus(mgrReqObj, STATUS[0][0])
        return HttpResponseRedirect('/fb360/choose-reportee/')

choose_peer = ChoosePeerWizard.as_view(FORMS)


@login_required
@is_manager
def WrappedChoosePeerView(request):
    return choose_peer(request)


# Helpers for reportee request screens
@login_required
@is_manager
def GetMyReporteeList(request, surveyObj):
    """
    Handler returns the list of eligible reportees
    Eligible Criteria
        Manager cannot send request to reportee
        when already a request is in place with either approved
        or pending state
        Manager can resend request if reportee rejects request.
    """
    myReportees = employee.models.Employee.objects.filter(
        manager=request.user.employee)
    mgrReq = Respondent.objects.filter(
        respondent_type=RESPONDENT_TYPES[1][0],
        initiator__survey=surveyObj
    )
    requestId = [eachReq.employee.id for eachReq in mgrReq]
    reporteeId = [eachReportee.user.id for eachReportee in myReportees]
    # Union of requestId and reporteeId
    reqExist = list(set(requestId) & set(reporteeId))
    if len(reqExist):
        # Removes reporteeId whose request already exist
        finalList = list(set(reporteeId) - set(reqExist))
    else:
        finalList = reporteeId
    # Picking eligible re-requests respondent ids if any
    rejectedReq = Respondent.objects.filter(
        employee__employee__manager=request.user.employee,
        status=STATUS[2][0],
        respondent_type=RESPONDENT_TYPES[1][0],
        initiator__survey=surveyObj
    )
    if len(rejectedReq):
        finalList = finalList + [eachReq.employee.id
                                 for eachReq in rejectedReq]
    validReportees = User.objects.filter(id__in=finalList)
    l = []
    for eachValidReportee in validReportees:
        d = {}
        d['id'] = eachValidReportee.id
        d['name'] = helper.GetUserFullName(eachValidReportee)
        d['emailid'] = eachValidReportee.email
        l.append(d)
    return l


@login_required
@is_manager
def GetMyReporteeFeedbackList(request, surveyObj):
    """
    Handler returns requested and approved list of reportees with
    first name, last name, email and employee ID along with thier status
    """
    myFBReportees = employee.models.Employee.objects.filter(
        manager=request.user.employee)
    myFBReporteesId = [eachReportee.user.id for eachReportee in myFBReportees]
    myFBReporteesStatus = Respondent.objects.filter(
        employee__in=myFBReporteesId,
        status__in=[STATUS[1][0], STATUS[0][0]],
        initiator__survey=surveyObj
    )
    l = []
    for eachReporteeStatus in myFBReporteesStatus:
        d = {}
        d['name'] = helper.GetUserFullName(eachReporteeStatus.employee)
        d['emailid'] = eachReporteeStatus.employee.email
        d['status'] = eachReporteeStatus.status
        l.append(d)
    return l
