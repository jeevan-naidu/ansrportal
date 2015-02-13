import os
import logging

from django.core.management.base import BaseCommand
from django.conf import settings
from datetime import datetime


class Command(BaseCommand):
    help = 'Get MySQL Database backups done using this command'

    def handle(self, *args, **options):
        if os.path.exists(".backup/") is False:
            os.system('mkdir .backup/')

        dbName = settings.DATABASES['default']['NAME']
        userName = settings.DATABASES['default']['USER']
        password = settings.DATABASES['default']['PASSWORD']
        host = settings.DATABASES['default']['HOST']
        port = settings.DATABASES['default']['PORT']
        fileName = "BK-{0}".format(datetime.now().strftime('%Y-%m-%d_%H-%M'))
        fileName = fileName.replace(' ', '_')
        currentTime = datetime.now().strftime("%A, %d %B %Y %I:%M%p")

        bkCmd = 'mysqldump --log-error={5}/{6}.log --port={0} --host={1} --user={2} --password={3} {4} | gzip > \
            {5}/{6}.sql.gz'.format(port,
                                   host,
                                   userName,
                                   password,
                                   dbName,
                                   settings.BACKUPDIR,
                                   fileName)

        status = os.system(bkCmd)

        if status == 0:
            logging.info(
                'All tables in DB are backedup on {0}'.format(currentTime))
        else:
            logging.error(
                'DB backup failed on {0}, due to {1}'.format(
                    currentTime,
                    status))
