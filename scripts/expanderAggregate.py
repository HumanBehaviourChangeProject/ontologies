from abc import ABC
from enum import Enum
from pathlib import Path
from pprint import pprint
from typing import Dict, final, Union, Optional

import openpyxl
from openpyxl.styles import Font
import sys
import argparse

ID_SPACE = (15000, 16000)

FREE_IDS = list(range(ID_SPACE[0] + 1, ID_SPACE[1]))
PREFIX = 'BCIO'
ID_WIDTH = 6

class Kind(Enum):
    NUMBER = "number"
    VALUE = "value"
    PEOPLE = "people"
    ATTRIBUTES = "attributes"
    ROLES = "roles"
    PAST_BEHAVIOUR = "past behaviour"
    
class Aggregate(Enum):
    MEAN = "mean"
    MINIMUM = "minimum"
    MAXIMUM = "maximum"
    MEDIAN = "median"
    PERCENTAGE = "percentage"
    PROPORTION = "proportion"
    

def get_aggregate_definition(statistic: str, aggregate: Aggregate, kind: Kind) -> str:
    definition = {
        (Aggregate.MEAN, Kind.NUMBER): f"A {statistic} population statistic that is the mean number of {statistic} in the population.",
        (Aggregate.MINIMUM, Kind.NUMBER): f"A {statistic} population statistic that is the minimum number of {statistic} in the population.",
        (Aggregate.MAXIMUM, Kind.NUMBER): f"A {statistic} population statistic that is the maximum number of {statistic} in the population.",
        (Aggregate.MEDIAN, Kind.NUMBER): f"A {statistic} population statistic that is the median number of {statistic} in the population.",
        
        (Aggregate.MEAN, Kind.VALUE): f"A {statistic} population statistic that is the mean value of {statistic} in the population.",
        (Aggregate.MINIMUM, Kind.VALUE): f"A {statistic} population statistic that is the minimum value of {statistic} in the population.",
        (Aggregate.MAXIMUM, Kind.VALUE): f"A {statistic} population statistic that is the maximum value of {statistic} in the population.",
        (Aggregate.MEDIAN, Kind.VALUE): f"A {statistic} population statistic that is the median value of {statistic} in the population.",
        (Aggregate.PERCENTAGE, Kind.VALUE): f"A {statistic} population statistic that is the percentage value of {statistic} in the population.",
        (Aggregate.PROPORTION, Kind.VALUE): f"A {statistic} population statistic that is the proportion of individuals having a {statistic} in the population.",
        
        (Aggregate.PERCENTAGE, Kind.PEOPLE): f"A {statistic} population statistic that is the percentage of people that are a {statistic} in the population.",
        (Aggregate.PROPORTION, Kind.PEOPLE): f"A {statistic} population statistic that is the proportion of people that are a {statistic} in the population.",
        
        (Aggregate.PERCENTAGE, Kind.ATTRIBUTES): f"A {statistic} population statistic that is the percentage of people that are {statistic} in the population.",
        (Aggregate.PROPORTION, Kind.ATTRIBUTES): f"A {statistic} population statistic that is the proportion of people that are {statistic} in the population.",
        
        (Aggregate.PERCENTAGE, Kind.ROLES): f"A {statistic} population statistic that is the percentage of people that have a {statistic} in the population.",
        (Aggregate.PROPORTION, Kind.ROLES): f"A {statistic} population statistic that is the proportion of people that have a {statistic} in the population.",
        
        (Aggregate.PERCENTAGE, Kind.PAST_BEHAVIOUR): f"A {statistic} population statistic that is the percentage of people that have {statistic} in the population.",
        (Aggregate.PROPORTION, Kind.PAST_BEHAVIOUR): f"A {statistic} population statistic that is the proportion of people that have {statistic} in the population.",

    }.get((aggregate, kind))
    
    if definition is None:
        raise ValueError(
            f"Unknown aggregate {aggregate} for kind {kind} in statistic '{statistic}'"
        )
        
    return definition
    


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


def add_extra_values(header, row, aggregate, kind: Kind, parents: Dict[str, str]):
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
                    parent = parents.get(name, None)
                    if parent is not None and parent != "":
                        extra_values[key] = parent + " population statistic"
                    else:
                        extra_values[key] = "population statistic"
                else:
                    extra_values[key] = f"{name} population statistic"
                
                # pprint((key, agg, extra_values))
            elif key == "ID":
                new_id = new_id_str()
                extra_values[key] = new_id
            elif key == "Definition":
                if agg == "aggregate":
                    extra_values[key] = f"A population statistic about {name}."
                else:
                    extra_values[key] = get_aggregate_definition(name, Aggregate(agg.lower().strip()), kind)
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
    assert sheet is not None
    data = sheet.rows
    rows = []
    aggregate_list = ["Mean", "Minimum", "Maximum", "Median"]
    header = [i.value for i in next(data)]
    
    kind_index = header.index("Kind") if "Kind" in header else None
    assert kind_index is not None, "Header must contain 'Kind' column"

    # build ID list:
    for row in sheet[2:sheet.max_row]:
        values = {}
        extra_rows = []
        for key, cell in zip(header, row):
            values[key] = cell.value
            if key == "ID" and cell.value != None:
                register_id(cell.value)
                
    # build parents dict:
    # label -> (parent, is aggregate)
    entries: dict[str, tuple[str, str]] = {}
    for row in sheet[2:sheet.max_row]:
        values = dict(zip(header, [v.value for v in row]))
        label = values["Label"].strip() if values["Label"] is not None else ""
        if label == "":
            continue
        
        entries[label] = (
            values["Parent"].strip() if values["Parent"] is not None else "",
            values["Aggregate"] is not None and values["Aggregate"].strip() != ""
        )
        
    parents = {k: p for k, (p, _) in entries.items() if entries.get(p, ("", False))[1] == True}
    
    pprint(parents)

    # copy original:
    for row in sheet[2:sheet.max_row]:
        values = {}
        for key, cell in zip(header, row):
            values[key] = cell.value
        if any(values.values()):
            rows.append(values)

    for i, row in enumerate(sheet[2:sheet.max_row]):
        try:
            values = {}
            extra_rows = []

            for key, cell in zip(header, row):
                values[key] = cell.value
                if key == "Aggregate" and cell.value != None and cell.value != "":
                    kind = Kind(row[kind_index].value.strip()) if kind_index is not None else None
                    
                    if kind is None:
                        print("No kind found for row:", row)
                        continue

                    extra_rows = add_extra_values(header, row, cell.value, kind, parents)
                    # pprint(extra_rows)

            for extra_row in extra_rows:  # add to end of sheet
                rows.append(extra_row)
        except Exception as e:
            print(f"Error processing row {i}")
            raise e

    # new sheet to save:
    save_wb = openpyxl.Workbook()
    save_sheet = save_wb.active

    for c in range(len(header)):
        save_sheet.cell(row=1, column=c + 1).value = header[c]
        save_sheet.cell(row=1, column=c + 1).font = Font(size=12, bold=True)

    for r in range(len(rows)):
        row = [v for v in rows[r].values()]
        
        # pprint(row)
        for c in range(len(header)):
            # todo: why index out of bounds error here? Empty cells
            try:
                # print("got c:", row[c])
                save_sheet.cell(row=r + 2, column=c + 1).value = row[c]
            except:
                pass
                # print(f"row[c] not there ({row}, {c})")
    # save:
    save_wb.save(pathpath + "/" + basename + "_Expanded.xlsx")
    print("success")
