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




