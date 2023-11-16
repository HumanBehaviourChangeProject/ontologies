from ontoutils import RobotImportsWrapper
from ontoutils import RobotTemplateWrapper
from ontoutils.lucid_chart import ParseLucidChartCsv

from logging_conf import setup_logging
setup_logging()


def main():
    # Get the imports and create the bcio_external.owl file

    import os
    os.chdir(os.path.dirname(__file__))

    robotWrapper = RobotImportsWrapper(robotcmd='robot', cleanup=False)
    robotWrapper.process_imports_from_excel(excel_file='../Upper Level BCIO/inputs/BCIO_External_Imports.xlsx',
                                            merged_iri='http://humanbehaviourchange.org/ontology/bcio_external.owl',
                                            merged_file='bcio_external.owl',
                                            merged_ontology_name='BCIO')

    # PARSE UPPER LEVEL DEFS FILE

    masterDefsFile = "../Upper Level BCIO/inputs/BCIO_Upper_Defs.xlsx"
    robotWrapper = RobotTemplateWrapper(robotcmd='robot')

    robotWrapper.add_classes_from_excel(masterDefsFile)

    # PARSE RELS FILE

    # Relations definitions and relation parents -- prepare a ROBOT template for creation
    # and for relabelling of relations.

    masterRelsFile = "../Upper Level BCIO/inputs/BCIO_Upper_Rels.xlsx"
    robotWrapper.add_rel_info_from_excel(masterRelsFile)

    csvFileName = 'rel-create-template.csv'
    robotWrapper.create_csv_relation_template_file(csvFileName)

    owlFileName = "bcio_relations.owl"
    BCIO_IRI_PREFIX = 'http://humanbehaviourchange.org/ontology/'
    BCIOR_ID_PREFIX = ['\"BCIOR: ' + BCIO_IRI_PREFIX + 'BCIOR_\"']
    ONTOLOGY_IRI = BCIO_IRI_PREFIX + "bcio_relations.owl"
    dependency = "bcio_external.owl"

    robotWrapper.createOntologyFromTemplateFile(csvFileName, dependency, BCIO_IRI_PREFIX, BCIOR_ID_PREFIX, ONTOLOGY_IRI,
                                                owlFileName)

    # The actual relation declarations for the upper level entities come from LucidChart.

    LucidChartCsvFileName = "../Upper Level BCIO/inputs/BCIO_Upper_level-LucidChart.csv"

    (entities, relations) = ParseLucidChartCsv.parseCsvEntityData(LucidChartCsvFileName)

    robotWrapper.mergeRelInfoFromLucidChart(entities, relations)

    # Create ROBOT template spreadsheet file ready for ExcelToOWL

    excelFileName = "BCIO_Upper_Level_Merged.xlsx"
    robotWrapper.write_spreadsheet(excelFileName, 'BCIO_ID')
    csvFileName = "BCIO_Upper_Level_Merged.csv"
    robotWrapper.add_classes_from_excel(excelFileName, csvFileName)

    owlFileName = "bcio_upper_level.owl"
    BCIO_IRI_PREFIX = 'http://humanbehaviourchange.org/ontology/'
    BCIO_ID_PREFIX = ['\"BCIO: ' + BCIO_IRI_PREFIX + 'BCIO_\"']
    ONTOLOGY_IRI = BCIO_IRI_PREFIX + "bcio_upper_level.owl"
    dependency = "bcio_relations.owl,bcio_external.owl"

    robotWrapper.createOntologyFromTemplateFile(csvFileName, dependency, BCIO_IRI_PREFIX, BCIO_ID_PREFIX, ONTOLOGY_IRI,
                                                owlFileName)

    # Create a single merged file for OLS:

    # robot merge --input bcio_upper_level.owl --input ../Setting/bcio_setting.owl --input ../ModeOfDelivery/bcio_mode_of_delivery.owl --input ../Source/bcio_source.owl  --input ../MechanismOfAction/bcio_moa.owl --input ../Behaviour/bcio_behaviour.owl --input ../BehaviourChangeTechniques/bcto.owl --input ../StyleOfDelivery/bcio_style.owl annotate --annotation rdfs:comment "The Behaviour Change Intervention Ontology (BCIO) is an ontology for all aspects of human behaviour change interventions and their evaluation. It is being developed as a part of the Human Behaviour Change Project (http://www.humanbehaviourchange.org). The BCIO is developed across several modules. This ontology file contains the merged version of the BCIO, encompassing the upper level and the modules for Setting, Mode of Delivery, Style of Delivery, Source, Mechanisms of Action, Behaviour and Behaviour Change Techniques. Additional modules will be added soon." --annotation dc:title "Behaviour Change Intervention Ontology" --ontology-iri "http://humanbehaviourchange.org/ontology/bcio.owl" --version-iri "http://humanbehaviourchange.org/ontology/bcio.owl/2023-08-30" --output bcio.owl

if __name__ == "__main__":
    main()