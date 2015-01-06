import os
from django.conf import settings
from datetime import datetime


if os.path.exists(".backup/") is False:
    os.system('mkdir .backup/')

dbName = settings.DATABASES['default']['NAME']
userName = settings.DATABASES['default']['USER']
password = settings.DATABASES['default']['PASSWORD']
host = settings.DATABASES['default']['HOST']
port = settings.DATABASES['default']['PORT']
fileName = "BK-{0}".format(str(datetime.now()))

bkCmd = 'mysqldump -P {0} -h {1} -u {2} -p{3} {4} > .backup/{5}.sql'.format(
    port, host, userName, password, dbName, fileName
)

print bkCmd
status = os.system('ls -l > .backup/11.txt')

print status
