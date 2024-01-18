set -e

#python3 ./ExcelToOwl.py -d bcio_upper_level.owl,bcio_external.owl -i ../Setting/bcio_setting.xlsx -o ../Setting/bcio_setting.owl
python3 ./ExcelToOwl.py -d bcio_upper_level.owl,bcio_external.owl -i ../ModeOfDelivery/MoD.xlsx -o ../ModeOfDelivery/bcio_mode_of_delivery.owl
python3 ./ExcelToOwl.py -d bcio_upper_level.owl,bcio_external.owl -i ../Source/inputs/BCIO_Source.xlsx -o ../Source/bcio_source.owl
python3 ./ExcelToOwl.py -d bcio_upper_level.owl,bcio_external.owl -i ../MechanismOfAction/inputs/BCIO_MoA.xlsx -o ../MechanismOfAction/bcio_moa.owl
python3 ./ExcelToOwl.py -d bcio_upper_level.owl,bcio_external.owl -i ../Behaviour/BCIO_behaviour.xlsx -o ../Behaviour/bcio_behaviour.owl
python3 ./ExcelToOwl.py -d bcio_upper_level.owl,bcio_external.owl -i ../BehaviourChangeTechniques/inputs/BCIO_BehaviourChangeTechniques.xlsx -o ../BehaviourChangeTechniques/bcto.owl
python3 ./ExcelToOwl.py -d bcio_upper_level.owl,bcio_external.owl -i ../StyleOfDelivery/BCIO_StyleOfDelivery.xlsx -o ../StyleOfDelivery/bcio_style.owl