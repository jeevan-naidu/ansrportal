#!/bin/sh

sudo mount -t cifs  //172.16.2.20/MyANSRsource_backup  /www/MyANSRSource/ansr-timesheet/backup -o 'username=myansrsource,password=P@ssword,domain=ANSR,file_mode=0777,dir_mode=0777'
