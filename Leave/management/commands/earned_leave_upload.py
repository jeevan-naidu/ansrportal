import logging
import os
import glob
import csv
from datetime import datetime
from django.utils.timezone import get_default_timezone
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from django.conf import settings
import re
from employee.models import Employee
from django.core.exceptions import PermissionDenied
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
                    with open(FEED_DIR+'earned.csv', 'r') as csvfile:
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
        columns_list = ['emp_id', 'name', 'earned_leave']
        user_obj = Employee.objects.get(employee_assigned_id=int(data_file[0]))
        if user_obj.user:
            for i in range(2,3):
                leave_type_obj = LeaveType.objects.get(leave_type=columns_list[i])
                obj, created = LeaveSummary.objects.get_or_create(user=user_obj.user, leave_type=leave_type_obj, year = '2015')
                value = data_file[i]
                if not value:
                    value = "0.0"

                obj.balance = value
                obj.applied = "0.0"
                obj.approved = "0.0"
                obj.year = "2015"
                obj.save()


    except:
        print "Emp id not found: " + str(data_file[0])
