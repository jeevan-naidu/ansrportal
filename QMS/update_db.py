import xlrd
import MySQLdb
import datetime
import os, sys
reload(sys)
sys.setdefaultencoding('utf-8')
# #
database = MySQLdb.connect(host="localhost", user="root", passwd="root", db="myansrsource")
cursor = database.cursor()
s = [f for f in os.listdir("/home/rsb/Desktop/Templates")]
# ['ansrS_QA_Tmplt_F&A Supps QA sheet_1.2_Template.xlsx',
#  'ansrS_QA_Tmplt_Assessment (Non Platform) QA sheet_3.3_Template.xlsx',
#  'ansrS_QA_Tmplt_Alt Text QA sheet_1.0_template_1.xlsx',
#  'ansrS_QA_Tmplt_Cengage 4LTR QA sheet_1.0_Template.xlsx',
#  'ansrS_QA_Tmplt_IM QA sheet_3.2_template.xlsx',
#  'ansrS_QA_Tmplt_Devo (Project Devt) QA sheet_1.2_Template.xlsx',
#  'ansrS_QA_Tmplt_Devo (Question Upload) QA sheet_1.2_Template.xlsx',
#  'ansrS_QA_Tmplt_Devo (SmartBook Reflow) QA sheet_1.2_Template.xlsx',
#  'ansrS_QA_Tmplt_LS SEM QA sheet_3.1_Template.xlsx',
#  'ansrS_QA_Tmplt_FA Tools and Apps QA sheet_1.1_Template.xlsx',
#  'ansrS_QA_Tmplt_Devo (ATP) QA sheet_1.2_Template.xlsx',
#  'ansrS_QA_Tmplt_PPT QA sheet_3.1_template.xlsx',
#  'ansrS_QA_Tmplt_LS HSSL QA sheet_3.2_Template.xlsx',
#  'ansrS_QA_Tmplt_MHE DLE QA sheet_1.2_Template.xlsx',
#  'ansrS_QA_Tmplt_EZT(SEM) QA sheet_2.3_Template.xlsx',
#
#  'ansrS_QA_Tmplt_FPX QA sheet_1.0_template.xlsx',
#
#  'ansrS_QA_Tmplt_Econ,Stats,SEM QA sheet_3.2_Template.xlsx',
#  'ansrS_QA_Tmplt_Cognero QA sheet_2.1_Template.xlsx']
# [30,31,35,26,20,21,38,28,25,27,34,32,36,22,33, 39 ,23,29
error = []
for t in s:
    book = xlrd.open_workbook("/home/rsb/Desktop/Templates/"+t)
    # sheets = ["copy_edit", "er", "eut", "QA", "CF"]
    sheets = book.sheet_names()

    #
    cursor.execute("SELECT id, name from QMS_defectclassificationmaster")
    result = cursor.fetchall()
    classification_master = dict((str(y), str(x)) for x, y in result)
    # print classification_master
    cursor.execute("SELECT id, name from QMS_defecttypemaster")
    result = cursor.fetchall()
    defect_type_master = dict((str(y), str(x)) for x, y in result)
    # print defect_type_master
    cursor.execute("SELECT id, name from QMS_severitylevelmaster")
    result = cursor.fetchall()
    severity_level_master = dict((str(y), str(x)) for x, y in result)
    # print severity_level_master
    now = datetime.datetime.now()

    for cur_sheet in sheets:
        if cur_sheet == "copy_edit":
            group_id = 1
            review_master_id = 2
        elif cur_sheet == "er":
            group_id = 2
            review_master_id = 1
        elif cur_sheet == "eut":
            group_id = 3
            review_master_id = 3
        elif cur_sheet == "QA":
            group_id = 4
            review_master_id = 4
        elif cur_sheet == "CF":
            group_id = 5
            review_master_id = 5

        sheet = book.sheet_by_name(cur_sheet)

        for r in range(1, sheet.nrows):
            try:
                if str(classification_master[str(sheet.row(r)[2].value)]) == "ansr Defect Classification" or \
                                str(severity_level_master[str(sheet.row(r)[1].value)]) == "Severity level" or \
                                str(defect_type_master[str(sheet.row(r)[0].value)]) == "Defect Type":
                    continue
                # print "class", sheet.row(r)[2].value, classification_master[sheet.row(r)[2].value]
                # print "sev", sheet.row(r)[1].value, severity_level_master[sheet.row(r)[1].value]
                # print "ty", sheet.row(r)[0].value, defect_type_master[sheet.row(r)[0].value]
                s = t[:-14]
                cursor.execute("SELECT id FROM QMS_templatemaster WHERE actual_name LIKE %s", ("%" + s + '%',))
                data = cursor.fetchall()
                # print data ,  t, s
                if not data:
                    if t == "ansrS_QA_Tmplt_IM QA sheet_3.2_template.xlsx":
                        data = 20
                    if t =="ansrS_QA_Tmplt_Alt Text QA sheet_1.0_template_1.xlsx":
                        data = 35
                    if t == "ansrS_QA_Tmplt_Devo (Project Devt) QA sheet_1.2_Template.xlsx":
                        data = 21
                    if t == "ansrS_QA_Tmplt_Devo (Question Upload) QA sheet_1.2_Template.xlsx":
                        data = 38
                    if t == "ansrS_QA_Tmplt_Devo (SmartBook Reflow) QA sheet_1.2_Template.xlsx":
                        data = 28
                    if t == "ansrS_QA_Tmplt_Devo (ATP) QA sheet_1.2_Template.xlsx":
                        data = 34
                    if t == "ansrS_QA_Tmplt_MHE DLE QA sheet_1.2_Template.xlsx":
                        data = 22

                if type(data) is int:
                    x = data
                else:
                    x = data[0][0]

                try:
                    cursor.execute(
                        "INSERT INTO QMS_defectseveritylevel(defect_classification_id,"
                        "product_type, "
                        "severity_level_id,severity_type_id,"
                        "is_active,"
                        "created_by_id,updated_by_id,created_on,updated_on)"" "
                        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                        (str(classification_master[sheet.row(r)[2].value]), 0,
                         str(severity_level_master[sheet.row(r)[1].value]),
                         str(defect_type_master[sheet.row(r)[0].value]), 1,
                         471, 471, now, now))
                    fk = cursor.lastrowid
                    database.commit()
                except Exception as e:
                    cursor.execute("SELECT id FROM QMS_defectseveritylevel WHERE defect_classification_id =%s AND severity_level_id=%s AND severity_type_id=%s ",
                                   (str(classification_master[sheet.row(r)[2].value]), str(severity_level_master[sheet.row(r)[1].value]),str(defect_type_master[sheet.row(r)[0].value])))
                    fk = cursor.fetchall()
                    fk = fk[0][0]
                try:
                    # print data ,  review_master_id,fk
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
print error
