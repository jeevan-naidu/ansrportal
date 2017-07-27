import xlrd
import MySQLdb
import datetime
import copy
import os, sys
reload(sys)
sys.setdefaultencoding('utf-8')
#
book = xlrd.open_workbook("MASTER.xlsx" , encoding_override="utf-8")
database = MySQLdb.connect(host="localhost", user="root", passwd="root", db="myansrsource")
database.set_character_set('utf8')
#

cursor = database.cursor()
#
cursor.execute("SELECT id, name from QMS_qmsprocessmodel")
result = cursor.fetchall()
# print result
process_model = dict((y, x) for x, y in result)
# print process_model
cursor.execute("SELECT id, alias from QMS_reviewgroup limit 9")
result = cursor.fetchall()
review_group = dict(((y), (x)) for x, y in result)
# for k, v in review_group.iteritems():
#     print k
# print "rg", review_group
cursor.execute("SELECT id, name from QMS_templatemaster")
result = cursor.fetchall()
template_master = dict((y, x) for x, y in result)
# book = xlrd.open_workbook('CAP2.xlsm', formatting_info=True)
# book = openpyxl.load_workbook(filename='CAP2.xlsm', read_only=False, keep_vba=True)
# tmp_copy = xlutils.copy.copy(book)
# s1 = set()
# s2 = set()
# s3 = set()
# tmp = {}

