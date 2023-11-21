import os
import re
import openpyxl
import csv
import codecs
import sys
import argparse
import subprocess

from ontoutils.core import *
from ontoutils import RobotTemplateWrapper
from ontoutils.lucid_chart import *

from logging_conf import setup_logging
setup_logging()


## PROGRAM EXECUTION --- required arguments: input and output file names, and optional dependencies
if __name__ == '__main__':

    parser=argparse.ArgumentParser()
    parser.add_argument('--inputExcel', '-i',help='Name of the input Excel spreadsheet file')
    parser.add_argument('--outputOWL', '-o', help='Name of the output OWL file')
    parser.add_argument('--dependency', '-d', help='Name(s) of OWL files that this one is dependent on')

    args=parser.parse_args()

    inputFileName = args.inputExcel
    owlFileName = args.outputOWL
    dependency = args.dependency

    if inputFileName is None or owlFileName is None:
        parser.print_help()
        sys.exit('Not enough arguments. Expected at least -i "Excel file name" and -o "output OWL file name"')


    robotWrapper = RobotTemplateWrapper(robotcmd='robot')

    csvFileName = inputFileName.replace(".xlsx", ".csv")
    robotWrapper.add_classes_from_excel(inputFileName, csvFileName)


## EXECUTE THE ROBOT COMMAND AS A SUB-PROCESS

    BCIO_IRI_PREFIX = 'http://humanbehaviourchange.org/ontology/'
    BCIO_ID_PREFIX = '\"BCIO: '+BCIO_IRI_PREFIX+'BCIO_\"'
    ADDICTO_ID_PREFIX = '\"ADDICTO: http://addictovocab.org/ADDICTO_\"'

    ONTOLOGY_IRI = BCIO_IRI_PREFIX+ os.path.basename(owlFileName)


    r = robotWrapper.createOntologyFromTemplateFile(csvFileName, dependency, BCIO_IRI_PREFIX, [BCIO_ID_PREFIX,ADDICTO_ID_PREFIX], ONTOLOGY_IRI,owlFileName)
    if r != 0:
        exit(r)

