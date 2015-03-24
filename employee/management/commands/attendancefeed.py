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
from django.conf import settings


class Command(BaseCommand):
    help = 'Pull Attendance to DB'

    def handle(self, *args, **options):
        if os.path.exists(settings.BK_DIR):
            file_pattern = "/*.{0}".format(settings.EXT)

            if glob.glob(settings.BK_DIR + file_pattern):

                # Reading each file and pushing record to db
                for eachFile in glob.glob(settings.BK_DIR + file_pattern):
                    with open(eachFile, 'r') as csvfile:
                        filereader = csv.reader(csvfile,
                                                delimiter=settings.DELIMITER)

                        print "Processing backup file {0}".format(eachFile)

                        # Validate data and insert to db
                        if len(args) and args[0]:
                            everyRec = args[0]
                        else:
                            everyRec = 10

                        feedData(filereader, eachFile, everyRec)

                        print "Processed backup file {0}".format(eachFile)

                        # Move backed up feed to a new folder
                        if os.path.exists(settings.SUCCESS_DIR) is False:
                            os.system('mkdir {0}'.format(
                                settings.SUCCESS_DIR))

                        os.system('mv {0} {1}'.format(eachFile,
                                                        settings.SUCCESS_DIR))
            else:
                print "No more files to backup"
        else:
            # No Such backup folder found
            print "No Backup folder found"
            logger.info("No Backup folder named {0} found").format(
                settings.BK_DIR)


def checkRow(firstRow):
    if len(firstRow) > 4:
        return False
    else:
        return True


def feedData(filereader, filename, everyRec):

    row = 0

    for eachRow in filereader:
        row += 1

        if checkRow(eachRow):

            if row == everyRec:
                print "Processed {0} records".format(row)

            # Converting data to relevant types
            try:
                attdate = datetime.strptime(eachRow[1],
                                            '%d-%m-%Y').date()
            except ValueError:
                logger.error("Date field failed for Emp.ID: {0}\
                            in {1} ".format(eachRow[0], filename)
                            )

            try:
                # Converting string to datetime object if time is given
                if eachRow[2]:
                    intime = datetime.strptime(eachRow[2],
                                            '%H:%M:%S').time()
                    swipe_in = datetime.combine(attdate, intime)
            except ValueError:
                logger.error("Intime field failed for Emp.ID: {0}\
                            in {1} ".format(eachRow[0], filename)
                            )

            try:
                if eachRow[3]:
                    outtime = datetime.strptime(eachRow[3],
                                                '%H:%M:%S').time()

                    swipe_out = datetime.combine(attdate, outtime)
            except ValueError:
                logger.error("Outtime field failed for Emp.ID: {0}\
                            in {1} ".format(eachRow[0], filename)
                            )

            try:
                # Insert appropriate data in db
                insertToDb(eachRow[0], attdate, swipe_in, swipe_out, filename)

            # To handle the unique key exception
            except IntegrityError:
                logger.error("Duplicate record for Emp.ID: {0}\
                                in {1}".format(eachRow[0], filename)
                            )
                pass
        else:
            print "{0} is corrupted".format(filename)
            logger.error("{0} is corrupted".format(filename))
            break


def insertToDb(employee, attdate, swipe_in, swipe_out, filename):

        # Getting employee object
    try:
        emp = Employee.objects.get(employee_assigned_id=employee)

    # Handler for null values in employee id
    except Employee.DoesNotExist:
        emp = None
        logger.error("Emp.ID: {0} in {1} does not exist".format(
            employee, filename))
        pass

    # Inserting attendance record to db
    try:
        att = Attendance()
        att.employee = emp
        att.attdate = attdate
        att.swipe_in = swipe_in.replace(tzinfo=utc)
        att.swipe_out = swipe_out.replace(tzinfo=utc)
        att.save()

    # To catch any validation errors if any
    except ValidationError:
        logger.error("Validation Error for \
                         employee {0} in {1} ".format(employee, filename)
                     )
