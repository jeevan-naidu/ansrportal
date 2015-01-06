from django.core.management.base import BaseCommand
import os
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
        fileName = "BK-{0}".format(str(datetime.now()))
        fileName = fileName.replace(' ', '_')
        currentTime = datetime.now().strftime("%A, %d %B %Y %I:%M%p")

        bkCmd = 'mysqldump -P {0} -h {1} -u {2} -p{3} {4} > \
            .backup/{5}.sql'.format(
                port, host, userName, password, dbName, fileName
            )

        status = os.system(bkCmd)

        if status == 0:
            print 'All tables in DB are backedup on {0}'.format(currentTime)
        else:
            print 'DB backup failed on {0}, due to {1}'.format(
                currentTime, status
            )
