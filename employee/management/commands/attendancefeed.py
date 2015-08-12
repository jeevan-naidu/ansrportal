import logging
import os
import glob
import csv
from datetime import datetime
from django.utils.timezone import get_default_timezone
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from employee.models import Attendance, Employee
from django.db import IntegrityError
from django.conf import settings

logger = logging.getLogger('employee')


class Command(BaseCommand):
    help = 'Upload daily attendance data into the system.'

    def handle(self, *args, **options):
        if os.path.exists(settings.FEED_DIR):
            file_pattern = "/*.{0}".format(settings.FEED_EXT)

            if glob.glob(settings.FEED_DIR + file_pattern):

                # Reading each file and pushing record to db
                for eachFile in glob.glob(settings.FEED_DIR + file_pattern):
                    with open(eachFile, 'r') as csvfile:
                        filereader = csv.reader(csvfile,
                                                delimiter=settings.FEED_DELIMITER)

                        logger.info(
                            "Processing file {0}".format(eachFile))

                        # Validate data and insert to db
                        if len(args) and args[0]:
                            everyRec = int(args[0])
                        else:
                            everyRec = 10

                        feedData(filereader, eachFile, everyRec)

                        logger.info("Processed file {0}".format(eachFile))

                        # Move backed up feed to a new folder
                        if os.path.exists(settings.FEED_SUCCESS_DIR) is False:
                            os.system('mkdir {0}'.format(
                                settings.FEED_SUCCESS_DIR))

                        os.system('mv {0} {1}'.format(eachFile,
                                                      settings.FEED_SUCCESS_DIR))
                        logger.info(
                            "Moved file {0} to processed directory".
                            format(eachFile))
            else:
                logger.info("No more files to process.")
        else:
            # No Such backup folder found
            logger.error("Directory {0} missing.".format(
                settings.FEED_DIR))


def checkRow(firstRow):
    if len(firstRow) > 4 or len(firstRow) == 0:
        return False
    else:
        return True


def feedData(filereader, filename, everyRec):

    row = 0

    for eachRow in filereader:
        row += 1
        swipe_in, swipe_out = '', ''

        if checkRow(eachRow):

            if row % everyRec == 0:
                print "Processed {0} records".format(row)

            # Converting data to relevant types
            try:
                attdate = datetime.strptime(eachRow[1],
                                            '%d-%m-%Y').date()
            except ValueError:
                attdate = ''
                logger.error("Attendance Date field data error: {0} |\
                             File: {1}  | Line # : {2}".format(eachRow, filename, row)
                             )

            try:
                # Converting string to datetime object if time is given
                if eachRow[2]:
                    intime = datetime.strptime(eachRow[2],
                                               '%H:%M:%S').time()
                    if attdate != '':
                        swipe_in = datetime.combine(attdate, intime)
                    else:
                        swipe_in = ''
            except ValueError:
                swipe_in = ''
                logger.error("In-time field data error: {0} |\
                             File: {1}  | Line # : {2}".format(eachRow, filename, row)
                             )

            try:
                if eachRow[3]:
                    outtime = datetime.strptime(eachRow[3],
                                                '%H:%M:%S').time()

                    if attdate != '':
                        swipe_out = datetime.combine(attdate, outtime)
                    else:
                        swipe_out = ''
            except ValueError:
                swipe_out = ''
                logger.error("Out-time field data error: {0} |\
                             File: {1}  | Line # : {2}".format(eachRow, filename, row)
                             )

            try:
                # Insert appropriate data in db
                insertToDb(
                    eachRow[0],
                    attdate,
                    swipe_in,
                    swipe_out,
                    filename,
                    row)

            # To handle the unique key exception
            except IntegrityError:
                logger.error("Intime field error in data : {0} |\
                             File: {1}  | Line # : {2}".
                             format(eachRow, filename, row)
                             )
        else:
            logger.error("{0} is corrupted on line {1}".format(filename, row))
            break


def insertToDb(employee, attdate, swipe_in, swipe_out, filename, row):

        # Getting employee object
    try:
        emp = Employee.objects.get(employee_assigned_id=employee)

    # Handler for null values in employee id
    except Employee.DoesNotExist:
        emp = None
        logger.error(
            "Emp.ID: {0} Not in myansrsource system. \
            Found in file : {1} | line {2}".format(
            employee,
            filename,
            row))

    # Inserting attendance record to db
    try:
        att = Attendance()
        att.incoming_employee_id = employee
        att.employee = emp
        if attdate != '':
            att.attdate = attdate
            if swipe_in != '':
                att.swipe_in = swipe_in.replace(tzinfo=get_default_timezone())
            if swipe_out != '':
                att.swipe_out = swipe_out.replace(tzinfo=get_default_timezone())
        att.save()

    # To catch any validation errors if any
    except ValidationError as e:
        logger.error("Validation Error {2} processing \
                     employee {0} in {1}  | Line #: {3}".
                     format(employee, filename, e, row)
                     )
