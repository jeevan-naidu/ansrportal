from django.core.management.base import BaseCommand
import logging
import os
import csv
from django.db import IntegrityError
from CompanyMaster.models import BusinessUnit
from MyANSRSource.models import Project

logger = logging.getLogger('MyANSRSource')
FEED_DIR = "/www/MyANSRSource/ansr-timesheet/backup/"
FEED_EXT = "csv"
FEED_SUCCESS_DIR = os.path.join(FEED_DIR, "completed")
FEED_ERROR_DIR = os.path.join(FEED_DIR, "error")
FEED_DELIMITER = ","
FILE = "project_BU.csv"
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
        bu_unit = row[1].upper()
        bu = BusinessUnit.objects.filter(name=bu_unit)
        project = Project.objects.get(projectId=row[0])
        if bu:
            project.bu = bu[0]
            project.save()
            print "project {0} now set to bu {1}".format(row[0], bu[0])

    except Exception as E:
        print "inconsistent data {0} for project {1} bussiness unit {2}".format(E, row[0], row[1])


