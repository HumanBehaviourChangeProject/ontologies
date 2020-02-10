## Documentation for the BCIO maintenance scripts

All scripts are implemented in Python 3. 

### 1. ExcelToOWL.py

For the BCIO project, the ontology files are primarily edited and maintained in Excel, while the OWL version is generated in full using scripts. The ExcelToOWL.py script is a wrapper around a subset of the [ROBOT](robot.obolibrary.org/) [template](http://robot.obolibrary.org/template) functionality. ROBOT templates offer a flexible and powerful mechanism for creating OWL ontology content based on CSV files following a specific structure. The wrapper script is intended to be used for generating classes that are to be added to the ontology in bulk. It adds the utility of having the primary content maintained in Excel rather than CSV (in particular to get around some oddities with editing CSV files using Excel), and having the template instructions hard coded for a defined set of column values. 

The columns that *must* appear in the input Excel file are: 

* **ID**: In which the identifier for the ontology class should be specified in CURIE format, i.e. BCIO:xxxxxx where xxxxxx is a unique number. 
* **Label**: In which the primary name for the ontology class is specified. Mapped to rdfs:label. 
* **Definition**: In which the text definition for the ontology class is specified. Mapped to an annotation of type IAO:0000115.
* **Parent**: In which the *label* of the immediate superclass (classification parent) should be specified. Mapped to rdfs:subClassOf. 

The columns that *may* appear in the input Excel file are: 
* **Definition_Source**: When definitions have been substantially re-used from external ontology sources, a pointer to the original source is specified here. Maps to an annotation axiom on the definition annotation, with type IAO:0000119.
* **Examples**: In which any examples of usage associated with the class should be annotated. Maps to an annotation of type IAO:0000112.
* **Elaboration**: In which any elaboration of the definition associated with the class should be annotated. Maps to an annotation of type IAO:0000112.
* **Comment**: In which any other comment associated with the class should be annotated. Maps to an annotation of type rdfs:comment.
* **Curator note**: In which a curator note associated with the class should be annotated. Maps to an annotation of type IAO:0000232.
* **Synonyms**: In which one or more synonyms for the entity should be annotated. These should be separated by a semicolon (;) if there are multiple. Maps to one or more annotations of the type IAO:0000118.
* One or more columns specifying specific types of **relationships** may be added. These should be named **REL 'rel name' [rel_id]**. For example, the column name for the *has part* relation should be: **REL 'has part' [BFO:0000051]**. These columns are mapped to object property assertions in OWL between the class specified by the template row and the class specified in the relation column. The column value should be the *name* of the target class. If more than one class is related to the template class with the specified relation, they may be separated with semicolons. 

Once the input template has been prepared, the script should be executed using 

python ExcelToOWL.py -i <input excel file name> -o <output owl file name> -d <owl dependencies>
  
Typically, when building the individual ontologies, the dependencies will be bcio_external.owl,bcio_upper_level.owl


### 2. ParseBCIOUpperLevel.py

The upper level of BCIO is more complex to build as it depends on appropriately importing external content as well as defining not only classes but also relations. For that reason, a dedicated script and several additional Excel files are required to (re)build the upper level BCIO from sources. The logic for this is implemented in the script file ParseBCIOUpperLevel.py. It follows several distinct steps. 

1. **Processing external imports**: The OWL file bcio_external.owl is built from the external imports Excel file BCIO_External_Imports.xlsx. That file has four columns: *Ontology ID*, *PURL*, *ROOT_ID* and *IDs*. The ontology ID is the short name of the external ontology, for example BFO, RO. The PURL is the stable URI for the ontology, and it is expected that the ontology will be downloadable from that PURL. In the root_id column, the base for the imported content is specified (content will be extracted from the external ontology with that as parent). In the IDs column a list of entities to be imported can be specified using semicolons as the separator; each entity should have the label followed by the ID in square brackets. For example: has part [BFO:0000051]. Externally imported content may be either classes or relations. The script downloads each external ontology file and then executes a [ROBOT extract](http://robot.obolibrary.org/extract) operation using the MIREOT approach. The result is merged into the file bcio_external.owl.
1. **Definition of relations**: Some of the relations used in the BCIO are imported, while others are only defined within the BCIO upper level. All relations that are used in the BCIO should appear in the Excel file BCIO_Upper_Rels.xlsx. This file has columns: *ID*, *Relationship*, *Equivalent to relationship*, *Parent relationship*, *Definition*, *Domain* and *Range*. For imported relationships, the ID should be the external ID, which should also be listed in the Equivalent to relationship column, but the name specified in the Relationship column may be specific to the usage within the BCIO. For the relations that are unique to BCIO, they should be assigned a unique identifier in the ID space "BCIOR", a parent relationship, text definition and a domain and range. The result is created as bcio_relations.owl.
1. **Definition of BCIO upper level**: The BCIO upper level is built from two separate files, namely the BCIO_Upper_Defs.xlsx which has the same features as a template for the ExcelToOWL.py script (described above) except without relation assertions, and the BCIO_Upper_level-LucidChart.csv file which is downloaded from the visual representation of the upper level that is developed within LucidChart. The names of the upper level entities should be identical in the LucidChart representation of the upper level and the Defs file, and the relation labels used in the LucidChart version must correspond to relation types defined in the Rels spreadsheet. The script then combines the class definitions with the relation assertions to create a normal input template file for execution with the ExcelToOWL utility script, and executes that to build the upper level OWL file bcio_upper_level.owl which in turn imports the relations and external owl files. 

The script can be executed from within the *scripts* folder and it will build the upper level of the ontology within the *Upper Level BCIO* folder. The repository file structure -- and consequently input and output file locations -- is currently specified *within* the script code, at a future date it might make sense to convert this to parameters. Thus, to execute the script just type 

python ParseBCIOUpperLevel.py





