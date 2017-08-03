import xlrd
import MySQLdb
import datetime
import os, sys
from os.path import basename
from openpyxl import load_workbook, Workbook
from openpyxl.worksheet.datavalidation import DataValidation


reload(sys)
sys.setdefaultencoding('utf-8')
# #
database = MySQLdb.connect(host="localhost", user="root", passwd="root", db="myansrsource")
cursor = database.cursor()
# dst = "/home/rsb/ansrportal/ansrportal/QMS/x/"
s = [f for f in os.listdir("/home/rsb/ansrportal/ansrportal/QMS/master_templates/")]
# print s
# sheets = [u'For Consolidation', u'Summary', u'Legend', u'Editor Review 1', u'Editor Review 2',
#  u'Editor Review 3', u'EA', u'Copy Edit 1', u'Copy Edit 2', u'End User Testing',
#  u'QA Spot Check', u'Customer Feedback', u'Defect types & severity levels',
#  u'R1', u'R2']

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
# # [30,31,35,26,20,21,38,28,25,27,34,32,36,22,33, 39 ,23,29
# cursor.execute("SELECT id, name from QMS_defectclassificationmaster")
# result = cursor.fetchall()
# classification_master = dict((y.strip(), x) for x, y in result)
# # print classification_master
# cursor.execute("SELECT id, name from QMS_defecttypemaster")
# result = cursor.fetchall()
# defect_type_master = dict((y.strip(), x) for x, y in result)
# # print defect_type_master
# cursor.execute("SELECT id, name from QMS_severitylevelmaster")
# result = cursor.fetchall()
# severity_level_master = dict((y.strip(), x) for x, y in result)
# # print severity_level_master
# now = datetime.datetime.now()
# review_master_id = 1
# group_id = 1
# error = []
#
# cursor.execute("SELECT id, actual_name from QMS_templatemaster")
# result = cursor.fetchall()
# template_master = dict((str(y)+".xlsx", str(x)) for x, y in result)
# # print "tm ", template_master
# template_master['ansrS_QA_Tmplt_Devo (Project Devt) QA sheet_1.2.xlsx'] =21
# template_master['ansrS_QA_Tmplt_MHE DLE QA sheet_1.2.xlsx']= 22
# template_master['ansrS_QA_Tmplt_Devo (Question Upload) QA sheet_1.2.xlsx'] =  38
# template_master['ansrS_QA_Tmplt_Devo (SmartBook Reflow) QA sheet_1.2.xlsx']=28
# template_master['ansrS_QA_Tmplt_Devo (ATP) QA sheet_1.2.xlsx']=34
# # import re
#
# class RegexDict(dict):
#
#     def get_matching(self, event):
#         return (self[key] for key in self if re.match(key, event))
#
#
# rd = RegexDict(template_master)
# d = {}
for t in s:
    dst = "/home/rsb/ansrportal/ansrportal/QMS/master_templates/"+t
    wb = load_workbook(filename="/home/rsb/ansrportal/ansrportal/QMS/master_templates/"+t ,data_only=False)
    # book = xlrd.open_workbook("/home/rsb/ansrportal/ansrportal/QMS/core_templates/"+t)
    # sheets = ["copy_edit", "er", "eut", "QA", "CF"]
    # print book
    # sheets = book.sheet_names()
    # print sheets
    # sheets = sheets[1]
    #
    #for cur_sheet in sheets:
    #     if cur_sheet == "copy_edit":
    #         group_id = 1
    #         review_master_id = 2
    #     elif cur_sheet == "er":
    #         group_id = 2
    #         review_master_id = 1
    #     elif cur_sheet == "eut":
    #         group_id = 3
    #         review_master_id = 3
    #     elif cur_sheet == "QA":
    #         group_id = 4
    #         review_master_id = 4
    #     elif cur_sheet == "CF":
    #         group_id = 5
    #         review_master_id = 5
    try:
        sheet = wb[u"Ref"]
    except:
        continue

        # print "sheet",sheet
    c = 4
    for r in range(3, 100):
        c = str(c)

        if sheet["D" + c].value is None or sheet["E" + c].value is  None or sheet["F" + c].value is None:
            break
        # if sheet["D"+c].value is not  None or len(sheet["D"+c].value) == 0:
        #     print "im here"
            # continue
        print sheet["D"+c].value, sheet["E" + c].value, sheet["F" + c].value
        d, e, f = sheet["D"+c].value, sheet["E" + c].value, sheet["F" + c].value
        print "d:",len(d), "e:",len(e), "f:",len(f)
        d,e,f = d.rstrip(),e.rstrip(),f.rstrip()
        print "d:", len(d), "e:", len(e), "f:", len(f)
        sheet["D"+c].value = d.rstrip()
        sheet["E" + c].value = e.rstrip()
        sheet["F" + c].value = f.rstrip()
        c = int(c)
        c += 1
    d=1
    ws1 = wb[u"Template1"]
    for r in range(3, 600):
        d = str(d)
        # if sheet["D" + d].value is None or sheet["E" + d].value is None or sheet["F" + d].value is None:
        #     break
        severity_formula = DataValidation(type="custom", formula1='IFNA(VLOOKUP(D' + d + ',name,2,),"")')
        ws1.add_data_validation(severity_formula)
        # ws1["E" + c].value = row[3]
        severity_formula.add(ws1["E" + d])

        classification_formula = DataValidation(type="custom", formula1='IFNA(VLOOKUP(D' + d + ',name,3,),"")')
        ws1.add_data_validation(classification_formula)
        # ws1["F" + c].value = row[4]
        classification_formula.add(ws1["E" + c])
        d = int(d)
        d+=1
    wb.save(filename="/home/rsb/ansrportal/ansrportal/QMS/master_templates/"+t)
        # try:
                # try:
                #     if len(sheet.row(r)[5].value) == 0:
                #         continue
                #     cursor.execute(
                #         "INSERT INTO QMS_defecttypemaster(name,created_by_id,updated_by_id,created_on,updated_on,is_active)"
                #         " VALUES (%s,%s,%s,%s,%s,%s)", (sheet.row(r)[3].value.rstrip(), 471, 471, now, now, 1))
                #     database.commit()
                # except Exception as e:
                #     error.append(str(e))
                # # print "try"
                # try:
