import xlrd
import MySQLdb
import datetime
import os, sys
reload(sys)
sys.setdefaultencoding('utf-8')
# #
database = MySQLdb.connect(host="localhost", user="root", passwd="hundred@100", db="myansrsource")
cursor = database.cursor()
s = [f for f in os.listdir("master_templates/") if f!= "QMS-T1.xlsx"]

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
cursor.execute("SELECT id, name from QMS_reviewmaster")
result = cursor.fetchall()
review_master = dict((y, x) for x, y in result)
# print severity_level_master
now = datetime.datetime.now()
error = []
for t in s:
    # print "t",t
    book = xlrd.open_workbook("master_templates/"+t)
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
                try:
                    classification = classification_master[sheet.row(r)[5].value]
                except:
                    try:
                        classification = cursor.execute("SELECT id FROM QMS_defectclassificationmaster WHERE name=%s ",
                                                        (sheet.row(r)[5].value.strip(),))
                        classification = cursor.fetchone()
                        classification = int(classification[0])
                    except Exception as e:
                        print str(e), #sheet.row(r)[2].value

                try:
                    severity_level = classification_master[sheet.row(r)[4].value]
                except:
                    try:
                        severity_level = cursor.execute("SELECT id FROM QMS_severitylevelmaster WHERE name=%s ",
                                                        (sheet.row(r)[4].value.strip(),))
                        severity_level = cursor.fetchone()
                        severity_level = int(severity_level[0])
                    except Exception as e:
                        print str(e),# sheet.row(r)[3].value

                try:
                    defect_type = classification_master[sheet.row(r)[3].value]
                except:
                    try:
                        defect_type = cursor.execute("SELECT id FROM QMS_defecttypemaster WHERE name=%s ",
                                                     (sheet.row(r)[3].value.strip(),))
                        defect_type = cursor.fetchone()
                        defect_type = int(defect_type[0])
                    except Exception as e:
                        print str(e), #sheet.row(r)[1].value
                cursor.execute(
                    "INSERT INTO QMS_defectseveritylevel(defect_classification_id,"
                    "product_type, "
                    "severity_level_id,severity_type_id,"
                    "is_active,"
                    "created_by_id,updated_by_id,created_on,updated_on)"" "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    ((classification), 0,
                     (severity_level),
                     (defect_type), 1,
                     35, 35, now, now))
                fk = cursor.lastrowid
                database.commit()
            except Exception as e:
                cursor.execute("SELECT id FROM QMS_defectseveritylevel WHERE defect_classification_id =%s AND severity_level_id=%s AND severity_type_id=%s ",
                               ((classification), (severity_level),(defect_type)))
                fk = cursor.fetchall()
                fk = fk[0][0]
            try:
                cursor.execute(
                "INSERT INTO QMS_dsltemplatereviewgroup(template_id,"
                "review_master_id,is_active, defect_severity_level_id,"
                "created_by_id,updated_by_id,created_on,updated_on)VALUES "
                "(%s,%s,%s,%s,%s,%s,%s,%s)", (x, review_master_id, 1, fk, 35, 35, now, now))
                database.commit()
            except Exception as e:
                print "dsltrg", str(e)
        except Exception as e:
            pass
            # print "error",  Exception, str(e)
            error.append(str(e))

s = [f for f in os.listdir("media_templates/combo") ]
error = []
for t in s:
    # print "t",t
    book = xlrd.open_workbook("media_templates/combo/" + t)
    # sheets = ["copy_edit", "er", "eut", "QA", "CF"]
    sheet = book.sheet_by_name(u"Ref")

    for r in range(0, sheet.nrows):
        try:
            cursor.execute("SELECT id FROM QMS_templatemaster WHERE actual_name LIKE %s", ("%" + t[:-5] + '%',))
            data = cursor.fetchall()
            x = data[0][0]

            try:
                try:
                    classification = classification_master[sheet.row(r)[2].value]
                except:
                    try:
                        classification = cursor.execute("SELECT id FROM QMS_defectclassificationmaster WHERE name=%s ",
                                                        (sheet.row(r)[2].value.strip(),))
                        classification = cursor.fetchone()
                        classification = int(classification[0])
                    except Exception as e:
                        print str(e), sheet.row(r)[2].value

                try:
                    severity_level = severity_level[sheet.row(r)[3].value]
                except:
                    try:
                        severity_level = cursor.execute("SELECT id FROM QMS_severitylevelmaster WHERE name=%s ",
                                                        (sheet.row(r)[3].value.strip(),))
                        severity_level = cursor.fetchone()
                        severity_level = int(severity_level[0])
                    except Exception as e:
                        print str(e), sheet.row(r)[3].value

                try:
                    defect_type = defect_type[sheet.row(r)[1].value]
                except:
                    try:
                        defect_type = cursor.execute("SELECT id FROM QMS_defecttypemaster WHERE name=%s ",
                                                     (sheet.row(r)[1].value.strip(),))
                        defect_type = cursor.fetchone()
                        defect_type = int(defect_type[0])
                    except Exception as e:
                        print str(e), sheet.row(r)[1].value
                cursor.execute(
                    "INSERT INTO QMS_defectseveritylevel(defect_classification_id,"
                    "product_type, "
                    "severity_level_id,severity_type_id,"
                    "is_active,"
                    "created_by_id,updated_by_id,created_on,updated_on)"" "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    ((classification), 0,
                     (severity_level),
                     (defect_type), 1,
                     35, 35, now, now))
                fk = cursor.lastrowid
                database.commit()
            except Exception as e:
                cursor.execute("SELECT id FROM QMS_defectseveritylevel WHERE defect_classification_id =%s AND severity_level_id=%s AND severity_type_id=%s ",
                               ((classification), (severity_level),(defect_type)))
                fk = cursor.fetchall()
                fk = fk[0][0]
            tmp = sheet.row(r)[0].value.split(",")
            tmp_list = []
            for s in tmp:
                s = s[:-3].strip()
                try:
                    s = s.split('_')

                    s = s[0] + " " + s[1]
                except:
                    s = s
                tmp_list.append(s)
            # tmp_list = [s[:-3].strip() for s in tmp]
            # print tmp_list
            for rm in tmp_list:
                try:
                    try:
                        r=review_master[rm]
                    except Exception as e:
                        # print rm[0]
                        r=review_master[rm[0]]
                        print "r", r
                    cursor.execute(
                        "INSERT INTO QMS_dsltemplatereviewgroup(template_id,"
                        "review_master_id,is_active, defect_severity_level_id,"
                        "created_by_id,updated_by_id,created_on,updated_on)VALUES "
                        "(%s,%s,%s,%s,%s,%s,%s,%s)", (x, review_master[rm], 1, fk, 35, 35, now, now))
                    database.commit()
                except Exception as e:
                    print "in", x, str(e)
        except Exception as e:
            # pass
            print "error",  Exception, str(e)
            error.append(str(e))




cursor.close()
database.close()
# print error












# print error
