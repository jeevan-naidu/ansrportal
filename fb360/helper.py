# Miscellaneous imports
from datetime import date

# Decorator imports
from django.contrib.auth.decorators import login_required

# Import app models
from .models import Initiator, Respondent, STATUS, FB360


def IsPageActionEligible(action, fbObj):
    """
    Helper to check today is in peer / feedback / reportee / additional managers
    date ranges or not
    Returns True -> If in range, False -> If not in range
            None -> If there is no FB object
    """
    if fbObj:
        if action == 'Accept':
            return (fbObj.approval_date >= date.today() and
                    fbObj.start_date <= date.today())
        elif action == 'Request' or action == 'Choose':
            return (fbObj.selection_date >= date.today() and
                    fbObj.start_date <= date.today())
    else:
        return None


@login_required
def GetSurveyList(request, currentStatus):
    """
    Hepler returns survey list based on current Status given
    Returns List of survey objects, if there is no survey
            returns None
    """
    initIds = []
    if currentStatus == STATUS[1][0]:
        initid = Initiator.objects.filter(
            employee=request.user,
            survey__approval_date__lt=date.today()
        )
        myResp = Respondent.objects.filter(
            initiator__in=[eachId.id for eachId in initid],
            initiator__survey__approval_date__lt=date.today()
        ).values('initiator__survey').distinct()
        initIds = [eachResp['initiator__survey'] for eachResp in myResp]
        resp = Respondent.objects.filter(
            employee=request.user,
            status=currentStatus,
            initiator__survey__approval_date__lt=date.today()
        ).values('initiator__survey').distinct()
    else:
        resp = Respondent.objects.filter(
            employee=request.user,
            status=currentStatus
        ).values('initiator__survey').distinct()
    respIds = [eachResp['initiator__survey'] for eachResp in resp]
    surveyIds = respIds + initIds
    return FB360.objects.filter(id__in=surveyIds).order_by('end_date')


@login_required
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
            peerObj = Respondent.objects.get(employee=request.user,
                                             initiator=eachObj)
            myPeerInfo['id'] = peerObj.id
            if peerObj.status == STATUS[1][0]:
                myPeerInfo['status'] = peerObj.status
        myPeerList.append(myPeerInfo)
    return myPeerList


def UpdateRequestStatus(obj, status):
    """
    Handler updates request status.
    Requests will be from peer / manager.
    Returns Nothing.
    """
    if status is not None:
        obj.status = status
        obj.save()


def GetUserFullName(cUser):
    """
    Handler returns user's full name
    Full Name format
        {FIRST_NAME} {LAST_NAME}{(EMPLOYEE_ID)}
    """
    return cUser.first_name + '  ' + \
        cUser.last_name + '(' + cUser.employee.employee_assigned_id + ')'
