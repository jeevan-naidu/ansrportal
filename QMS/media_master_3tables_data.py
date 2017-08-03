import xlrd
import MySQLdb
import datetime
import os
#
# import os
# path = "/home/rsb/Desktop/Templates"
# filenames = os.listdir(path)
# for filename in filenames:
#     os.rename(os.path.join(path, filename), os.path.join(path, filename.replace(' ', '_')))
database = MySQLdb.connect(host="localhost", user="root", passwd="root", db="myansrsource")
cursor = database.cursor()
error = []
base_path = u"/home/rsb/ansrportal/ansrportal/QMS/media_templates/media_master_templates/"
# s = [f for f in os.listdir("/home/rsb/Desktop/Templates")]
# for media

s = [f for f in os.listdir(base_path)]


# print s
error = []
s1 = set()
s2 = set()
s3 = set()
for t in s:
    book = xlrd.open_workbook(base_path+t)
    # sheets = book.sheet_names()
    sheet = book.sheet_by_name("combo")
    # print sheets

    now = datetime.datetime.now()
    for r in range(1, sheet.nrows):
        if sheet.row(r)[0].value != '' or sheet.row(r)[1].value != '' or sheet.row(r)[2].value != '':
            s1.add(sheet.row(r)[0].value)
            s2.add(sheet.row(r)[1].value)
            s3.add(sheet.row(r)[2].value)

for ele in s1:
    try:
        cursor.execute("INSERT INTO QMS_defecttypemaster(name,created_by_id,updated_by_id,created_on,updated_on,is_active)"
                       " VALUES (%s,%s,%s,%s,%s,%s)", (ele, 471, 471, now, now, 1))
        database.commit()
    except Exception as e:
        error.append(str(e))
for ele in s2:
    try:
        cursor.execute("INSERT INTO QMS_severitylevelmaster (name,created_by_id,updated_by_id,created_on,updated_on,is_active)"
                       "VALUES (%s,%s,%s,%s,%s,%s)", (ele, 471, 471, now, now, 1))
        database.commit()
    except Exception as e:
        error.append(str(e))
for ele in s2:
    try:
        cursor.execute("INSERT INTO QMS_defectclassificationmaster (name,created_by_id,updated_by_id,"
                       "created_on,updated_on,is_active)"
                       "VALUES (%s,%s,%s,%s,%s,%s)", (ele, 471, 471, now, now, 1))
        database.commit()
    except Exception as e:
        error.append(str(e))


cursor.close()
database.close()
