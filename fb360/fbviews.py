# Log file management
import logging
logger = logging.getLogger('MyANSRSource')

# FB360 models, views import
from .models import Initiator, Respondent, Question, \
    Response, QualitativeResponse, Group, STATUS
import fb360

# Miscellaneous imports
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from datetime import date

# Decorator imports
from django.contrib.auth.decorators import login_required
from .fb360eligible import eligible_360
from .fbeligible import fb_eligible


# Available choices for each FB Question
CHOICE_OPTIONS = (
    ('SA', 'Strongly agree'),
    ('A', 'Agree'),
    ('NAND', 'Neither agree nor disagree'),
    ('D', 'Disagree'),
    ('CD', 'Completely disagree'),
    ('NA', 'Not Applicable'),
    )


@login_required
@eligible_360
@fb_eligible
def MyFBRequestees(request):
    """
    Handler shows list of requestees who wants
    feedback from Me
    Also supports to choose a requestee to give feedback
    """
    if request.method == 'POST':
        # To pass selected user from one screen to another
        request.session['selectedUser'] = int(request.POST.get('id'))
        return redirect('/fb360/feedback/qa')
    else:
        return render(request, 'fb360FeedbackRequestee.html',
                      {'data': GetMyRequesteesList(request)}
                      )


@login_required
@eligible_360
@fb_eligible
def GetQA(request):
    """
    Handler shows list of QA for chosen user along with
    previously selected answers if any.
    Also has the ability to update answers
    """
    if request.method == 'POST':
        submit = 0
        if 'submit' in request.POST:
            submit = 1
        for i in range(1, int(request.POST.get('totalValue')) + 1):
            qst = 'qId' + str(i)
            qtype = 'qtype' + str(i)
            ans = 'choice' + str(i)
            data = {'qst': int(request.POST.get(qst)),
                    'type': request.POST.get(qtype),
                    'ans': request.POST.get(ans)}
            if request.POST.get(ans):
                DecideAction(request.user, int(request.session['selectedUser']),
                             data, submit)
    return render(request, 'fb360FeedbackQA.html',
                  {'qst': GetCurrentYearQuestions(request),
                   'ans': CHOICE_OPTIONS})


def DecideAction(cUser, sUser, data, action):
    """
    Handler insert / updates new response, also general feedback
    Returns nothing
    """
    # Checks QA or general response and responds accordingly
    if data['type'] == 'M':
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
    elif data['type'] == 'Q':
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
@eligible_360
@fb_eligible
def GetCurrentYearQuestions(request):
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
    if 'selectedUser' in request.session:
        selectedUser = User.objects.get(pk=request.session['selectedUser'])
        groupObj = GetGroupInfo()
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


def GetGroupInfo():
    """
    Handler returns current year's group obj
    which is ordered by priority seq. given by admin
    """
    return Group.objects.filter(fb__year=date.today().year).order_by('priority')


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
@eligible_360
@fb_eligible
def GetMyRequesteesList(request):
    """
    Handler returns list of requestees who wants
    feedback from Me, with their names
    """
    l = []
    # Getting Manager's Request
    mgrReqObj = ManagerRequest.objects.filter(
        respondent=request.user,
        status=STATUS[1][0]
    )
    if len(mgrReqObj):
        l.append(ConstructUserInfo(request, request.user.employee.manager.user))
    # Getting requests from whom i got connect request
    peerObj = Peer.objects.filter(employee=request.user, status=STATUS[1][0])
    empPeerObj = EmpPeer.objects.filter(
        id__in=[eachPeerObj.emppeer.id for eachPeerObj in peerObj]
    )
    for eachObj in empPeerObj:
        l.append(ConstructUserInfo(request, eachObj.employee))
    # Getting requests to whom i sent connect request
    empPeerObj = EmpPeer.objects.filter(employee=request.user)
    peerObj = Peer.objects.filter(
        emppeer__in=[eachEmpPeerObj for eachEmpPeerObj in empPeerObj],
        status=STATUS[1][0]
    )
    for eachObj in peerObj:
        l.append(ConstructUserInfo(request, eachObj.employee))
    return l


@login_required
def ConstructUserInfo(request, cUser):
    """
    Handler returns a dict of user's full name, id,
    and remaining questions count
    Return Type
        {'name': USER_FULL_NAME, 'id': USER_ID, QCount': QST_COUNT}
    """
    d = {}
    d['name'] = fb360.views.GetUserFullName(cUser)
    d['id'] = cUser.id
    d['QCount'] = GetQuestionRemainingCount(request, cUser)
    return d


@login_required
def GetQuestionRemainingCount(request, cUser):
    """
    Handler to get number question remaining to answer for
    requestee
    Returns
        Total number of question's count for current year
        if no answer is recorded.
        Else Remaining questions's count will be returned.
    """
    QuestionYear = Question.objects.filter(
        group__fb__year=date.today().year
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
            respondent=request.user
        )
        if len([eachResp.submitted for eachResp in totalResp]):
            if [eachResp.submitted for eachResp in totalResp][0]:
                return -1
            else:
                # General Feedback
                totalQResp = QualitativeResponse.objects.filter(
                    employee=cUser,
                    respondent=request.user
                )
                return (len(totalQuestionYear)) - \
                    (len(totalResp) + len(totalQResp))
        else:
            # General Feedback
            totalQResp = QualitativeResponse.objects.filter(
                employee=cUser,
                respondent=request.user
            )
            return (len(totalQuestionYear)) - \
                (len(totalResp) + len(totalQResp))
    else:
        return 0
