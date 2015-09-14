# Log file management
import logging
logger = logging.getLogger('MyANSRSource')

# FB360 models and forms import
from .forms import PeerForm
from .models import EmpPeer, Peer, FB360, ManagerRequest, STATUS

# Employee model import
import employee

# Miscellaneous imports
from django.shortcuts import render
from django.db.models import Q
from django.contrib.auth.models import User
from datetime import date

# Exception handlers import
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist

# Decorator imports
from django.contrib.auth.decorators import login_required
from .fb360eligible import eligible_360
from .ismanager import is_manager


@login_required
@eligible_360
def PeerRequest(request):
    """
    Handler to show list of peers along with thier status.
    Also support ability to add a new peer.
    Status types -> Pending, Approved, Rejected
    """
    if request.method == 'POST':
        acceptedForm = PeerForm(request.POST)
        if acceptedForm.is_valid():
            empPeerObj = EmpPeer()
            empPeerObj.employee = request.user
            try:
                empPeerObj.save()
            except IntegrityError:
                empPeerObj = EmpPeer.objects.get(employee=request.user)
            for eachPeer in acceptedForm.cleaned_data['peer']:
                if IsPeerEligible(request, eachPeer, empPeerObj) and \
                        IsPeerRequestExist(request, eachPeer, empPeerObj):
                    peerObj = Peer()
                    peerObj.employee = eachPeer
                    peerObj.emppeer = empPeerObj
                    peerObj.save()
    return render(request, 'fb360SelectPeer.html',
                  {'form': PeerForm(), 'data': GetMyPeerList(request),
                   'request_eligible': IsPageActionEligible('Request')})


@login_required
@eligible_360
def GetMyPeerList(request):
    """
    Handler sends back peer list for logged in user.
    Returns user's employee Id, firstname, lastname, email id and status
    """
    myObj = EmpPeer.objects.filter(
        employee=request.user
    )
    myObjAccepted = Peer.objects.filter(~Q(status=STATUS[3][0]),
                                        employee=request.user)
    if myObj or myObjAccepted:
        myPeerObj = Peer.objects.filter(~Q(status=STATUS[3][0]), emppeer=myObj)
        if myPeerObj or myObjAccepted:
            list1 = ConstructList(request, myPeerObj)
            list2 = ConstructList(request,
                                  [eachObj.emppeer
                                   for eachObj in myObjAccepted])
            return list1 + list2
        else:
            return None
    else:
        return None


@login_required
@eligible_360
def IsPeerEligible(request, eachPeer, empPeerObj):
    """
    Handler checks the current peer is eligible to be added or not.
    Eligible Criteria:
        Peer must not be None.
        Peer must not be already added to this employee in Approved / Pending
        state.
        Peer cannot be self assigned.
        Peer cannot be my manager.
        If i am a manager, i can't add my reportee as peer
        Peer must be FB360 eligible.
    Returns 0 -> Not Eligible or  1 -> Is Eligible
    """
    if eachPeer is not None:
        if eachPeer != request.user:
            try:
                if eachPeer.employee.is_360eligible:
                    if request.user.employee.manager != eachPeer:
                        myPeerObj = Peer.objects.filter(
                            employee=eachPeer,
                            emppeer=empPeerObj,
                        )
                        if myPeerObj:
                            if myPeerObj.filter(status__in=(STATUS[3][0],
                                                            STATUS[2][0])):
                                UpdateRequestStatus(myPeerObj[0], STATUS[0][0])
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
                else:
                    return 0
            except ObjectDoesNotExist:
                return 0
        else:
            return 0
    else:
        return 0


@login_required
@eligible_360
def IsPeerRequestExist(request, eachPeer, empPeerObj):
    """
    Handler checks the current peer has requested me
    Returns 0 -> Not Eligible or  1 -> Is Eligible
    """
    req = Peer.objects.filter(employee=request.user).values('emppeer__employee')
    if eachPeer.id in [eachReq['emppeer__employee'] for eachReq in req]:
        return 0
    else:
        return 1


@login_required
@eligible_360
def RequestAction(request):
    """
    Handler to approve / Reject peer, manager requests
    """
    if request.method == 'POST':
        for i in range(1, int(request.POST.get('totalValue')) + 1):
            choice = "choice" + str(i)
            rowid = "rowid" + str(i)
            if 'mgrChoice' in request.POST:
                myManagerObj = ManagerRequest.objects.get(
                    respondent=request.user
                )
                UpdateRequestStatus(myManagerObj, request.POST.get('mgrChoice'))
            if choice in request.POST:
                myPeerObj = Peer.objects.get(
                    id=int(request.POST.get(rowid))
                )
                UpdateRequestStatus(myPeerObj, request.POST.get(choice))
    return render(request, 'fb360RequestAction.html',
                  {'data': [GetPeerRequest(request),
                            GetMyManagerRequest(request)
                            ],
                   'accept_eligible': IsPageActionEligible('Accept')})


