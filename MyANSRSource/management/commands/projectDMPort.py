from django.core.management.base import BaseCommand
import logging
import os
import csv
from django.db import IntegrityError
from django.contrib.auth.models import User
from MyANSRSource.models import ProjectDetail, Project

logger = logging.getLogger('MyANSRSource')
FEED_DIR = "/home/vivekpradhan/Downloads/"
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
        delivery_manager_users = row[1].split(",")
        delivery_manager_user_name = delivery_manager_users[0] if delivery_manager_users else ""
        user = User.objects.filter(username__contains=delivery_manager_user_name)
        project = Project.objects.filter(projectId=row[0])
        if user and project:
            project_detail, created = ProjectDetail.objects.get_or_create(project=project[0])
            project_detail.deliveryManager = user[0]
            project_detail.save()

            if created:
                print "project {0} created having delivery manager {1}".format(project_detail.project, user[0])
            else:
                print "project {0} changed delivery manager {1}".format(project_detail.project, user[0])
        else:
            if user:
                print "project not avaliable {0}".format(row)
            else:
                print "user not avalibale {0}".format(row)

    except IntegrityError:
        raise IntegrityError("Incositent data")