#                 #     # if (classification_master[(sheet.row(r)[5].value)]) == u"ansr Defect Classification" or \
#                 #     #                 (severity_level_master[(sheet.row(r)[4].value)]) == u"Severity level" or \
#                 #     #                 (defect_type_master[(sheet.row(r)[3].value)]) == u"Defect Types":
#                 #     #     print"yup"
#                 #     #     continue
#                 #     # else:
#                 #         # pass
#                 #         print sheet.row(r)[3].value, " --- ",sheet.row(r)[4].value, "  ----",sheet.row(r)[5].value
#                 #         #print classification_master[sheet.row(r)[2].value], severity_level_master[sheet.row(r)[1].value] ,defect_type_master[sheet.row(r)[0].value]
#                 # except Exception as e:
#                 #     print str(e)
#                 # print "class", sheet.row(r)[2].value, classification_master[sheet.row(r)[2].value]
#                 # print "sev", sheet.row(r)[1].value, severity_level_master[sheet.row(r)[1].value]
#                 # # print "ty", sheet.row(r)[0].value, defect_type_master[sheet.row(r)[0].value]
#                 # tmp = os.path.splitext(t)[0]
#                 # # print "basse name" , tmp , sheet.nrows
#                 # data = rd.get_matching(tmp)
#                 # for o in rd.get_matching(tmp):
#                 #     data = o
#                 # try:
#                 #     print t, ":",  template_master[t]
#                 # except Exception as e:
#                 #     print str(e)
#                 # cursor.execute("SELECT id FROM QMS_templatemaster WHERE actual_name LIKE %s", ("%" + tmp + '%',))
#                 # data = cursor.fetchall()
#                 #print tmp, data[0]
#                 # if not data:
#                 #     if t == "ansrS_QA_Tmplt_IM QA sheet_3.2_template.xlsx":
#                 #         data = 20
#                 #     if t =="ansrS_QA_Tmplt_Alt Text QA sheet_1.0_template_1.xlsx":
#                 #         data = 35
#                 #     if t == "ansrS_QA_Tmplt_Devo (Project Devt) QA sheet_1.2_Template.xlsx":
#                 #         data = 21
#                 #     if t == "ansrS_QA_Tmplt_Devo (Question Upload) QA sheet_1.2_Template.xlsx":
#                 #         data = 38
#                 #     if t == "ansrS_QA_Tmplt_Devo (SmartBook Reflow) QA sheet_1.2_Template.xlsx":
#                 #         data = 28
#                 #     if t == "ansrS_QA_Tmplt_Devo (ATP) QA sheet_1.2_Template.xlsx":
#                 #         data = 34
#                 #     if t == "ansrS_QA_Tmplt_MHE DLE QA sheet_1.2_Template.xlsx":
#                 #         data = 22
#                 #
#                 # if type(data) is int:
#                 #     x = data
#                 # else:
#                # # x = data[0][0]
#                #  try:
#                #      # print type(sheet.row(r)[5].value)
#                #      sheet.row(r)[5].value = sheet.row(r)[5].value
#                #      sheet.row(r)[4].value = sheet.row(r)[4].value
#                #      sheet.row(r)[3].value = sheet.row(r)[3].value
#                #      print classification_master[sheet.row(r)[5].value.strip()],\
#                #          severity_level_master[sheet.row(r)[4].value.strip()], \
#                #          defect_type_master[sheet.row(r)[3].value.strip()]
#                #  except Exception as e :
#                #     print "error", str(e)
#                #     # print classification_master ,defect_type_master
#                #     print sheet.row(r)[5].value ,"---",sheet.row(r)[4].value,"---",sheet.row(r)[3].value ,t
#                #  classification = sheet.row(r)[5].value.rstrip()
#                #  level = sheet.row(r)[4].value.rstrip()
#                #  type = sheet.row(r)[3].value.rstrip()
#                 # if type.lower() == "suggestion":
#                 #     try:
#                 #         cursor.execute(
#                 #             "INSERT INTO QMS_defectseveritylevel(defect_classification_id,"
#                 #             "product_type, "
#                 #             "severity_level_id,severity_type_id,"
#                 #             "is_active,"
#                 #             "created_by_id,updated_by_id,created_on,updated_on)"" "
#                 #             "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
#                 #             ((641), 0,
#                 #              (3),
#                 #              (639), 1,
#                 #              471, 471, now, now))
#                 #         fk = cursor.lastrowid
#                 #         database.commit()
#                 #     except:
#                 #         cursor.execute(
#                 #             "SELECT id FROM QMS_defectseveritylevel WHERE defect_classification_id =%s AND severity_level_id=%s AND severity_type_id=%s ",
#                 #             ((641),
#                 #              (3), (639)))
#                 #         fk = cursor.fetchall()
#                 #         fk = fk[0][0]
#                 #     try:
#                 #         # print data ,  review_master_id,fk
#                 #         cursor.execute(
#                 #             "INSERT INTO QMS_dsltemplatereviewgroup(template_id,"
#                 #             "review_master_id,is_active, defect_severity_level_id,"
#                 #             "created_by_id,updated_by_id,created_on,updated_on)VALUES "
#                 #             "(%s,%s,%s,%s,%s,%s,%s,%s)",
#                 #             (template_master[t], review_master_id, 1, fk, 471, 471, now, now))
#                 #         database.commit()
#                 #     except:
#                 #         continue
#                 # # if len(classification) == 0 or len(level) == 0 or len(type) == 0:
#                 #     continue
#                 # try:
#                 #     # continue
#                 #     cursor.execute(
#                 #         "INSERT INTO QMS_defectseveritylevel(defect_classification_id,"
#                 #         "product_type, "
#                 #         "severity_level_id,severity_type_id,"
#                 #         "is_active,"
#                 #         "created_by_id,updated_by_id,created_on,updated_on)"" "
#                 #         "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
#                 #         ((classification_master[classification]), 0,
#                 #          (severity_level_master[level]),
#                 #          (defect_type_master[type]), 1,
#                 #          471, 471, now, now))
#                 #     fk = cursor.lastrowid
#                 #     database.commit()
#                 # except Exception as e:
#                 #     print classification, level, type
#                 #     try:
#                 #         print "select or inssert", str(e)
#                 #         cursor.execute("SELECT id FROM QMS_defectseveritylevel WHERE defect_classification_id =%s AND severity_level_id=%s AND severity_type_id=%s ",
#                 #                        ((classification_master[classification]),
#                 #                         (severity_level_master[level]),(defect_type_master[type])))
#                 #         fk = cursor.fetchall()
#                 #         fk = fk[0][0]
#                 #     except:
#                 #         cursor.execute(
#                 #             "SELECT id FROM QMS_defectseveritylevel WHERE defect_classification_id =%s AND severity_level_id=%s AND severity_type_id=%s ",
#                 #             ((classification_master[str(classification)]),
#                 #              (severity_level_master[str(level)]), (defect_type_master[str(type)])))
#                 #         fk = cursor.fetchall()
#                 #         fk = fk[0][0]
#                 #
#                 # try:
#                 #     # continue
#                 #     # print data ,  review_master_id,fk
#                 #     cursor.execute(
#                 #     "INSERT INTO QMS_dsltemplatereviewgroup(template_id,"
#                 #     "review_master_id,is_active, defect_severity_level_id,"
#                 #     "created_by_id,updated_by_id,created_on,updated_on)VALUES "
#                 #     "(%s,%s,%s,%s,%s,%s,%s,%s)", (template_master[t], review_master_id, 1, fk, 471, 471, now, now))
#                 #     database.commit()
#                 # except Exception as e:
#                 #     print "dsltrg", str(e)
#             except Exception as e:
#                 pass
#                 # print "error",  Exception, str(e)
#                 error.append(str(e))
#     except Exception as e:
#         pass
#         #print "template", t
# cursor.close()
# database.close()






