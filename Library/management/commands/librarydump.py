import logging
import os
import csv
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from Library.models import Book, Author, LendPeriods, Publisher

logger = logging.getLogger('MyANSRSource')
FEED_DIR = "/www/MyANSRSource/ansr-timesheet/backup/Access-Control-Data/"
FEED_EXT = "csv"
FEED_SUCCESS_DIR = os.path.join(FEED_DIR,  "completed")
FEED_ERROR_DIR = os.path.join(FEED_DIR,  "error")
FEED_DELIMITER = ","


class Command(BaseCommand):
    help = 'Upload Leave summary.'

    def handle(self, *args, **options):
        if os.path.exists(FEED_DIR):
                    with open(FEED_DIR+'library.csv', 'r') as csvfile:
                        filereader = csv.reader(
                            csvfile,
                            delimiter=FEED_DELIMITER)
                        feedData(filereader)

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
            authorname = data_file[1]
            authorname = authorname.split(" ")
            first_name = authorname[0]
            surname = authorname[1:]
            if surname:
                surname = reduce(lambda x, y: x + " " + y, surname)
            else:
                surname = ""

            author, created1 = Author.objects.get_or_create(name=first_name, surname=surname)
            publisher, created2 = Publisher.objects.get_or_create(name=data_file[3])
            Book(title=data_file[0],
                 ISBN=1111111111111,
                 page_amount=250,
                 author=author,
                 lend_period=LendPeriods.objects.get(id=1),
                 publisher=publisher,
                 status='available',
                 genre=data_file[2],
                 ).save()

    except Exception, e:
        print "Exception happen: " + str(e) + "book having problem" + data_file[0]
