import xlrd
import MySQLdb
import datetime
import copy
import os, sys
reload(sys)
sys.setdefaultencoding('utf-8')
#
book = xlrd.open_workbook("combo.xlsx" , encoding_override="utf-8")
database = MySQLdb.connect(host="localhost", user="root", passwd="root", db="myansrsource")
database.set_character_set('utf8')
#

cursor = database.cursor()
#
cursor.execute("SELECT id, name from QMS_qmsprocessmodel")
result = cursor.fetchall()
process_model = dict((y, x) for x, y in result)

cursor.execute("SELECT id, alias from QMS_reviewgroup ")
result = cursor.fetchall()
review_group_dict = dict((y, x) for x, y in result)

cursor.execute("SELECT id, alias from QMS_reviewgroup limit 9")
result = cursor.fetchall()
editorial_review_group = dict((y, x) for x, y in result)


cursor.execute("SELECT id, name from QMS_templatemaster")
result = cursor.fetchall()
template_master = dict((y, x) for x, y in result)

now = datetime.datetime.now()
# for cur_sheet in sheets:
sheet = book.sheet_by_name("Sheet3")
for r in range(1, sheet.nrows):

    if sheet.row(r)[2].value == "END":
        break
    if sheet.row(r)[2].value == "":
        continue

    if sheet.row(r)[2].value == "None":
        continue
    mandatory = str(sheet.row(r)[2].value.strip().encode('ascii', 'ignore').decode('ascii')).split(",")
    mandatory = [s.strip().encode('ascii', 'ignore').decode('ascii') for s in mandatory if s is not None]
    process_model = cursor.execute("SELECT id FROM QMS_qmsprocessmodel WHERE name=%s ", (sheet.row(r)[1].value,))
    process_model = cursor.fetchone()

    template = cursor.execute("SELECT id FROM QMS_templatemaster WHERE name=%s ", (sheet.row(r)[6].value.strip(),))

    template = cursor.fetchone()

    for s in mandatory:
        if s == "":
            continue
        else:

            review_group = review_group_dict[s]

        cursor.execute(
            "INSERT INTO QMS_templateprocessreview(review_group_id,created_by_id,updated_by_id,"
            "created_on,updated_on,is_mandatory,qms_process_model_id,template_id)"
                               " VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", (review_group, 471, 471, now, now, 1,
                                                                     int(process_model[0]), int(template[0])))
        database.commit()
    non_mandatory = str(sheet.row(r)[3].value.strip()).split(",")
    if sheet.row(r)[3].value == "all":
        non_mandatory = editorial_review_group.values()
    else:
        non_mandatory = [s.strip().encode('ascii', 'ignore').decode('ascii') for s in non_mandatory if s is not None]
    for s in non_mandatory:
        if s == "":
            continue

        else:
            review_group = review_group_dict[s]

        cursor.execute(
            "INSERT INTO QMS_templateprocessreview(review_group_id,created_by_id,updated_by_id,"
            "created_on,updated_on,is_mandatory,qms_process_model_id,template_id)"
            " VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", (review_group, 471, 471, now, now, 0,
                                                  int(process_model[0]), int(template[0])))
        database.commit()




cursor.close()
database.close()
