import xlrd
import MySQLdb
import datetime
#
import os, sys
reload(sys)
sys.setdefaultencoding('utf-8')
book = xlrd.open_workbook("MASTER.xlsx",encoding_override="cp1252")
database = MySQLdb.connect(host="localhost", user="root", passwd="root", db="myansrsource")
database.set_character_set('utf8')
#
cursor = database.cursor()

s1 = set()
s2 = set()
# # s3 = set()
# tmp = {}
now = datetime.datetime.now()
# # for cur_sheet in sheets:
templates= {}
sheet = book.sheet_by_name("Sheet3")
for r in range(1, sheet.nrows):

    if sheet.row(r)[1].value == " ":
        continue
    if sheet.row(r)[1].value == "END":
        break
    # s1.add(repr(sheet.row(r)[1].value))
    if sheet.row(r)[1].value != "":
        try:
            cursor.execute("INSERT INTO QMS_qmsprocessmodel(name,created_by_id,updated_by_id,created_on,updated_on,is_active,product_type)"
                           " VALUES (%s,%s,%s,%s,%s,%s,%s)", (sheet.row(r)[1].value, 35, 35, now, now, 1, 0))
        except:
            pass
        database.commit()

    if len(sheet.row(r)[4].value) > 0  and  sheet.row(r)[4].value != '' and sheet.row(r)[4].value not in s1:
        s1.add(sheet.row(r)[4].value)
        tmp = sheet.row(r)[4].value

    if sheet.row(r)[5].value != '' :
        # s2.add(sheet.row(r)[6].value)
        templates[tmp[:-4]] = sheet.row(r)[6].value


for k, v in templates.iteritems():
    if not k :
        continue
    else:
        print k,v
    try:
        cursor.execute("INSERT INTO QMS_templatemaster(name, actual_name, created_by_id,updated_by_id,created_on,updated_on,is_active)"
                   " VALUES (%s,%s, %s,%s,%s,%s,%s)", (v, k, 35, 35, now, now, 1))
    except :
        pass
    database.commit()

cursor.close()
database.close()
