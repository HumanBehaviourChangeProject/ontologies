import os
from pathlib import Path
import re
import openpyxl
from openpyxl.styles import Font
import csv
import codecs
import sys
import argparse
import subprocess
import io




def generate_unique_id(base_id, id_list, num):
    num_list = []
    split_base = base_id.split(":")
    #print("Got split base",split_base[0])
    #print("id_list is ",id_list)
    
    # Get all BCIO IDs 
    for id in id_list:
        split_id = id.split(":")
        if split_id[0] == "BCIO":
            split_id_num = int(split_id[1])
            if split_id_num > 15000 and split_id_num < 16000:
                num_list.append(split_id_num)
    num_list.sort()
    
    new_num = max(num_list) + 1   # The default is the latest one
    
    if split_base[0] == 'BCIO':
        split_base_num = int(split_base[1])
        if split_base_num > 15000 and split_base_num < 16000:
            if split_base_num+num not in num_list: # First fill gaps 
                new_num = split_base_num + num
 
    id_list.append("BCIO:"+str(new_num).zfill(6))
    
    return id_list, "BCIO:"+str(new_num).zfill(6)


def add_extra_values(header, row, aggregate, id_list):#, num):
    aggregate = aggregate.lower()
    aggregate_list = aggregate.split(";")
    #add "aggregate" to beginning of aggregate_list
    aggregate_list.insert(0, "aggregate")    
    extra_rows = []
    i = 0#num
    for agg in aggregate_list:
        agg = agg.strip()
        i = i+1
        extra_values = {}
        name = ""
        for key, cell in zip(header, row):
            if key == "Label":
                extra_values[key] = f"[{cell.value}] {agg}"
                name = str(cell.value)
            elif key == "Parent":
                if agg == "aggregate":
                    extra_values[key] = 'data item'
                else: 
                    extra_values[key] = "aggregate "+name 
            elif key == "ID": 
                id_list, new_id = generate_unique_id(cell.value, id_list, i)
                extra_values[key] = new_id 
            elif key == "Definition":
                extra_values[key] = "The " + agg + " of " + name + " in a population."
            elif key in ["Curation status","Sub-ontology"]:
                extra_values[key] = str(cell.value)
            elif key == "REL 'aggregate of'":
                extra_values[key] = name
            else:
                extra_values[key] = "" 
        if any(extra_values.values()):
            extra_rows.append(extra_values)
    return id_list, extra_rows#, num


## PROGRAM EXECUTION --- required argument: input file name
if __name__ == '__main__':

    parser=argparse.ArgumentParser()
    parser.add_argument('--inputExcel', '-i',help='Name of the input Excel spreadsheet file')
    
    args=parser.parse_args()

    inputFileName = args.inputExcel
    
    if inputFileName is None :
        parser.print_help()
        sys.exit('Not enough arguments. Expected at least -i "Excel file name" ')

    pathpath = str(Path(inputFileName).parents[0])
    basename = str(Path(inputFileName).stem)
    suffix = str(Path(inputFileName).suffix)
    
    wb: openpyxl.Workbook = openpyxl.load_workbook(inputFileName)
    sheet = wb.active
    data = sheet.rows
    rows = []
    aggregate_list = ["Mean", "Minimum", "Maximum", "Median"]
    header = [i.value for i in next(data)]
    
    #build ID list:
    id_list = []
    for row in sheet[2:sheet.max_row]:
        values = {}
        extra_rows = []
        for key, cell in zip(header, row):
            values[key] = cell.value
            if key == "ID" and cell.value != None:
                id_list.append(cell.value)

    next_id = max(int(x.split(":")[-1]) for x in id_list) + 1
    # Generate missing IDs
    for row in sheet[2:sheet.max_row]:
        for key, cell in zip(header, row):
            if key == "ID" and cell.value is None:
                cell.value = f"BCIO:{next_id:06}"
                id_list.append(cell.value)
                next_id += 1
    wb.save(inputFileName)


    # copy original:
    for row in sheet[2:sheet.max_row]:
        values = {}
        extra_rows = []
        for key, cell in zip(header, row): 
            values[key] = cell.value
        if any(values.values()):
            rows.append(values)

    #create and add extra rows to end of sheet:
    #num = -1
    for row in sheet[2:sheet.max_row]:
        values = {}
        extra_rows = []

        for key, cell in zip(header, row):
            values[key] = cell.value
            if key == "Aggregate" and cell.value != None and cell.value != "":
                #num = num+1
                id_list, extra_rows = add_extra_values(header, row, cell.value, id_list)#, num)  #, num
        for extra_row in extra_rows: #add to end of sheet
            rows.append(extra_row)
        
    for r in range(len(rows)):
        row = [v for v in rows[r].values()]
        if "Aggregate" in header:
            cell = row[header.index("Aggregate")]    

    #new sheet to save:

    save_wb = openpyxl.Workbook()
    save_sheet = save_wb.active

    for c in range(len(header)):
        save_sheet.cell(row=1, column=c+1).value=header[c]
        save_sheet.cell(row=1, column=c+1).font = Font(size=12,bold=True)
    for r in range(len(rows)):
        row = [v for v in rows[r].values()]
        #print("got row", row)
        for c in range(len(header)):       
            #todo: why index out of bounds error here? Empty cells
                try:
                    #print("got c:", row[c])
                    save_sheet.cell(row=r+2, column=c+1).value=row[c]
                except: 
                    pass
                    # print("row[c] not there")            
    #save:   
    save_wb.save(pathpath + "/" + basename + "_Expanded.xlsx")
    print("success")
    

