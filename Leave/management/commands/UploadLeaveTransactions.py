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
FEED_DIR = "/home/vivekpradhan/csvdata"
FEED_EXT = "csv"
FEED_SUCCESS_DIR = os.path.join(FEED_DIR,  "completed")
FEED_ERROR_DIR = os.path.join(FEED_DIR,  "error")
FEED_DELIMITER = ","


class Command(BaseCommand):
    help = 'Upload Leave summary.'

    def handle(self, *args, **options):
        if os.path.exists(FEED_DIR):

            file_pattern = u"/*.{0}".format(FEED_EXT)

            if glob.glob(FEED_DIR + file_pattern):
                # Reading each file and pushing record to db
                for eachFile in glob.glob(FEED_DIR + file_pattern):
                    with open(eachFile, 'r') as csvfile:
                        filereader = csv.reader(
                            csvfile,
                            delimiter=FEED_DELIMITER)

                        logger.info(
                            u"Processing file {0}".format(eachFile))

                        feedData(filereader)

                        logger.info(u"Processed file {0}".format(eachFile))

                        # Move backed up feed to a new folder
                        if os.path.exists(FEED_SUCCESS_DIR) is False:
                            os.system(u'mkdir {0}'.format(
                                FEED_SUCCESS_DIR))

                        os.system(
                            u'mv {0} {1}'.format(
                                eachFile,
                                FEED_SUCCESS_DIR))
                        logger.info(
                            u"Moved file {0} to processed directory".
                            format(eachFile))
            else:
                logger.info("No more files to process.")
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
        columns_list = ['emp_id', 'name', 'bereavement_leave', 'casual_leave',
         'earned_leave', 'loss_of_pay', 'maternity_leave',
         'paternity_leave', 'pay_off', 'sick_leave', 'work_from_home', 'comp_off_earned', 'comp_off_avail', 'sabbatical']
        user_obj = Employee.objects.get(employee_assigned_id=int(data_file[0])).user
        if user_obj:
            for i in range(2,14):
                leave_type_obj = LeaveType.objects.get(leave_type=columns_list[i])
                obj, created = LeaveSummary.objects.get_or_create(user=user_obj, leave_type=leave_type_obj)
                value = data_file[i]
                if not value:
                    value = "0.0"
                if i==13:
                    value = "180.0"
                if i==6 and value:
                    value="84.0"

                obj.balance = value
                obj.applied = "0.0"
                obj.approved = "0.0"
                obj.year = "2016"
                obj.save()


    except:
        print "Emp id not found: " + str(data_file[0])
