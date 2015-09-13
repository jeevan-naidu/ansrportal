# Log file management
import logging
logger = logging.getLogger('MyANSRSource')

# FB360 models, views import
from .models import EmpPeer, Peer, ManagerRequest, Question, \
    Response, QualitativeResponse, STATUS
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
        for i in range(1, int(request.POST.get('totalValue')) + 1):
            qst = 'qId' + str(i)
            ans = 'choice' + str(i)
            data = {'qst': int(request.POST.get(qst)),
                    'ans': request.POST.get(ans)}
            DecideAction(request.user, int(request.session['selectedUser']),
                         data)
    return render(request, 'fb360FeedbackQA.html',
                  {'qst': GetCurrentYearQuestions(request),
                   'ans': CHOICE_OPTIONS})


def DecideAction(cUser, sUser, data):
    """
    Handler insert / updates new response, also general feedback
    return nothing
    """
    if len(data):
        resp = Response.objects.get(employee=sUser, respondent=cUser,
                                    qst__id=data['qst'])
    else:
        pass


@login_required
@eligible_360
@fb_eligible
def GetCurrentYearQuestions(request):
    """
    Handler returns list of question for chosen user
    Return Type
        {'qst': QST, 'qstId': ID}
    """
    selectedUser = User.objects.get(pk=request.session['selectedUser'])
    QuestionYear = Question.objects.filter(
        fb__year=date.today().year
    ).values('category', 'qst', 'id')
    l = []
    for eachCategory in QuestionYear:
        d = {}
        if eachCategory['category'] == selectedUser.employee.designation.id:
            d['qst'] = eachCategory['qst']
            d['qstId'] = eachCategory['id']
            l.append(d)
    return l


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
        fb__year=date.today().year
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
        # General Feedback
        totalQResp = QualitativeResponse.objects.filter(
            employee=cUser,
            respondent=request.user
        )
        return (len(totalQuestionYear) + 1) - (len(totalResp) + len(totalQResp))
    else:
        return 0
