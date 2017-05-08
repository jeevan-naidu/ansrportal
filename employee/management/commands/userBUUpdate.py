from django.core.management.base import BaseCommand
import logging
import os
import csv
from django.db import IntegrityError
from MyANSRSource.models import Employee

logger = logging.getLogger('MyANSRSource')
FEED_DIR = "/www/MyANSRSource/ansr-timesheet/backup/Access-Control-Data/"
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
        employee_detail, created = Employee.objects.get_or_create(user_id=row[0])
        employee_detail.business_unit_id = row[1]
        employee_detail.save()

    except IntegrityError:
        raise IntegrityError("InConsistent data")


