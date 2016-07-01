import logging
import os
import glob
import csv
from datetime import datetime
from django.utils.timezone import get_default_timezone
from django.core.management.base import BaseCommand
from django.conf import settings
import re


logger = logging.getLogger('employee')


class Command(BaseCommand):
    help = 'Upload daily attendance data into the system.'

    def handle(self, *args, **options):
        
            file_pattern = u"/*.{0}".format(settings.FEED_EXT)
            file_path = "/home/amol/Django_Projects/Myansr_dev/ansr-timesheet/backup/Access-Control-Data/Leave-Transactions-Uploads"
            
            
            import ipdb;ipdb.set_trace()
            if glob.glob(file_path + file_pattern):
                import ipdb;ipdb.set_trace()
                # Reading each file and pushing record to db
                for eachFile in glob.glob(file_path + file_pattern):
                    with open(eachFile, 'r') as csvfile:
                        filereader = csv.reader(
                            csvfile,
                            delimiter=",")

                        logger.info(
                            u"Processing file {0}".format(eachFile))

                        # Validate data and insert to db
                        if "transaction" in csvfile.name.lower():
                            ProcessLeaveTransactions(filereader)
                        elif "balance" in csvfile.name.lower():
                            pass
                        else:
                            print "file not found"

                        logger.info(u"Processed file {0}".format(eachFile))
            else:
                logger.info("No more files to process.")
       

def ProcessLeaveTransactions(reader):
        import ipdb;ipdb.set_trace()
        
        headers_list = ['sl_no', 'employee_no', 'name', 'manager_no', 'manager_name', 'company',
                        'leave_type', 'transition_type', 'posted_date', 'from_date', 'to_date',
                        'days', 'expire_date', 'reason', 'remarks']
        headers_list = [i.lower().replace(" ", "_") for i in headers_list]
        
        #exclude headers row from csv
        reader.next()
        
        for index, row in enumerate(reader):
            temp_var = re.findall("[a-zA-Z]|[0-9]", row[0])  # to check for empty rows in csv,empty row will not contain any characters so exlude it
            if temp_var:
                row_dict = dict(zip(headers_list, row))
    
