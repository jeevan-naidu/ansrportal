import os
import glob
from django.core.management.base import BaseCommand
from employee.models import Attendance

BK_DIR = "backup/Access-Control-Data"


class Command(BaseCommand):
    help = 'Pull Attendance to DB'

    def handle(self, *args, **options):
        if os.path.exists(BK_DIR):
            print os.listdir(BK_DIR)
            newest = max(glob.iglob('*.csv'), key=os.path.getctime)
            print newest
