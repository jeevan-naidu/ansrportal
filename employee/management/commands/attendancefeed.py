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
from django.db import IntegrityError

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

                        print "Processing backup file {0}".format(eachFile)

                        # Validate data and insert to db
                        feedData(filereader, eachFile)

                        print "Processed backup file {0}".format(eachFile)

                        # Move backed up feed to a new folder
                        if os.path.exists(SUCCESS_DIR) is False:
                            os.system('mkdir {0}'.format(SUCCESS_DIR))

                        os.system('mv {0} {1}'.format(eachFile,
                                                      SUCCESS_DIR))
            else:
                print "No more files to backup"
        else:
            # No Such backup folder found
            print "No Backup folder found"
            logger.info("No Backup folder named {0} found").format(BK_DIR)


def feedData(filereader, filename):

    row = 0

    for eachRow in filereader:

        row += 1

        if row % 10 == 0:
            print "Processed {0} records".format(row)

        # Converting data to relevant types
        try:
            attdate = datetime.strptime(eachRow[1],
                                        '%d-%m-%Y').date()
        except ValueError:
            logger.error("Date field failed for Emp.ID: {0}\
                         in {1} file ".format(eachRow[0]), filename)

        try:
            # Converting string to datetime object if time is given
            if eachRow[2]:
                intime = datetime.strptime(eachRow[2],
                                           '%H:%M:%S').time()
                swipe_in = datetime.combine(attdate, intime)
        except ValueError:
            logger.error("Intime field failed for Emp.ID: {0}\
                         in {1} file ".format(eachRow[0]), filename)

        try:
            if eachRow[3]:
                outtime = datetime.strptime(eachRow[3],
                                            '%H:%M:%S').time()

                swipe_out = datetime.combine(attdate, outtime)
        except ValueError:
            logger.error("Outtime field failed for Emp.ID: {0}\
                         in {1} file ".format(eachRow[0]), filename)

        try:
            # Insert appropriate data in db
            insertToDb(eachRow[0], attdate, swipe_in, swipe_out, filename)

        # To handle the unique key exception
        except IntegrityError:
            logger.exception("Duplicate record for Emp.ID: {0}\
                             in {1} file ".format(eachRow[0]), filename)
            pass


def insertToDb(employee, attdate, swipe_in, swipe_out, filename):

        # Getting employee object
        try:
            employee = Employee.objects.get(
                employee_assigned_id=employee)

        # Handler for null values in employee id
        except Employee.DoesNotExist:
            employee = None
            logger.exception("Emp.ID: {0} in {1} file does not exist".format(
                employee, filename))

        # Inserting attendance record to db
        try:
            att = Attendance()
            att.employee = employee
            att.attdate = attdate
            att.swipe_in = swipe_in.replace(tzinfo=utc)
            att.swipe_out = swipe_out.replace(tzinfo=utc)
            att.save()

        # To catch any validation errors if any
        except ValidationError:
            logger.error("Validation Error for \
                         employee {0} in {1} file".format(employee, filename)
                         )
