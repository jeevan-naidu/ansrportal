from django.core.management.base import BaseCommand
import logging
import os
import csv
from django.db import IntegrityError
from employee.models import Employee
from CompanyMaster.models import BusinessUnit

logger = logging.getLogger('MyANSRSource')
FEED_DIR = "/www/MyANSRSource/ansr-timesheet/backup/"
FEED_EXT = "csv"
FEED_SUCCESS_DIR = os.path.join(FEED_DIR, "completed")
FEED_ERROR_DIR = os.path.join(FEED_DIR, "error")
FEED_DELIMITER = ","
FILE = "bu_update.csv"
class Command(BaseCommand):
    help = "upload delivery manager for existing project"

    def handle(self, *args, **kwargs):
        if os.path.exists(FEED_DIR):
            with open(FEED_DIR + FILE, 'r') as csvfile:
                filereader = csv.reader(
                    csvfile,
                    delimiter=FEED_DELIMITER
                )
                feed_data(filereader)
        else:
            logger.error(u"Directory {0} missing.".format(FEED_DIR))


def feed_data(filereader):

    for row in filereader:
        try:
            insert_into_db(row)
        except IntegrityError as error:
            logger.error(u"Manger data is incorrect for row {0} error {1}".format(row, error))


def insert_into_db(row):
    try:
        employees = Employee.objects.filter(employee_assigned_id=row[0])
        employee_detail = employees[0] if employees else ''
        if row[1] and employee_detail:
            bu = BusinessUnit.objects.filter(name__contains=row[1])
            if bu:
                employee_detail.business_unit = bu[0]
                employee_detail.save()

    except IntegrityError:
        raise IntegrityError("InConsistent data")


