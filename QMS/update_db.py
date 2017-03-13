import xlrd
import MySQLdb
import datetime
#
book = xlrd.open_workbook("template_1.xlsx")
sheets = ["copy_edit", "er", "eut"]
database = MySQLdb.connect(host="localhost", user="root", passwd="root", db="myansrsource")
#
cursor = database.cursor()
#
cursor.execute("SELECT id, name from QMS_defectclassificationmaster")
result = cursor.fetchall()
classification_master = dict((y, str(x)) for x, y in result)

cursor.execute("SELECT id, name from QMS_defecttypemaster")
result = cursor.fetchall()
defect_type_master = dict((y, str(x)) for x, y in result)

cursor.execute("SELECT id, name from QMS_severitylevelmaster")
result = cursor.fetchall()
severity_level_master = dict((y, str(x)) for x, y in result)

now = datetime.datetime.now()

for cur_sheet in sheets:
    if cur_sheet == "copy_edit":
        group_id = 1
    elif cur_sheet == "er":
        group_id = 2
    else:
        group_id = 3
    sheet = book.sheet_by_name(cur_sheet)

    for r in range(1, sheet.nrows):
        try:
            cursor.execute(
                "INSERT INTO QMS_defectseveritylevel(defect_classification_id,"
                "review_master_id, "
                "severity_level_id,severity_type_id,template_id,"
                "created_by_id,updated_by_id,created_on,updated_on)"" "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (classification_master[sheet.row(r)[2].value],
                 group_id, severity_level_master[sheet.row(r)[1].value],
                 defect_type_master[sheet.row(r)[0].value], 1,
                 471, 471, now, now))
            database.commit()

        except Exception as e:
            print str(e)

cursor.close()
database.close()