# print error
# ['ansrS_QA_Tmplt_FA Tools and Apps QA sheet_1.1.xlsx', 'ansrS_QA_Tmplt_Devo (Project Devt) QA sheet_1.2.xlsx',
#  'ansrS_QA_Tmplt_EZT(SEM) QA sheet_2.3.xlsx', 'ansrS_QA_Tmplt_F&A Supps QA sheet_1.2.xlsx',
#  'ansrS_QA_Tmplt_LS F&A QA sheet_1.0.xlsx', 'ansrS_QA_Tmplt_Passage Review QA sheet_1.1.xlsx',
#  'ansrS_QA_Tmplt_Devo (SmartBook Reflow) QA sheet_1.2.xlsx',
#  'ansrS_QA_Tmplt_Assessment (Non Platform) QA sheet_3.3.xlsx', 'ansrS_QA_Tmplt_PPT QA sheet_3.1.xlsx',
#  'ansrS_QA_Tmplt_F&A Performance card_1.1.xlsm', 'ansrS_QA_Tmplt_LS HSSL QA sheet_3.2.xlsx',
#  'ansrS_QA_Tmplt_Devo (ATP) QA sheet_1.2.xlsx', 'ansrS_QA_Tmplt_Cognero QA sheet_2.1.xlsx',
#  'ansrS_QA_Tmplt_LS SEM QA sheet_3.1.xlsx', 'ansrS_QA_Tmplt_Cengage 4LTR QA sheet_1.0.xlsx',
#  'ansrS_QA_Tmplt_Devo (Question Upload) QA sheet_1.2.xlsx', 'ansrS_QA_Tmplt_F&A Performance card_1.1.xlsx',
#  'ansrS_QA_Tmplt_Econ,Stats,SEM QA sheet_3.2.xlsx', 'ansrS_QA_Tmplt_Alt Text QA sheet_1.0.xlsx',
#  'ansrS_QA_Tmplt_IM QA sheet_3.1.xlsx', 'ansrS_QA_Tmplt_MHE DLE QA sheet_1.2.xlsx']
# {'ansrS_QA_Tmplt_Cognero QA sheet_2.1.xlsx': '29', 'ansrS_QA_Tmplt_LS HSSL QA sheet_3.2.xlsx': '24',
#  'ansrS_QA_Tmplt_Cengage 4LTR QA sheet_1.0.xlsx': '26', 'ansrS_QA_Tmplt_FPX QA sheet_1.0.xlsx': '39',
#  'ansrS_QA_Tmplt_MHE DLE QA sheet_1.1.xlsx': '22',
#  'ansrS_QA_Tmplt_Assessment (Non Platform) QA sheet_3.3.xlsx': '31', 'ansrS_QA_Tmplt_PPT QA sheet_3.1.xlsx': '32',
#  'ansrS_QA_Tmplt_Econ,Stats,SEM QA sheet_3.2.xlsx': '23', 'ansrS_QA_Tmplt_LS HSSL QA sheet_3.1.xlsx': '36',
#  'ansrS_QA_Tmplt_Devo (SmartBook Reflow) QA sheet_1.1.xlsx': '28',
#  'ansrS_QA_Tmplt_F&A Supps QA sheet_1.2.xlsx': '30', 'ansrS_QA_Tmplt_Alt Text QA sheet_1.0.xlsx': '35',
#  'ansrS_QA_Tmplt_Devo (Question Upload) QA sheet_1.1.xlsx': '38',
#  'ansrS_QA_Tmplt_Devo (Project Devt) QA sheet_1.1.xlsx': '21', 'ansrS_QA_Tmplt_LS SEM QA sheet_3.1.xlsx': '25',
#  'ansrS_QA_Tmplt_FA Tools and Apps QA sheet_1.1.xlsx': '27', 'ansrS_QA_Tmplt_IM QA sheet_3.1.xlsx': '20',
#  'ansrS_QA_Tmplt_Devo (ATP) QA sheet_1.1.xlsx': '34', 'ansrS_QA_Tmplt_F&A Performance card_1.1.xlsx': '37',
#  'ansrS_QA_Tmplt_EZT(SEM) QA sheet_2.3.xlsx': '33'}
