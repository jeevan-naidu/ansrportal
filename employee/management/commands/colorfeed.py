import logging
import os
import csv
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from employee.models import Employee
from Leave.models import LeaveType, LeaveSummary

logger = logging.getLogger('MyANSRSource')
FEED_DIR = "/www/MyANSRSource/ansr-timesheet/backup/Access-Control-Data/"
FEED_EXT = "csv"
FEED_SUCCESS_DIR = os.path.join(FEED_DIR,  "completed")
FEED_ERROR_DIR = os.path.join(FEED_DIR,  "error")
FEED_DELIMITER = ","

class Command(BaseCommand):
    help = 'Upload Leave summary.'

    def handle(self, *args, **options):
        if os.path.exists(FEED_DIR):
                    with open(FEED_DIR+'color.csv', 'r') as csvfile:
                        filereader = csv.reader(
                            csvfile,
                            delimiter=FEED_DELIMITER)
                        feedData(filereader)

        else:
            # No Such backup folder found
            logger.error(u"Directory {0} missing.".format(
                FEED_DIR))


def feedData(filereader):

    for eachRow in filereader:
            try:
                # Insert appropriate data in db
                if eachRow:
                    insertToDb1(
                        eachRow
                        )

            # To handle the unique key exception
            except IntegrityError:
                logger.error(u"Intime field error in data : {0} |\
                             File: {1}  | Line # : {2}".
                             format(eachRow)
                             )

def insertToDb1(data_file):
    try:
        user_obj = Employee.objects.get(employee_assigned_id=int(data_file[0]))
        user_obj.color = data_file[1]
        user_obj.save()



    except:
        print "Emp id not found: " + str(data_file[0])
