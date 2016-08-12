#!/bin/sh

sudo mount -t cifs  //172.16.2.20/Prod\ Engineering  /www/MyANSRSource/ansr-timesheet/backup -o 'username=myansrsource,password=Welcome123,domain=ANSR,file_mode=0777,dir_mode=0777'
