ansr-timesheet
==============


Creating a new deployment VM
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

Deploy Code 
-------------

* Deploy django code from git.
* Create a virtualenv for the project
* activate the virtualenv
* pip install -r requirements.txt


Install RabbitMQ
-------------------
Execute the following command to add the APT repository to your /etc/apt/sources.list.d:
echo 'deb http://www.rabbitmq.com/debian/ testing main' |
        sudo tee /etc/apt/sources.list.d/rabbitmq.list

(Please note that the word testing in this line refers to the state of our release of RabbitMQ, not any particular Debian distribution. You can use it with Debian stable, testing or unstable, as well as with Ubuntu. We describe the release as "testing" to emphasise that we release somewhat frequently.)
(optional) To avoid warnings about unsigned packages, add our public key to your trusted key list using apt-key(8):
wget -O- https://www.rabbitmq.com/rabbitmq-release-signing-key.asc |
        sudo apt-key add -
Our public signing key is also available from Bintray.

Run the following command to update the package list:
sudo apt-get update
Install rabbitmq-server package:
sudo apt-get install rabbitmq-server

Setting RabbitMQ
------------------
1) user creation --- rabbitmqctl add_user root root
2) add host -- rabbitmqctl add_vhost ansr
3) providing access for user for host --- rabbitmqctl set_permissions -p /ansr root "^root-.*" ".*" ".*"

