# Log file management
import logging
logger = logging.getLogger('MyANSRSource')

# FB360 models import
from .models import EmpPeer, Peer, ManagerRequest, STATUS

# Miscellaneous imports
from django.shortcuts import render
from django.db.models import Q
from django.contrib.auth.models import User

# Exception handlers import
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist

# Decorator imports
from django.contrib.auth.decorators import login_required
from .fb360eligible import eligible_360
from .fbeligible import fb_eligible


@login_required
@eligible_360
@fb_eligible
def MyFBRequestees(request):
    """
    Handler shows list of requestees who wants
    feedback from Me
    Also supports to choose a requestee to give feedback
    """
    mgrReqObj = ManagerRequest.objects.filter(
        respondent=request.user,
        status=STATUS[1][0]
    )
    peerObj = Peer.objects.filter(employee=request.user, status=STATUS[1][0])
    empPeerObj = Peer.objects.filter(employee=request.user, status=STATUS[1][0])
    return render(request, 'fb360FeedbackRequestee.html', {})
