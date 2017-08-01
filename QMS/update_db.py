import xlrd
import MySQLdb
import datetime
import os, sys
reload(sys)
sys.setdefaultencoding('utf-8')
# #
database = MySQLdb.connect(host="localhost", user="root", passwd="root", db="myansrsource")
cursor = database.cursor()
s = [f for f in os.listdir("/home/rsb/ansrportal/ansrportal/QMS/master_templates/") if f!= "QMS-T1.xlsx"]

cursor.execute("SELECT id, name from QMS_defectclassificationmaster")
result = cursor.fetchall()
classification_master = dict((y, x) for x, y in result)
# print classification_master
cursor.execute("SELECT id, name from QMS_defecttypemaster")
result = cursor.fetchall()
defect_type_master = dict((y, x) for x, y in result)
# print defect_type_master
cursor.execute("SELECT id, name from QMS_severitylevelmaster")
result = cursor.fetchall()
severity_level_master = dict((y, x) for x, y in result)
# print severity_level_master
now = datetime.datetime.now()
error = []
for t in s:
    # print "t",t
    book = xlrd.open_workbook("/home/rsb/ansrportal/ansrportal/QMS/master_templates/"+t)
    # sheets = ["copy_edit", "er", "eut", "QA", "CF"]
    sheet = book.sheet_by_name(u"Ref")
    #for cur_sheet in sheets:
        # if cur_sheet == "copy_edit":
        #     group_id = 1
        #     review_master_id = 2
        # elif cur_sheet == "er":
        #     group_id = 2
        #     review_master_id = 1
        # elif cur_sheet == "eut":
        #     group_id = 3
        #     review_master_id = 3
        # elif cur_sheet == "QA":
        #     group_id = 4
        #     review_master_id = 4
        # elif cur_sheet == "CF":
        #     group_id = 5
    review_master_id = 1

    # sheet = book.sheet_by_name(cur_sheet)

    for r in range(2, sheet.nrows):
        try:
            cursor.execute("SELECT id FROM QMS_templatemaster WHERE actual_name LIKE %s", ("%" + t[:-5] + '%',))
            data = cursor.fetchall()
            x = data[0][0]

            try:

                cursor.execute(
                    "INSERT INTO QMS_defectseveritylevel(defect_classification_id,"
                    "product_type, "
                    "severity_level_id,severity_type_id,"
                    "is_active,"
                    "created_by_id,updated_by_id,created_on,updated_on)"" "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    ((classification_master[sheet.row(r)[5].value]), 0,
                     (severity_level_master[sheet.row(r)[4].value]),
                     (defect_type_master[sheet.row(r)[3].value]), 1,
                     471, 471, now, now))
                fk = cursor.lastrowid
                database.commit()
            except Exception as e:
                cursor.execute("SELECT id FROM QMS_defectseveritylevel WHERE defect_classification_id =%s AND severity_level_id=%s AND severity_type_id=%s ",
                               ((classification_master[sheet.row(r)[5].value]), (severity_level_master[sheet.row(r)[4].value]),(defect_type_master[sheet.row(r)[3].value])))
                fk = cursor.fetchall()
                fk = fk[0][0]
            try:
                cursor.execute(
                "INSERT INTO QMS_dsltemplatereviewgroup(template_id,"
                "review_master_id,is_active, defect_severity_level_id,"
                "created_by_id,updated_by_id,created_on,updated_on)VALUES "
                "(%s,%s,%s,%s,%s,%s,%s,%s)", (x, review_master_id, 1, fk, 471, 471, now, now))
                database.commit()
            except Exception as e:
                print "dsltrg", str(e)
        except Exception as e:
            pass
            # print "error",  Exception, str(e)
            error.append(str(e))

cursor.close()
database.close()
# print error
