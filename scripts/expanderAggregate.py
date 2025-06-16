from pathlib import Path
from typing import Dict, Union, Optional

import openpyxl
from openpyxl.styles import Font
import sys
import argparse

ID_SPACE = (15000, 16000)

FREE_IDS = list(range(ID_SPACE[0] + 1, ID_SPACE[1]))
PREFIX = 'BCIO'
ID_WIDTH = 6


def register_id(id: Union[str, int]) -> Optional[int]:
    if isinstance(id, str):
        [prefix, id_str] = id.split(":")
        if prefix.lower() != prefix.lower():
            return None

        id = int(id_str.strip())

    if id in FREE_IDS:
        FREE_IDS.remove(id)

    return id


def new_id() -> int:
    return FREE_IDS.pop(0)


def new_id_str() -> str:
    return f"{PREFIX}:{str(new_id()).zfill(ID_WIDTH)}"


def add_extra_values(header, row, aggregate, parents: Dict[str, str]):
    aggregate = aggregate.lower()
    aggregate_list = aggregate.split(";")
    # add "aggregate" to beginning of aggregate_list
    aggregate_list.insert(0, "aggregate")
    extra_rows = []
    for agg in aggregate_list:
        agg = agg.strip()
        extra_values = {}
        name = ""
        for key, cell in zip(header, row):
            if key == "Label":
                if agg == "aggregate":
                    extra_values[key] = f"{cell.value} population statistic"
                else:
                    extra_values[key] = f"{agg} {cell.value} population statistic"

                name = str(cell.value)

            elif key == "Parent":
                if agg == "aggregate":
                    if name in parents:
                        extra_values[key] = parents[name] + " population statistic"
                    else:
                        extra_values[key] = "population statistic"
                else:
                    extra_values[key] = f"{name} population statistic"
            elif key == "ID":
                new_id = new_id_str()
                extra_values[key] = new_id
            elif key == "Definition":
                if agg == "aggregate":
                    extra_values[key] = f"A population statistic about {name}."
                else:
                    extra_values[key] = f"The {agg} of {name} in a population."
            elif key in ["Curation status"]:
                extra_values[key] = str(cell.value) if cell.value != "External" else "Published"
            elif key in ["Sub-ontology"]:
                extra_values[key] = str(cell.value)
            elif key == "REL 'aggregate of'":
                extra_values[key] = name
            else:
                extra_values[key] = ""
        if any(extra_values.values()):
            extra_rows.append(extra_values)

    return extra_rows


## PROGRAM EXECUTION --- required argument: input file name
if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--inputExcel', '-i', help='Name of the input Excel spreadsheet file')

    args = parser.parse_args()

    inputFileName = args.inputExcel

    if inputFileName is None:
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

    # build ID list:
    for row in sheet[2:sheet.max_row]:
        values = {}
        extra_rows = []
        for key, cell in zip(header, row):
            values[key] = cell.value
            if key == "ID" and cell.value != None:
                register_id(cell.value)

    # copy original:
    for row in sheet[2:sheet.max_row]:
        values = {}
        for key, cell in zip(header, row):
            values[key] = cell.value
        if any(values.values()):
            rows.append(values)

    # build parents dict:
    parents = {}
    for row in sheet[2:sheet.max_row]:
        values = {}
        for key, cell in zip(header, row):
            values[key] = cell.value.strip() if cell.value is not None else cell.value
            if key == "Parent" and cell.value != None and cell.value != "":
                parents[values["Label"]] = cell.value.strip()

    for row in sheet[2:sheet.max_row]:
        values = {}
        extra_rows = []

        for key, cell in zip(header, row):
            values[key] = cell.value
            if key == "Aggregate" and cell.value != None and cell.value != "":
                extra_rows = add_extra_values(header, row, cell.value, parents)

        for extra_row in extra_rows:  # add to end of sheet
            rows.append(extra_row)

    # new sheet to save:
    save_wb = openpyxl.Workbook()
    save_sheet = save_wb.active

    for c in range(len(header)):
        save_sheet.cell(row=1, column=c + 1).value = header[c]
        save_sheet.cell(row=1, column=c + 1).font = Font(size=12, bold=True)

    for r in range(len(rows)):
        row = [v for v in rows[r].values()]
        # print("got row", row)
        for c in range(len(header)):
            # todo: why index out of bounds error here? Empty cells
            try:
                # print("got c:", row[c])
                save_sheet.cell(row=r + 2, column=c + 1).value = row[c]
            except:
                pass
                # print("row[c] not there")
    # save:
    save_wb.save(pathpath + "/" + basename + "_Expanded.xlsx")
    print("success")
