# Log file management
import logging
logger = logging.getLogger('MyANSRSource')

# FB360 models, forms import
from .models import Initiator, Respondent, Question, \
    Response, QualitativeResponse, Group, STATUS, QST_TYPE
from .forms import SurveyForm, FB360RequesteeForm, QuestionForm
from . import helper

# Miscellaneous imports
from django.contrib.formtools.wizard.views import SessionWizardView
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from datetime import date

# Decorator imports
from django.contrib.auth.decorators import login_required


# Available choices for each FB Question
CHOICE_OPTIONS = (
    ('SA', 'Strongly agree'),
    ('A', 'Agree'),
    ('NAND', 'Neither agree nor disagree'),
    ('D', 'Disagree'),
    ('CD', 'Completely disagree'),
    ('NA', 'Cannot Rate'),
    )


# Form Wizard initialization
FORMS = [
    ("Select Survey", SurveyForm),
    ("Select Requestee", FB360RequesteeForm),
    ("Give Feedback", QuestionForm),
]
TEMPLATES = {
    "Select Survey": "MyANSRSource/fb360/feedbackSurveyList.html",
    "Select Requestee": "MyANSRSource/fb360/feedbackRequestee.html",
    "Give Feedback": "MyANSRSource/fb360/feedbackQuestions.html",
}


class GiveFeedbackWizard(SessionWizardView):

    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    # Filtering out surveys where i have to give feedback
    def get_form(self, step=None, data=None, files=None):
        form = super(GiveFeedbackWizard, self).get_form(step, data, files)
        step = step if step else self.steps.current
        if step == 'Select Survey':
            form.fields['survey'].queryset = helper.GetSurveyList(self.request,
                                                                  STATUS[1][0])
        return form

    def get_context_data(self, form, **kwargs):
        context = super(GiveFeedbackWizard, self).get_context_data(
            form=form, **kwargs)

        # Returns List of requestee(s) for selected survey
        if self.steps.current == 'Select Requestee':
            if self.get_cleaned_data_for_step('Select Survey') is not None:
                surveyObj = self.get_cleaned_data_for_step(
                    'Select Survey')['survey']
            context.update({
                'data': GetMyRequesteesList(self.request, surveyObj)
            })

        # Sends the questions based on the selected user
        if self.steps.current == 'Give Feedback':
            if self.get_cleaned_data_for_step('Select Survey') is not None:
                surveyObj = self.get_cleaned_data_for_step(
                    'Select Survey')['survey']
            context.update({
                'qst': GetCurrentYearQuestions(
                    self.request, self.request.POST.get('id'), surveyObj),
                'ans': CHOICE_OPTIONS,
                'sUser': self.request.POST.get('id')
            })
        return context

    def done(self, form_list, **kwargs):
        if self.request.method == 'POST':
            submit = 0
            if 'submit' in self.request.POST:
                submit = 1
            if 'totalValue' in self.request.POST:
                for i in range(1, int(self.request.POST.get('totalValue')) + 1):
                    qst = 'qId' + str(i)
                    qtype = 'qtype' + str(i)
                    ans = 'choice' + str(i)
                    data = {'qst': int(self.request.POST.get(qst)),
                            'type': self.request.POST.get(qtype),
                            'ans': self.request.POST.get(ans)}
                    if self.request.POST.get(ans):
                        DecideAction(self.request.user,
                                     int(self.request.POST.get('sUser')),
                                     data, submit)
        return HttpResponseRedirect('/fb360/give-feedback/')

give_feedback = GiveFeedbackWizard.as_view(FORMS)


@login_required
def WrappedGiveFeedbackView(request):
    return give_feedback(request)


def DecideAction(cUser, sUser, data, action):
    """
    Handler insert / updates new response, also general feedback
    Returns nothing
    """
    # Checks QA or general response and responds accordingly
    if data['type'] == QST_TYPE[1][0]:
        try:
            # Updates user's response
            resp = Response.objects.get(employee__id=sUser,
                                        respondent=cUser,
                                        qst__id=data['qst'])
            resp.ans = data['ans']
            if action:
                resp.submitted = True
            resp.save()

        except Response.DoesNotExist:
            # Inserts new response
            resp = Response()
            resp.employee = User.objects.get(pk=sUser)
            resp.respondent = cUser
            resp.qst = Question.objects.get(pk=data['qst'])
            resp.ans = data['ans']
            if action:
                resp.submitted = True
            resp.save()
    elif data['type'] == QST_TYPE[0][0]:
        try:
            # Updates user's general response
            if len(data['ans'].strip()):
                resp = QualitativeResponse.objects.get(employee__id=sUser,
                                                       respondent=cUser,
                                                       qst__id=data['qst'])
                resp.general_fb = data['ans']
                if action:
                    resp.submitted = True
                resp.save()

        except QualitativeResponse.DoesNotExist:
            # Inserts new general response
            if len(data['ans'].strip()):
                resp = QualitativeResponse()
                resp.employee = User.objects.get(pk=sUser)
                resp.respondent = cUser
                resp.qst = Question.objects.get(pk=data['qst'])
                resp.year = date.today().year
                resp.general_fb = data['ans']
                if action:
                    resp.submitted = True
                resp.save()


