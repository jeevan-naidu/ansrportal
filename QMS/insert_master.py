import xlrd
import MySQLdb
import datetime
#
import os, sys
reload(sys)
sys.setdefaultencoding('utf-8')
book = xlrd.open_workbook("combo.xlsx")
database = MySQLdb.connect(host="localhost", user="root", passwd="root", db="myansrsource")
database.set_character_set('utf8')
#
cursor = database.cursor()
# #
# # cursor.execute("SELECT id, name from QMS_defectclassificationmaster")
# # result = cursor.fetchall()
# # classification_master = dict((y, x) for x, y in result)
# #
# # cursor.execute("SELECT id, name from QMS_defecttypemaster")
# # result = cursor.fetchall()
# # defect_type_master = dict((y, x) for x, y in result)
# #
# # cursor.execute("SELECT id, name from QMS_severitylevelmaster")
# # result = cursor.fetchall()
# # severity_level_master = dict((y, x) for x, y in result)
# cursor.execute("SELECT name from QMS_qmsprocessmodel")
# result = cursor.fetchall()
# # qms = [(y, x) for x, y in result]
# pm = [i[0] for i in result]
# # print pm
# s1 = set()
# s2 = set()
# # s3 = set()
# tmp = {}
now = datetime.datetime.now()
# # for cur_sheet in sheets:
# process_model_set = []
# sheet = book.sheet_by_name("Sheet3")
# for r in range(1, sheet.nrows):
#     if sheet.row(r)[1].value == "END":
#         break
#     if sheet.row(r)[1].value == "":
#         continue
    # print sheet.row(r)[0]
    # print "1", sheet.row(r)[1].value
    # print "2",sheet.row(r)[2].value
    # print "3",sheet.row(r)[3].value
    # print "4",sheet.row(r)[4].value
    # print "5",sheet.row(r)[5].value
    # print "6",sheet.row(r)[6].value
    # print "7",sheet.row(r)[7].value
    # if sheet.row(r)[1].value != "END":
    #     break
    # if sheet.row(r)[6].value != '' :
    #     tmp[sheet.row(r)[6].value] = sheet.row(r)[5].value
    #     s1.add(sheet.row(r)[6].value)
    # if sheet.row(r)[2].value != '' :
    #     s2.add(sheet.row(r)[2].value)
    # s2.add(sheet.row(r)[1].value)
    # s3.add(sheet.row(r)[2].value)

# print s1
# print list(s2)
# z= list(s2 - set(pm))
# print z
z = [u'e-learning Creation',  u'Videos Creation', u'IP Creation', u'Videos Revision', u'IP Revision', u'Migration and/or Content Adaptation']

# #
for ele in z:
    try:
        cursor.execute('SET CHARACTER SET utf8;')
        cursor.execute('SET character_set_connection=utf8;')
        cursor.execute('SET NAMES utf8;')
        try:
            cursor.execute("INSERT INTO QMS_qmsprocessmodel(name,created_by_id,updated_by_id,created_on,updated_on,is_active,product_type)"
                           " VALUES (%s,%s,%s,%s,%s,%s,%s)", (ele, 471, 471, now, now, 1, 0))
        except:
            pass
        database.commit()
    except Exception as e:
        print str(e)


database.commit()
# "db" is the result of MySQLdb.connect(), and "dbc" is the result of  db.cursor().
#     except Exception as e:
#         print str(e)
# for ele in s1:
#     try:
#         cursor.execute("INSERT INTO QMS_templatemaster(name, actual_name, created_by_id,updated_by_id,created_on,updated_on,is_active)"
#                    " VALUES (%s,%s, %s,%s,%s,%s,%s)", (ele, tmp[ele], 471, 471, now, now, 1))
#     except :
#         pass
#     database.commit()
# # for ele in s2:
#     cursor.execute("INSERT INTO QMS_severitylevelmaster (name,created_by_id,updated_by_id,created_on,updated_on,is_active)"
#                    "VALUES (%s,%s,%s,%s,%s,%s)", (ele, 471, 471, now, now, 1))
#     database.commit()
# for ele in s3:
#     cursor.execute("INSERT INTO QMS_defectclassificationmaster (name,created_by_id,updated_by_id,"
#                    "created_on,updated_on,is_active)"
#                    "VALUES (%s,%s,%s,%s,%s,%s)", (ele, 471, 471, now, now, 1))
#     database.commit()

# cursor.execute("SELECT id, name from QMS_defectclassificationmaster")
# result = cursor.fetchall()
# classification_master = dict((y, x) for x, y in result)
#
# cursor.execute("SELECT id, name from QMS_defecttypemaster")
# result = cursor.fetchall()
# defect_type_master = dict((y, x) for x, y in result)
#
# cursor.execute("SELECT id, name from QMS_severitylevelmaster")
# result = cursor.fetchall()
# severity_level_master = dict((y, x) for x, y in result)


# print classification_master, "\n",  defect_type_master ,"\n", severity_level_master
# for s in s1:
#     print s,"\n"
# print len(s)
cursor.close()
database.close()
