import xlrd
import MySQLdb
import datetime
import os, sys
reload(sys)
sys.setdefaultencoding('utf-8')
# #
database = MySQLdb.connect(host="localhost", user="root", passwd="root", db="myansrsource")
cursor = database.cursor()
header = set()
base_path = u"/home/rsb/ansrportal/ansrportal/QMS/media_templates/media_master_templates/"
s = [f for f in os.listdir(base_path)]
for t in s:
    # print u"/home/rsb/ansrportal/ansrportal/QMS/media_templates/media_master_templates/"+t
    book = xlrd.open_workbook(base_path+t)
    header.update(book.sheet_names())
s = set([u'Client Gold', u'Customer Feedback',  u'Client Round',
     u'QA Spot Check', u'Live', u'Scripts Copyedit', u'Gold-Review 4',
      u'Review 1', u'Beta 3-Review 3', u'combo', u'Beta 1-Review 1',
     u'Review 2',  u'Client Beta-Feedback',  u'Scripts Review',
     u'Video Review ', u'Review 3', u'Copy Edit 2', u'Copy Edit 1', u'Beta 2-Review 2', u'Client Feedback 2',
     u'Client Feedback 1', u'Copyedit', u'Screenshots'])
alias_combo = {u'Client Gold': u'CG', u'Customer Feedback': u'CF', }
ignore_header = [u'combo', u'Project Details', u'Data validation new', u'Summary',  u'Legend', u'R1']
print header

# Client Gold
# Customer Feedback
# Client Round
# QA Spot Check
# Live
# Scripts Copyedit
# Gold-Review 4
# Review 1
# Review 2
# Review 3
# Beta 1-Review 1
# Beta 3-Review 3
# Client Beta-Feedback
# Scripts Review
# Video Review
# Copy Edit 2
# Copy Edit 1
# Beta 2-Review 2
# Client Feedback 2
# Client Feedback 1
# Copyedit
# Screenshots

