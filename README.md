# Welcome to the repository for the Behaviour Change Intervention Ontology (BCIO)

The Human Behaviour Change Project (HBCP) funded by the Wellcome Trust, and the Advancing Prevention Research in Cancer through Ontology Tools (APRICOT) Project funded by the US National Institutes of Health, are developing the Behaviour Change Intervention Ontology and associated tools and resources to be used in reporting research; linking datasets and synthesising evidence; and AI/machine learning algorithms to predict intervention outcomes in novel scenarios.

The overall aim of these projects is to automate evidence searching, synthesis and interpretation to rapidly address questions from policy-makers, practitioners and others to answer ‘What works, compared with what, how well, with what exposure, with what behaviours (for how long), for whom, in what settings and why?’. To achieve this, ontologies can help structure evidence, i.e., link evidence with a shared formal description of classes and relationships capturing domain knowledge in order to enable aggregation and semantic querying. We are developing and maintaining the Behaviour Change Intervention Ontology (BCIO) to do this.

Here you will find files of completed ontologies within the overarching BCIO. To date, the ontology files that have been released and are maintained include: 

* **The BCIO (with all lower-level ontologies)**
  * **bcio.owl:** The BCIO classes and relations in OWL format.
    
* **Upper-Level BCIO:** Includes files for the Behaviour Change Intervention Ontology (BCIO) and its upper-level structure.

  * **bcio_external.owl:** The classes imported from external ontologies into the BCIO in OWL format.
  * **bcio_relations.owl:** The relations in the BCIO in OWL format.
  * **bcio_upper_level.owl:** The upper-level classes and their relations in the BCIO in OWL format.

* **Behaviour:** Includes files for the Human Behaviour Ontology, a lower-level ontology within the BCIO that captures classes and relations to describe behaviours and their attributes.
  * **BCIO-behaviour-hierarchy.xlsx:** Spreadsheet with the Human Behaviour Ontology classes organised hierarchically for applications in behavioural sciences.
  * **bcio_behaviour.owl:** The Human Behaviour Ontology classes and their relations in OWL format.
  * **bcio_behaviour.xlsx:** Spreadsheet with the Human Behaviour Ontology classes and their relations.
  * **bcio_behaviour.rels.xlsx:** Spreadsheet with some relations in the Human Behaviour Ontology.
    * For additional relations, please refer to the relevant file in **Upper-Level BCIO**.

* **Behaviour Change Techniques:** Includes files for the Behaviour Change Technique Ontology, a lower-level ontology within the BCIO that captures classes and relations to describe behaviour change techniques (BCTs).
  * **BCIO-bcto-hierarchy.xlsx:** Spreadsheet with the Behaviour Change Technique Ontology classes organised hierarchically for applications in behavioural sciences.
  * **bcto.owl:** The Behaviour Change Technique Ontology classes and their relations in OWL format.
  * **bcto.xlsx:** Spreadsheet with the Behaviour Change Technique Ontology classes and their relations.

* **Engagement:** Includes files for the Intervention Engagement Ontology, a lower-level ontology within the BCIO that captures classes and relations to describe participants’ engagement with behaviour change interventions.
  * **BCIO_Engagement.xlsx:** Spreadsheet with the Intervention Engagement Ontology classes and their relations.
  * **bcio_engagement.owl:** The Engagement Ontology classes and their relations in OWL format.

* **Mechanism of Action:** Includes files for the Mechanism of Action Ontology, a lower-level ontology within the BCIO that captures classes and relations to describe mechanisms of action of behaviour change interventions.
  * **BCIO-moa-hierarchy.xlsx:** Spreadsheet with the Mechanism of Action Ontology classes organised hierarchically for applications in behavioural sciences.
  * **bcio_moa.owl:** The Mechanism of Action Ontology classes and their relations in OWL format.
  * **bcio_moa.xlsx**: Spreadsheet with the Mechanism of Action Ontology classes and their relations.

* **Mode of Delivery:** Includes files for the Mode of Delivery Ontology, a lower-level ontology within the BCIO that captures classes and relations to describe the mediums through which behaviour change interventions are delivered.
  * **BCIO-mode_of_delivery-hierarchy.xlsx:** Spreadsheet with the Mode of Delivery Ontology classes organised hierarchically for applications in behavioural sciences.
  * **bcio_mode_of_delivery.owl:** The Mode of Delivery Ontology classes and their relations in OWL format.
  * **bcio_mode_of_delivery.xlsx:** Spreadsheet with the Mode of Delivery Ontology classes and their relations.