@login_required
@eligible_360
@is_manager
def ChooseReportee(request):
    """
    Handler to choose my reportee(s) to get feedback
    """
    if request.method == 'POST':
        for i in range(1, int(request.POST.get('totalValue')) + 1):
            choice = "choice" + str(i)
            rowid = "rowid" + str(i)
            if request.POST.get(choice) is not None:
                try:
                    mgrReqObj = ManagerRequest()
                    mgrReqObj.respondent = User.objects.get(
                        pk=int(request.POST.get(rowid))
                    )
                    mgrReqObj.status = STATUS[0][0]
                    mgrReqObj.save()
                except IntegrityError:
                    mgrReqObj = ManagerRequest.objects.get(
                        respondent__id=int(request.POST.get(rowid))
                    )
                    UpdateRequestStatus(mgrReqObj, STATUS[0][0])
    return render(request, 'fb360ChooseReportee.html',
                  {'data': [
                      GetMyReporteeList(request),
                      GetMyReporteeFeedbackList(request)
                  ],
                      'choose_eligible': IsPageActionEligible('Choose')})


def IsPageActionEligible(action):
    """
    Handler to check today is in peer / feedback / reportee
    date ranges or not
    Returns True -> If in range, False -> If not in range
            None -> If there is no FB object
    """
    fbObj = FB360.objects.filter(year=date.today().year)
    if fbObj:
        if action == 'Accept':
            return (fbObj[0].approval_date >= date.today() and
                    fbObj[0].selection_start_date <= date.today())
        elif action == 'Request' or action == 'Choose':
            return (fbObj[0].selection_date >= date.today() and
                    fbObj[0].selection_start_date <= date.today())
    else:
        return None


@login_required
@eligible_360
def GetPeerRequest(request):
    """
    Returns List of peer requests.
    """
    myRequests = Peer.objects.filter(employee=request.user,
                                     status=STATUS[0][0])
    if myRequests:
        return ConstructList(request,
                             [eachReq.emppeer for eachReq in myRequests])
    else:
        return None


@login_required
@eligible_360
def ConstructList(request, myObj):
    """
    Handler to contruct basic employee information.
    Returns List from object with employee name, email ID, status
    """
    myPeerList = []
    for eachObj in myObj:
        myPeerInfo = {}
        myPeerInfo['name'] = GetUserFullName(eachObj.employee)
        myPeerInfo['emailid'] = eachObj.employee.email
        try:
            myPeerInfo['status'] = eachObj.status
        except AttributeError:
            pass
        if 'status' in myPeerInfo:
            myPeerInfo['id'] = eachObj.id
        else:
            peerObj = Peer.objects.get(employee=request.user, emppeer=eachObj)
            myPeerInfo['id'] = peerObj.id
            if peerObj.status == STATUS[1][0]:
                myPeerInfo['status'] = peerObj.status
        myPeerList.append(myPeerInfo)
    return myPeerList


@login_required
@eligible_360
def GetMyManagerRequest(request):
    """
    Handler sends back my manager request for feedback
    Returns True if a request is in place,
            False if i have no manager / no request from my manager
    """
    try:
        mgrReq = ManagerRequest.objects.filter(respondent=request.user)
        if len(mgrReq):
            return [True, mgrReq[0].status]
        else:
            return [False, None]
    except AttributeError:
        return [False, None]


def UpdateRequestStatus(obj, status):
    """
    Handler updates request status.
    Requests will be from peer / manager.
    Returns Nothing.
    """
    if status is not None:
        obj.status = status
        obj.save()


@login_required
@eligible_360
@is_manager
def GetMyReporteeFeedbackList(request):
    """
    Handler returns requested and approved list of reportees with
    first name, last name, email and employee ID along with thier status
    """
    myFBReportees = employee.models.Employee.objects.filter(
        manager=request.user.employee)
    myFBReporteesId = [eachReportee.user.id for eachReportee in myFBReportees]
    myFBReporteesStatus = ManagerRequest.objects.filter(
        respondent__in=myFBReporteesId,
        status__in=[STATUS[1][0], STATUS[0][0]]
    )
    l = []
    for eachReporteeStatus in myFBReporteesStatus:
        d = {}
        d['name'] = GetUserFullName(eachReporteeStatus.respondent)
        d['emailid'] = eachReporteeStatus.respondent.email
        d['status'] = eachReporteeStatus.status
        l.append(d)
    return l


@login_required
@eligible_360
@is_manager
def GetMyReporteeList(request):
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
    mgrReq = ManagerRequest.objects.all()
    requestId = [eachReq.respondent.id for eachReq in mgrReq]
    reporteeId = [eachReportee.user.id for eachReportee in myReportees]
    # Union of requestId and reporteeId
    reqExist = list(set(requestId) & set(reporteeId))
    if len(reqExist):
        # Removes reporteeId whose request already exist
        finalList = list(set(reporteeId) - set(reqExist))
    else:
        finalList = reporteeId
    # Picking eligible re-requests respondent ids if any
    rejectedReq = ManagerRequest.objects.filter(
        respondent__employee__manager=request.user.employee,
        status=STATUS[2][0]
    )
    if len(rejectedReq):
        finalList = finalList + [eachReq.respondent.id
                                 for eachReq in rejectedReq]
    validReportees = User.objects.filter(id__in=finalList)
    l = []
    for eachValidReportee in validReportees:
        d = {}
        d['id'] = eachValidReportee.id
        d['name'] = GetUserFullName(eachValidReportee)
        d['emailid'] = eachValidReportee.email
        l.append(d)
    return l


def GetUserFullName(cUser):
    """
    Handler returns user's full name
    Full Name format
        {FIRST_NAME} {LAST_NAME}{(EMPLOYEE_ID)}
    """
    return cUser.first_name + '  ' + \
        cUser.last_name + '(' + cUser.employee.employee_assigned_id + ')'
