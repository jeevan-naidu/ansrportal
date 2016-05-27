from templated_email import send_templated_mail
from django.core.management.base import BaseCommand
from MyANSRSource.models import TimeSheetEntry, Report
from django.conf import settings
from smtplib import SMTPException
import logging
import os
from datetime import date, timedelta
logger = logging.getLogger('MyANSRSource')


class Command(BaseCommand):

    def handle(self, *args, **options):
        weekDay = date.today().weekday()
        wkStart = date.today() - timedelta(days=weekDay)
        wkEnd = date.today() + timedelta(days=6 - weekDay)
        newList = []
        pList = TimeSheetEntry.objects.filter(
            project__closed=False, project__endDate__lte=date.today(),
            wkstart=wkStart, wkend=wkEnd
        ).values('project__projectId', 'project__name').distinct()
        if len(pList):
            newList = [
                eachRec['project__projectId'] + ' : ' + eachRec['project__name'] for eachRec in pList
            ]
        if len(newList):
            toAddr = getReportNotifyDetails()
            if len(toAddr):
                content = {'data': newList}
                sendEmail('nonclosedprojectts', toAddr, content)


def getReportNotifyDetails():
    myName = os.path.basename(__file__).split(".")[0]
    reportDetails = Report.objects.filter(name=myName).values(
        'notify__email', 'freq', 'day', 'weekday'
    )
    if len(reportDetails):
        emailList = []
        for eachDetail in reportDetails:
            if eachDetail['freq'] == 'W':
                if int(eachDetail['weekday']) == date.today().weekday():
                    if eachDetail['notify__email'] != '':
                        emailList.append(eachDetail['notify__email'])
            else:
                if int(eachDetail['day']) == date.today().day:
                    if eachDetail['notify__email'] != '':
                        emailList.append(eachDetail['notify__email'])
        return emailList
    else:
        logger.error("No Report details found for {0}".format(myName))
        return []


def sendEmail(template_name, toAddr, content):
    try:
        send_templated_mail(
            template_name=template_name,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=toAddr,
            context=content
        )
    except SMTPException as e:
        logger.error(str(e))
