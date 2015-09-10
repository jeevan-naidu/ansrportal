import logging
logger = logging.getLogger('MyANSRSource')

from .forms import PeerForm
from .models import EmpPeer, Peer, FB360, ManagerRequest
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from .fb360eligible import eligible_360
from datetime import date


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
    myObjAccepted = Peer.objects.filter(~Q(status='D'),
                                        employee=request.user)
    if myObj or myObjAccepted:
        myPeerObj = Peer.objects.filter(~Q(status='D'), emppeer=myObj)
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
                            if myPeerObj.filter(status__in=('D', 'R')):
                                UpdatePeerStatus(myPeerObj[0], 'P')
                                return 0
                            else:
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
def PeerAccept(request):
    """
    Handler to approve peer
    """
    myApprovalList = [GetPeerRequest(request), GetMyManagerRequest(request)]
    if request.method == 'POST':
        for i in range(1, int(request.POST.get('totalValue')) + 1):
            choice = "choice" + str(i)
            rowid = "rowid" + str(i)
            myPeerObj = Peer.objects.get(
                id=int(request.POST.get(rowid))
            )
            UpdatePeerStatus(myPeerObj, request.POST.get(choice))
        myApprovalList = [GetPeerRequest(request), GetMyManagerRequest(request)]
    return render(request, 'fb360ApprovePeer.html',
                  {'data': myApprovalList,
                   'accept_eligible': IsPageActionEligible('Accept')})


def IsPageActionEligible(action):
    """
    Handler to check today is in peer / feedback date ranges or not
    Returns True -> If in range, False -> If not in range
            None -> If there is no FB object
    """
    fbObj = FB360.objects.filter(year=date.today().year)
    if fbObj:
        if action == 'Accept':
            return (fbObj[0].approval_date >= date.today() and
                    fbObj[0].selection_start_date <= date.today())
        elif action == 'Request':
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
                                     status='P')
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
        myPeerInfo['name'] = eachObj.employee.first_name + '  ' + \
            eachObj.employee.last_name + '(' + \
            eachObj.employee.employee.employee_assigned_id + ')'
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
            if peerObj.status == 'A':
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
    if request.user.manager:
        mgrReq = ManagerRequest.objects.filter(respondent=request.user)
        if len(mgrReq):
            return True
        else:
            return False
    else:
        return False


def UpdatePeerStatus(myPeerObj, status):
    """
    Handler updates peer's status.
    Returns Nothing.
    """
    if status is not None:
        myPeerObj.status = status
        myPeerObj.save()
