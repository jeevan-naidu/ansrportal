ansr-timesheet
==============


Creating a new deployement VM
=============================
For creating a new deployment VM.  First setup uwsgi using the following instructions.

Install needed libraries
--------------------------------------

apt-get install python2.7-dev htop libldap2-dev libsasl2-dev libssl-dev

Install uwsgi
--------------

Follow instructions for installation of uwsgi as given here

http://uwsgi-docs.readthedocs.org/en/latest/tutorials/Django_and_nginx.html

Install MySQL
--------------

Use this command to install client files

sudo apt-get install libmysqlclient-dev

Install Supervisor
------------------

Use this command to install supervisor

Use only pip to install supervisor and uwsgi

Create a new folder named "log" in {your-project}/supervisor/ folder