import ast
process_model_set = []
sheet = book.sheet_by_name("Sheet3")
# for r in range(1, sheet.nrows):
#     if sheet.row(r)[1].value == "":
#         continue
#     elif sheet.row(r)[1].value == "END":
#         break
#     else:
#         print sheet.row(r)[1].value , type(sheet.row(r)[1].value)
#         process_model_set.append(sheet.row(r)[1].value)
# print set(process_model_set)
#
now = datetime.datetime.now()
# for cur_sheet in sheets:
sheet = book.sheet_by_name("Sheet3")
for r in range(1, sheet.nrows):
    # print "0",sheet.row(r)[0].value # type
    # print "1",sheet.row(r)[1].value # process model
    # # # if sheet.row(r)[2].value == "" or sheet.row(r)[3].value == "none" or sheet.row(r)[5].value == ""  or sheet.row(r)[6].value == "" :
    # # #     continue
    # print "2", sheet.row(r)[2].value  # mandatory
    # print "3", sheet.row(r)[3].value  # non mandatory
    # print "4", sheet.row(r)[4].value  # template name
    # print "5", sheet.row(r)[5].value  # required template name
    # print "6", sheet.row( r)[6].value  # remarks
    if sheet.row(r)[2].value == "END":
        break
    if sheet.row(r)[2].value == "":
        continue

    if sheet.row(r)[2].value == "None":

        try:
            pass
            process_model = cursor.execute("SELECT id FROM QMS_qmsprocessmodel WHERE name=%s ", (sheet.row(r)[1].value,))
            process_model = cursor.fetchone()
            # print int(process_model[0])
            tmp = sheet.row(r)[5].value
            tmp = tmp[:-4]
            template = cursor.execute("SELECT id FROM QMS_templatemaster WHERE name=%s ", (tmp,))

            template = cursor.fetchone()
            # print template
    # cursor.execute("SELECT id, name from QMS_qmsprocessmodel where name=")
                # result = cursor.fetchall()
            # non_mandatory = unicode(sheet.row(r)[3].value.strip()).split(",")
            # non_mandatory = [repr(s.strip()) for s in non_mandatory if s is not None]
            #
            for k, v in review_group.iteritems():
                cursor.execute(
                "INSERT INTO QMS_templateprocessreview(review_group_id,created_by_id,updated_by_id,"
                "created_on,updated_on,is_mandatory,qms_process_model_id,template_id)"
                               " VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", (v, 471, 471, now, now, 0,
                                                                 int(process_model[0]),int(template[0])))
            database.commit()

        except Exception as e:
            print str(e)
    else:
        pass
        mandatory = str(sheet.row(r)[2].value.strip()).split(",")
        print sheet.row(r)[2].value , mandatory
        # mandatory = [s.encode('ascii') for s in ast.literal_eval(mandatory)]
        mandatory = [s.strip().encode('ascii', 'ignore').decode('ascii') for s in mandatory if s is not None]
        # non_mandatory = str(sheet.row(r)[3].value.strip()).split(",")
        # non_mandatory = [s.strip() for s in non_mandatory if s is not None]
        print mandatory
        # print non_mandatory
    # database.commit()
    # print "7", sheet.row(r)[7].value   # all non mandatory
    # print "\n"
    # mandatory = unicode(sheet.row(r)[2].value.strip()).split(",")
    # for s in mandatory:
    #     print s
    # mandatory = [repr(s.strip()) for s in mandatory if s is not None]
    # print mandatory
    # for s in mandatory:
    #     try:
    #         pass
    #         print review_group[s], process_model[sheet.row(r)[2].value], template_master[sheet.row(r)[6].value]
    #     except Exception as e:
    #         print str(e)
        # cursor.execute(
        #     "INSERT INTO QMS_templateprocessreview(review_group_id,created_by_id,updated_by_id,"
        #     "created_on,updated_on,is_mandatory,qms_process_model_id,template_id)"
        #                        " VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", (review_group[s], 471, 471, now, now, 1,
        #                                                              process_model[str(sheet.row(r)[2].value)],
        #                                                              template_master[sheet.row(r)[6].value]))
        # database.commit()

    # if sheet.row(r)[3].value == "All":
    #     # print "all"
    #     tmp_dict = {}
    #     tmp_dict = copy.deepcopy(review_group)
    #     for key in mandatory:
    #         if key  in tmp_dict:
    #             del tmp_dict[key]
    #     non_mandatory = tmp_dict.keys()
    #
    # else:
    #     non_mandatory = unicode(sheet.row(r)[3].value.strip()).split(",")
    # non_mandatory = [s.strip() for s in non_mandatory if s is not None]
    # print non_mandatory

    # for s in non_mandatory:
    #     try:
    #         print review_group[s], process_model[sheet.row(r)[2].value], template_master[sheet.row(r)[6].value]
    #     except Exception as e:
    #         print str(e)
        # cursor.execute(
        #     "INSERT INTO QMS_templateprocessreview(review_group_id,created_by_id,updated_by_id,"
        #     "created_on,updated_on,is_mandatory,qms_process_model_id,template_id)"
        #     " VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", (review_group[s], 471, 471, now, now, 0,
        #                                           process_model[str(sheet.row(r)[2].value)],
        #                                           template_master[sheet.row(r)[6].value]))
        # database.commit()

    # if sheet.row(r)[6].value != '' :
    #     tmp[sheet.row(r)[6].value] = sheet.row(r)[5].value
    #     s1.add(sheet.row(r)[6].value)
    # if sheet.row(r)[2].value != '' :
    #     s2.add(sheet.row(r)[2].value)
    # s2.add(sheet.row(r)[1].value)
    # s3.add(sheet.row(r)[2].value)

#
# for ele in s2:
#     try:
#         cursor.execute('SET CHARACTER SET utf8;')
#         cursor.execute('SET character_set_connection=utf8;')
#         cursor.execute('SET NAMES utf8;')
#         cursor.execute("INSERT INTO QMS_qmsprocessmodel(name,created_by_id,updated_by_id,created_on,updated_on,is_active,product_type)"
#                        " VALUES (%s,%s,%s,%s,%s,%s,%s)", (ele, 471, 471, now, now, 1, 0))
#         database.commit()
#     except Exception as e:
#         print str(e)


# database.commit()
# # "db" is the result of MySQLdb.connect(), and "dbc" is the result of  db.cursor().
# #     except Exception as e:
# #         print str(e)
# for ele in s1:
#     cursor.execute("INSERT INTO QMS_templatemaster(name, actual_name, created_by_id,updated_by_id,created_on,updated_on,is_active)"
#                    " VALUES (%s,%s, %s,%s,%s,%s,%s)", (ele, tmp[ele], 471, 471, now, now, 1))
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
