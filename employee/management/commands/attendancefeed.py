import logging
logger = logging.getLogger('employee')
import os
import glob
import csv
from datetime import datetime
from django.utils.timezone import utc
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from employee.models import Attendance, Employee

# Backup folder and extension settings
BK_DIR = "backup/Access-Control-Data"
EXT = "csv"
SUCCESS_DIR = BK_DIR + "/completed"
DELIMITER = ","


class Command(BaseCommand):
    help = 'Pull Attendance to DB'

    def handle(self, *args, **options):
        if os.path.exists(BK_DIR):
            file_pattern = "/*.{0}".format(EXT)

            if glob.glob(BK_DIR + file_pattern):

                # Reading each file and pushing record to db
                for eachFile in glob.glob(BK_DIR + file_pattern):
                    with open(eachFile, 'r') as csvfile:
                        filereader = csv.reader(csvfile, delimiter=DELIMITER)

                        # Validate data and insert to db
                        feedData(filereader)

                        # Move backed up feed to a new folder
                        if os.path.exists(SUCCESS_DIR) is False:
                            os.system('mkdir {0}'.format(SUCCESS_DIR))

                        os.system('mv {0} {1}'.format(eachFile,
                                                      SUCCESS_DIR))
            else:
                logger.exception("No more files to backup")
        else:
            # No Such backup folder found
            logger.exception("No Backup folder found")


def feedData(filereader):

    for eachRow in filereader:

        # Converting data to relevant types
        try:
            attdate = datetime.strptime(eachRow[1],
                                        '%d-%m-%Y').date()

            # Converting string to datetime object if time is given
            if eachRow[2]:
                intime = datetime.strptime(eachRow[2],
                                           '%H:%M:%S').time()
                swipe_in = datetime.combine(attdate, intime)

            if eachRow[3]:
                outtime = datetime.strptime(eachRow[3],
                                            '%H:%M:%S').time()

                swipe_out = datetime.combine(attdate, outtime)

            # Insert appropriate data in db
            insertToDb(eachRow[0], attdate, swipe_in, swipe_out)

        # To catch any error in values if any
        except ValueError as e:
            logger.exception(e)


def insertToDb(employee, attdate, swipe_in, swipe_out):

        # Getting employee object
        try:
            employee = Employee.objects.get(
                employee_assigned_id=employee)

        # Handler for null values in employee id
        except Employee.DoesNotExist:
            employee = None

        # Inserting attendance record to db
        try:
            att = Attendance()
            att.employee = employee
            att.attdate = attdate
            att.swipe_in = swipe_in.replace(tzinfo=utc)
            att.swipe_out = swipe_out.replace(tzinfo=utc)
            att.save()

        # To catch any validation errors if any
        except ValidationError as e:
            logger.exception(e)
