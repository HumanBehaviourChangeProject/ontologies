set -e

python3 ParseBCIOUpperLevel.py
bash build-owl-files.sh

robot merge\
  --input bcio_upper_level.owl\
  --input ../Setting/bcio_setting.owl\
  --input ../ModeOfDelivery/bcio_mode_of_delivery.owl\
  --input ../Source/bcio_source.owl\
  --input ../MechanismOfAction/bcio_moa.owl\
  --input ../Behaviour/bcio_behaviour.owl\
  --input ../BehaviourChangeTechniques/bcto.owl\
  --input ../StyleOfDelivery/bcio_style.owl\
  annotate\
  --annotation rdfs:comment "The Behaviour Change Intervention Ontology (BCIO) is an ontology for all aspects of human behaviour change interventions and their evaluation. It is being developed as a part of the Human Behaviour Change Project (http://www.humanbehaviourchange.org). The BCIO is developed across several modules. This ontology file contains the merged version of the BCIO, encompassing the upper level and the modules for Setting, Mode of Delivery, Style of Delivery, Source, Mechanisms of Action, Behaviour and Behaviour Change Techniques. Additional modules will be added soon."\
  --annotation dc:title "Behaviour Change Intervention Ontology"\
  --ontology-iri "http://humanbehaviourchange.org/ontology/bcio.owl" --version-iri "http://humanbehaviourchange.org/ontology/bcio.owl/$(date +'%Y-%m-%d')" --output bcio.owl

cp bcio{,_external,_upper_level,_relations}.owl ../Upper\ Level\ BCIO/
