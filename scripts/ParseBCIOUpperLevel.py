import os
import sys
import ontoutils
from ontoutils.core import *
from ontoutils.robot_wrapper import *
from ontoutils.lucid_chart import *

# os.chdir("/Users/hastingj/Work/Onto/HBCP/ontologies/scripts")
# Get the imports and create the bcio_external.owl file

robotWrapper = RobotImportsWrapper(robotcmd='robot')
robotWrapper.processImportsFromExcel(importsFileName='../Upper Level BCIO/inputs/BCIO_External_Imports.xlsx',
                                        importsOWLURI='http://humanbehaviourchange.org/ontology/bcio_external.owl',
                                        importsOWLFileName = 'bcio_external.owl',
                                        ontologyName = 'BCIO')



#PARSE UPPER LEVEL DEFS FILE

masterDefsFile = "../Upper Level BCIO/inputs/BCIO_Upper_Defs.xlsx"
robotWrapper = RobotTemplateWrapper(robotcmd='robot')

robotWrapper.processClassInfoFromExcel(masterDefsFile)


#PARSE RELS FILE

# Relations definitions and relation parents -- prepare a ROBOT template for creation
# and for relabelling of relations.

masterRelsFile = "../Upper Level BCIO/inputs/BCIO_Upper_Rels.xlsx"
robotWrapper.processRelInfoFromExcel(masterRelsFile)

csvFileName = 'rel-create-template.csv'
robotWrapper.createCsvRelationTemplateFile(csvFileName)

owlFileName = "bcio_relations.owl"
BCIO_IRI_PREFIX = 'http://humanbehaviourchange.org/ontology/'
BCIOR_ID_PREFIX = '\"BCIOR: '+BCIO_IRI_PREFIX+'BCIOR_\"'
ONTOLOGY_IRI = BCIO_IRI_PREFIX+"bcio_relations.owl"
dependency = "bcio_external.owl"

robotWrapper.createOntologyFromTemplateFile(csvFileName, dependency, BCIO_IRI_PREFIX, BCIOR_ID_PREFIX, ONTOLOGY_IRI , owlFileName)


# The actual relation declarations for the upper level entities come from LucidChart.

LucidChartCsvFileName = "../Upper Level BCIO/inputs/BCIO_Upper_level-LucidChart.csv"

parser = ParseLucidChartCsv()
(entities, relations) = parser.parseCsvEntityData(LucidChartCsvFileName)

robotWrapper.mergeRelInfoFromLucidChart(entities,relations)


# Create ROBOT template spreadsheet file ready for ExcelToOWL

excelFileName = "BCIO_Upper_Level_Merged.xlsx"
robotWrapper.createMergedSpreadsheet(excelFileName)
csvFileName = robotWrapper.processClassInfoFromExcel(excelFileName)


owlFileName = "bcio_upper_level.owl"
BCIO_IRI_PREFIX = 'http://humanbehaviourchange.org/ontology/'
BCIO_ID_PREFIX = '\"BCIO: '+BCIO_IRI_PREFIX+'BCIO_\"'
ONTOLOGY_IRI = BCIO_IRI_PREFIX+"bcio_upper_level.owl"
dependency = "bcio_relations.owl,bcio_external.owl"

robotWrapper.createOntologyFromTemplateFile(csvFileName, dependency, BCIO_IRI_PREFIX, BCIO_ID_PREFIX, ONTOLOGY_IRI,owlFileName)