@login_required
def GetCurrentYearQuestions(request, userId, surveyObj):
    """
    Handler returns list of question for chosen user
    based on priority and with its group
    Return Type
    [{
      'gName': GROUP_NAME,
      'qst_set': [{'qst': QST, 'qstId': ID, 'myfb': CHOICE_OPTIONS, \
                   'type': QUESTION_TYPE, mygeneralfb': GENERALFB, \
                   'qno': QUESTION_NUMBER
                }]
    }]
    """
    if userId is not None:
        selectedUser = User.objects.get(pk=userId)
        groupObj = GetGroupInfo(surveyObj)
        cList = []
        if groupObj:
            qno = 1
            for eachGroup in groupObj:
                cDict = {}
                QuestionYear = Question.objects.filter(
                    group=eachGroup
                ).values('category', 'qst', 'id', 'qtype').order_by('priority')
                cDict['gName'] = eachGroup.name
                cDict['qst_set'] = []
                for eachCategory in QuestionYear:
                    qDict = {}
                    if eachCategory['category'] == selectedUser.employee.designation.id:
                        qDict['qno'] = qno
                        qDict['qst'] = eachCategory['qst']
                        qDict['qstId'] = eachCategory['id']
                        qDict['type'] = eachCategory['qtype']
                        qDict['myfb'], qDict['mygeneralfb'] = '', ''
                        if eachCategory['id']:
                            qDict['myfb'] = GetMyResponse([request.user,
                                                           selectedUser,
                                                           eachCategory['id']])
                            qDict['mygeneralfb'] = GetMyResponse(
                                [request.user, selectedUser])
                    if qDict:
                        qno += 1
                        cDict['qst_set'].append(qDict)
                if len(cDict['qst_set']):
                    cList.append(cDict)
            return cList
        else:
            return cList
    else:
        return []


def GetGroupInfo(surveyObj):
    """
    Handler returns current year's group obj
    which is ordered by priority seq. given by admin
    """
    return Group.objects.filter(fb=surveyObj).order_by('priority')


def GetMyResponse(data):
    """
    Handler returns my response to corresponding Question
    and general feedback
    Return Type
        None if its a fresh record
        Returns answer / general FB if a record exist
    """
    if len(data) == 3:
        try:
            resp = Response.objects.get(employee=data[1],
                                        respondent=data[0],
                                        qst__id=data[2])
            return [resp.ans, resp.submitted]
        except Response.DoesNotExist:
            return None
    elif len(data) == 2:
        try:
            resp = QualitativeResponse.objects.get(employee=data[1],
                                                   respondent=data[0],
                                                   year=date.today().year)
            return [resp.general_fb, resp.submitted]
        except QualitativeResponse.DoesNotExist:
            return None


@login_required
def GetMyRequesteesList(request, surveyObj):
    """
    Handler returns list of requestees who wants
    feedback from Me for selected survey, with their names
    """
    l = []
    # Getting requests from whom i got connect request
    peerObj = Respondent.objects.filter(employee=request.user,
                                        status=STATUS[1][0],
                                        initiator__survey=surveyObj)
    empPeerObj = Initiator.objects.filter(
        id__in=[eachPeerObj.initiator.id for eachPeerObj in peerObj]
    )
    for eachObj in empPeerObj:
        l.append(ConstructUserInfo(request, eachObj.employee, surveyObj))
    # Getting requests to whom i sent connect request
    empPeerObj = Initiator.objects.filter(employee=request.user,
                                          survey=surveyObj)
    peerObj = Respondent.objects.filter(
        initiator__in=[eachEmpPeerObj for eachEmpPeerObj in empPeerObj],
        status=STATUS[1][0],
        initiator__survey=surveyObj
    )
    for eachObj in peerObj:
        l.append(ConstructUserInfo(request, eachObj.employee, surveyObj))
    return l


@login_required
def ConstructUserInfo(request, cUser, surveyObj):
    """
    Handler returns a dict of user's full name, id,
    and remaining questions count
    Return Type
        {'name': USER_FULL_NAME, 'id': USER_ID, QCount': QST_COUNT}
    """
    d = {}
    d['name'] = helper.GetUserFullName(cUser)
    d['id'] = cUser.id
    d['QCount'] = GetQuestionRemainingCount(request, cUser, surveyObj)
    return d


@login_required
def GetQuestionRemainingCount(request, cUser, surveyObj):
    """
    Handler to get number question remaining to answer for
    requestee, for selected survey
    Returns
        Total number of question's count for current year
        if no answer is recorded.
        Else Remaining questions's count will be returned.
    """
    QuestionYear = Question.objects.filter(
        group__fb=surveyObj
    ).values('category')
    totalQuestionYear = [
        eachCategory
        ['category']
        for eachCategory in
        QuestionYear
        if eachCategory['category'] == cUser.employee.designation.id]
    if len(totalQuestionYear):
        # QA Choices
        totalResp = Response.objects.filter(
            employee=cUser,
            respondent=request.user,
            qst__group__fb=surveyObj
        )
        totalQResp = QualitativeResponse.objects.filter(
            employee=cUser,
            respondent=request.user,
            qst__group__fb=surveyObj
        )
        if len([eachResp.submitted for eachResp in totalResp] or
               [eachResp.submitted for eachResp in totalQResp]):
            if len(totalResp):
                if [eachResp.submitted for eachResp in totalResp][0]:
                    return -1
                else:
                    return (len(totalQuestionYear)) - \
                        (len(totalResp) + len(totalQResp))
            elif len(totalQResp):
                if [eachResp.submitted for eachResp in totalQResp][0]:
                    return -1
                else:
                    return (len(totalQuestionYear)) - \
                        (len(totalResp) + len(totalQResp))
        else:
            return (len(totalQuestionYear)) - \
                (len(totalResp) + len(totalQResp))
    else:
        return 0
