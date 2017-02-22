from ExitApp.models import ResignationInfo, EmployeeClearanceInfo
from django.contrib.auth.models import User
from datetime import date, timedelta, datetime
from django.core.management.base import BaseCommand
import logging
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from Leave.tasks import leaveTypeDictionary

logger = logging.getLogger('MyANSRSource')


class Command(BaseCommand):
    help = 'Send Email for Resigned candidate.'

    def handle(self, *args, **options):
        sendemailresignedcandidate()


def sendemailresignedcandidate():
    print str(datetime.now()) + " short attendance auto apply started running"
    duedate = date.today() - timedelta(days=1)
    d = date.today()
    final_val = d + timedelta(days=1)
    candidatelist = ResignationInfo.objects.filter(last_date_accepted=final_val)
    for attendance in candidatelist:
        send_mail(attendance)
        print "leave saved for {0}".format(attendance.user)
    print str(datetime.now()) + " Email sending for resigned candidate "\
                                + str(len(candidatelist))


def send_mail(user):
    msg_html = render_to_string('email_templates/resingedcandidateemail.html',
                                {'registered_by': user.first_name,
                                 })

    mail_obj = EmailMessage('Your Last Date',
                            msg_html, settings.EMAIL_HOST_USER, [user.email],
                            cc=[])

    mail_obj.content_subtype = 'html'
    email_status = mail_obj.send()
    if email_status == 0:
        logger.error(
            "Unable To send Mail To The Authorities For"
            "The Following Leave Applicant : Date time : ")
        return "failed"
    else:
        logger.debug('send successful')