* **Population:** Includes files for the Population Ontology, a lower-level ontology within the BCIO that captures classes and relations to describe people participating in a behaviour change intervention.
  * **BCIO-population-hierarchy.xlsx:** Spreadsheet with the Population Ontology classes organised hierarchically for applications in behavioural sciences.
  * **BCIO_Population.xlsx:** Spreadsheet with the Population Ontology classes and their relations.
  * **BCIO_Population_Expanded.xlsx:** Spreadsheet with the Population Ontology classes (including aggregate entities) and their relations.
  * **bcio_population.owl:** The Population Ontology classes and their relations in OWL format.

* **Schedule:** Includes files for the Intervention Schedule Ontology, a lower-level ontology within the BCIO that captures classes and relations to describe the timing of behaviour change interventions.
  * **BCIO_Schedule.xlsx:** Spreadsheet with the Intervention Schedule Ontology classes and their relations.
  * **bcio_schedule.owl:** The Intervention Schedule Ontology classes and their relations in OWL format.

* **Setting:** Includes files for the Intervention Setting Ontology, a lower-level ontology within the BCIO that captures classes and relations to describe entities that form the environment in which a behaviour change intervention is provided.
  * **BCIO-setting-hierarchy.xlsx:** Spreadsheet with the Intervention Setting Ontology classes organised hierarchically for applications in behavioural sciences.
  * **bcio_setting.owl:** The Intervention Setting Ontology classes and their relations in OWL format.
  * **bcio_setting.xlsx:** Spreadsheet with the Intervention Setting Ontology classes and their relations.

* **Source:** Includes files for the Intervention Source Ontology, a lower-level ontology within the BCIO that captures classes and relations to describe who delivers a behaviour change intervention.
  * **BCIO-source-hierarchy.xlsx:** Spreadsheet with the Intervention Source Ontology classes organised hierarchically for applications in behavioural sciences.
  * **bcio_source.owl:** The Intervention Source Ontology classes and their relations in OWL format.
  * **bcio_source.xlsx:** Spreadsheet with the Intervention Source Ontology classes and their relations.

* **Style of Delivery:** Includes files for the Intervention Style of Delivery Ontology, a lower-level ontology within the BCIO that captures classes and relations to describe the manner in which a behaviour change intervention is provided.
  * **BCIO-style-hierarchy.xlsx:** Spreadsheet with the Intervention Style of Delivery Ontology classes organised hierarchically for applications in behavioural sciences.
  * **bcio_style.owl:** The Intervention Style of Delivery Ontology classes and their relations in OWL format.
  * **bcio_style.xlsx:** Spreadsheet with the Intervention Style of Delivery Ontology classes and their relations.


In addition, the file for ‘onto-ed’ captures a script for OntoSpreadEd, an open-access ontology editor with GitHub integration, useful particularly for non-technical ontology developers. 
You can also find the scripts used to generate OWL files for each ontology [[scripts folder]](https://github.com/HumanBehaviourChangeProject/ontologies/tree/master/scripts). 

# Issue tracking 
You can report any issues with ontology files here: https://github.com/HumanBehaviourChangeProject/ontologies/labels 

# How is the Behaviour Change Intervention Ontology (BCIO) being developed? 
You can find methods used to develop the ontology in the following paper: https://wellcomeopenresearch.org/articles/5-126
Papers for each ontology will be published on Wellcome Open Research and updated here when available: https://wellcomeopenresearch.org/gateways/humanbehaviourchange/about 

# Relevant resources 
   * **Project website:** https://www.humanbehaviourchange.org/ 
   
   * **BCIO website:** https://www.bciontology.org/ 
   
   * **BCIOSearch website:** https://www.bciosearch.org/ 
   
   * **BCIOVisualise website:** https://bciovis.hbcptools.org/ 
   
   * **Ontology LookUp Service:** https://www.ebi.ac.uk/ols4/ontologies/bcio  
   
   For more information, please contact humanbehaviourchange@ucl.ac.uk

# GitHub contributors 
Janna Hastings, Björn Gehrke, Maya Braun, Robert West, Paulina Schenk, Ailbhe N. Finnerty, Emma Norris, Colbie Reed

# APRICOT and HBCP team members
The HBCP and APRICOT project are collaborations between behavioural and computer scientists, ontologists and systems architects. Members of the APRICOT Project team are listed directly below.

**APRICOT investigators:** Susan Michie, Janna Hastings, William Hogan, Marta Marques

**APRICOT researchers:** Björn Gehrke, Carolina Silva, Colbie Reed, Maya Braun, Paulina Schenk

**APRICOT consultants:** Robert West, Marie Johnston, Alex Rothman

**APRICOT administrator:** Amelia Massoura

The members of the Human Behaviour-Change Project can be found here: https://www.humanbehaviourchange.org/the-hbcp-team 
