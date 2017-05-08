from django.core.management.base import BaseCommand
import logging
import os
import csv
from django.db import IntegrityError
from MyANSRSource.models import ProjectDetail

logger = logging.getLogger('MyANSRSource')
FEED_DIR = "/www/MyANSRSource/ansr-timesheet/backup/Access-Control-Data/"
FEED_EXT = "csv"
FEED_SUCCESS_DIR = os.path.join(FEED_DIR, "completed")
FEED_ERROR_DIR = os.path.join(FEED_DIR, "error")
FEED_DELIMITER = ","
FILE = "dm_port.csv"
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
            logger.error(u"Manager data is incorrect for row {0} error {1}".format(row, error))



def insert_into_db(row):
    try:
        project_detail, created = ProjectDetail.objects.get_or_create(project_id=row[0],
                                                                      deliveryManager_id=row[1])

    except IntegrityError:
        raise IntegrityError("Incositent data")


