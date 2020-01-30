


# Parse ALL input files and collect information about how many
# entities there are (BCIO, external, etc.)


# Relies on there being an ID column with either a BCIO ID or
# an external ID to count


# Needs specification of the root directory in which to find input files


ROOT_DIR = '../inputs/'

import os
import openpyxl

total_count = 0

for dir in os.listdir(ROOT_DIR):
    #print(dir)
    if os.path.isdir(ROOT_DIR+"/"+dir):
        for file in os.listdir(ROOT_DIR+"/"+dir):
            #print (file)
            ext = os.path.splitext(file)[-1].lower()
            if ext == ".xlsx":
                file_count = 0
                #print ("Got spreadsheet: ",file)
                wb = openpyxl.load_workbook(ROOT_DIR+"/"+dir+"/"+file)
                sheet = wb.active
                data = sheet.rows

                header = [i.value for i in next(data)]
                for row in data:
                    file_count = file_count+1

                print (file, ":", file_count)
                total_count = total_count+file_count

print('TOTAL COUNT: ',total_count)











