import os
import re
import openpyxl
import csv
import codecs
import sys
import argparse
import subprocess

from robot_wrapper import *


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

    csvFileName = robotWrapper.processClassInfoFromExcel(inputFileName)


## EXECUTE THE ROBOT COMMAND AS A SUB-PROCESS

    BCIO_IRI_PREFIX = 'http://humanbehaviourchange.org/ontology/'
    BCIO_ID_PREFIX = '\"BCIO: '+BCIO_IRI_PREFIX+'BCIO_\"'
    ONTOLOGY_IRI = BCIO_IRI_PREFIX+owlFileName


    robotWrapper.createOntologyFromTemplateFile(csvFileName, dependency, BCIO_IRI_PREFIX, BCIO_ID_PREFIX, ONTOLOGY_IRI,owlFileName)

