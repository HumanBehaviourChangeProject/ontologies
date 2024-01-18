import os
import re
import openpyxl
import csv
import pronto
import distutils
import distutils.util

import urllib.request
import json
import re
import requests
import traceback


BCIOVOCAB_API = "https://api.bciosearch.org/"
GET_TERMS_BY_LABEL = "terms?label={}&page={}&itemsPerPage={}"
GET_TERMS = "terms/{}"
POST_TERMS = "terms"
DELETE_TERMS = "terms/{}"
PATCH_TERMS = "terms/{}"

AUTH_STR = "X-AUTH-TOKEN"
#AUTH_KEY = os.environ["AUTH_KEY"]

os.chdir("/Users/hastingj/Work/Onto/HBCP/ontologies")

in_path = "."
out_path = 'outputs'
label_id_map = {}
total_good = 0
num_entities = 0

# --- helper functions


def getIdForLabel(value):
    if value in label_id_map.keys():
        return ( label_id_map[value] )
    if value in label_id_map.values():
        return value  # already an ID
    if value.lower() in label_id_map.keys():
        return ( label_id_map[value.lower()] )
    if value.strip() in label_id_map.keys():
        return ( label_id_map[value.strip()] )
    if value.lower().strip() in label_id_map.keys():
        return ( label_id_map[value.lower().strip()] )

    m = re.search(r"\[(.*?)\]", value)
    if m:
        value2 = value.replace(m.group(0),"")
        return getIdForLabel(value2)

    raise ValueError (f"No ID found for {value}.")

def getLabelForID(value):
    if value in label_id_map.values():
        keys = [k for k,v in label_id_map.items() if v == value]
        return keys[0]
    else:
        return value

def getCorrectFormForLabel(value):
    if value in label_id_map.keys():
        return ( value )
    if value.lower() in label_id_map.keys():
        return ( value.lower() )
    if value.strip() in label_id_map.keys():
        return ( value.strip() )
    if value.lower().strip() in label_id_map.keys():
        return ( value.lower().strip() )

    return (value)

# -- Get the data out of spreadsheets

os.makedirs(out_path,exist_ok=True)   # shouldn't exist

bcio_files = ['./Upper Level BCIO/inputs/BCIO_Upper_Level_Merged.xlsx',
      './Source/bcio_source.xlsx',
      './MechanismOfAction/bcio_moa.xlsx',
      './Behaviour/bcio_behaviour.xlsx',
      './Setting/bcio_setting.xlsx',
      './ModeOfDelivery/bcio_mode_of_delivery.xlsx',
      './BehaviourChangeTechniques/bcto.xlsx',
      './StyleOfDelivery/bcio_style.xlsx']


for file in bcio_files:
    try:
        wb = openpyxl.load_workbook(file)
    except Exception as e:
        print(e)
        raise Exception("Error! Not able to parse file: "+file)

    sheet = wb.active
    data = sheet.rows
    good_entities = {}

    rel_columns = {}

    header = [i.value for i in next(data)]
    print (header)

    id_column = [i for (i,j) in zip(range(len(header)),header) if j=='ID' or j=='BCIO_ID'][0]
    label_column = [i for (i,j) in zip(range(len(header)),header) if j=='Label' or j=='Name'][0]
    def_column = [i for (i,j) in zip(range(len(header)),header) if j=='Definition'][0]
    parent_column = [i for (i,j) in zip(range(len(header)),header) if j=='Parent'][0]
    # Add comments, other fields
    # Add sub-ontology
#    if "REL 'has role'" in header:
#        rel_columns['has role'] = [i for (i,j) in zip(range(len(header)),header) if j=="REL 'has role'"][0]
#    if "REL 'has part'" in header:
#        rel_columns['has part'] = [i for (i,j) in zip(range(len(header)),header) if j=="REL 'has part'"][0]

    for relmatch in filter(lambda x: x.startswith("REL"), header):
        print(relmatch)
        s = re.search(r"REL '(.*?)'(.*?)",relmatch)
        if s:
            relname = s.group(1)
            rel_columns[relname] = header.index(relmatch)

    for row in data:
        rowdata = [i.value for i in row]
        id = rowdata[id_column]
        label = rowdata[label_column]
        if label:
            label = label.strip()
            if id in label_id_map.values():
                otherlabel = [k for k,v in label_id_map.items() if v == id][0]
                if label != otherlabel:
                    print(f"Appears to be a duplicate? This one {id}-{label}, the other {id}-{otherlabel}")
            label_id_map[label]=id
        defn = rowdata[def_column]
        parent = rowdata[parent_column]
        if parent:
            parent = parent.strip()

        if label and defn and parent:
            if len(label)>0 and len(defn)>0 and len(parent)>0:
                if label in good_entities.keys():
                    print(f"Appears to be a duplicate label: {label} in {file}")
                good_entities[label] = rowdata

    # Not validating the parents strictly for now.
    print(f"In file {file}, {len(good_entities)} GOOD.")
    total_good = total_good + len(good_entities)

    # If the parent is good too, replace its label with its ID
    for (label,rowdata) in good_entities.items():
        parent = rowdata[parent_column]
        if parent in label_id_map.keys():
            rowdata[parent_column] = label_id_map[parent]
    # Same for relation columns
        for colname, colindex in rel_columns.items():
            if rowdata[colindex]:
                vals = rowdata[colindex].split(";")
                vals_updated = []
                for v in vals:
                    if v in label_id_map.keys():
                        vals_updated.append(label_id_map[v])
                    else:
                        vals_updated.append(v)
                rowdata[colindex] = ";".join(vals_updated)

    # Write to modified files for sending to database
    filename = out_path + "/" + file.replace('/','.').split(sep=".")[-2] + ".csv"

    with open(filename, 'w') as ofile:
        writer = csv.writer(ofile)
        writer.writerow(header)
        for rowdata in good_entities.values():
            writer.writerow(rowdata)


print(f"Finished extracting {total_good} good entities.")


# -- Submit to BCIO Vocab



def getFromBCIOVocabByLabel(label,pageNo=1,totPerPage=30):
    urlstring = BCIOVOCAB_API + GET_TERMS_BY_LABEL.format(label,pageNo,totPerPage)
    print(urlstring)

    r = requests.get(urlstring,headers={AUTH_STR:AUTH_KEY})
    #print(f"Get returned {r.status_code}")
    return ( r.json() )


def getFromBCIOVocab(id):
    urlstring = BCIOVOCAB_API + GET_TERMS.format(id)
    #print(urlstring)
    r = requests.get(urlstring,headers={AUTH_STR:AUTH_KEY})
    #print(f"Get returned {r.status_code}")
    if r.status_code == 404:
        return (r.status_code, None)
    else:
        return (r.status_code, r.json())


def getURIForID(id, prefix_dict):
    if "BCIO" in id:
        return "http://bciovocab.org/"+id
    else:
        if ":" in id:
            id_split = id.split(":")
        elif "_" in id:
            id_split = id.split("_")
        else:
            print(f"Cannot determine prefix in {id}, just returning id")
            return(id)
        prefix=id_split[0]
        if prefix in prefix_dict:
            uri_prefix = prefix_dict[prefix]
            return (uri_prefix + "_" +id_split[1])
        else:
            print("Prefix ",prefix,"not in dict")
            return (id)


def createTermInBCIOVocab(header,rowdata, prefix_dict, create=True,links=False,revision_msg="Release"):
    data = {}
    for (value, headerval) in zip(rowdata,header):
        if value:
            if headerval == "ID" or headerval == "BCIO_ID":
                data['id'] = value
                data['uri'] = getURIForID(value, prefix_dict)
            elif headerval == "Label" or headerval == "Name":
                data['label'] = value
            elif headerval == "Definition":
                data['definition'] = value
            elif headerval in ["Definition source","Definition_Source", "Definition_ID"]:
                if 'definitionSource' in data:
                    data['definitionSource'] = data['definitionSource']+'\n'+value
                else:
                    data['definitionSource'] = value
            elif headerval == "Logical definition":
                data['logicalDefinition'] = value
            elif headerval == "Informal definition":
                data['informalDefinition'] = value
            elif headerval == "Sub-ontology":
                if value.lower() in ['population', 'engagement', 'schedule', 'reach', 'dose', 'fidelity', 'style of delivery', 'behaviour', 'mechanisms of action', 'setting', 'mode of delivery', 'source', 'outcome prediction']:
                    data['lowerLevelOntology'] = value.lower()
                else:
                    print("Lower level ontology value unknown: ",value)
            elif headerval == "Curator note":
                data['curatorNote'] = value
            elif headerval == "Synonyms":
                vals = value.split(";")
                data['synonyms'] = vals
            elif headerval == "Comment":
                data['comment'] = value
            elif headerval in ["Examples of usage","Examples","Elaboration"]:
                if 'examples' in data:
                    data['examples'] = data['examples']+'\n'+value
                else:
                    data['examples'] = value
            elif headerval == "Fuzzy set":
                if value:
                    try:
                        data['fuzzySet'] = bool(int(value))
                    except ValueError:
                        data['fuzzySet'] = bool(distutils.util.strtobool(value))
                else:
                    data['fuzzySet'] = False
            elif headerval == "Curator":
                pass
            elif headerval == "Curation status":
                if value in ['To Be Discussed','In Discussion']:
                    value = "Proposed"
                data['curationStatus'] = value
            elif headerval == "Why fuzzy":
                data['fuzzyExplanation'] = value
            elif headerval == "Cross reference":
                vals = value.split(";")
                data['crossReference'] = vals
            elif headerval == "BFO entity":
                pass
            elif links and headerval == "Parent":
                vals = value.split(";")
                if len(vals)==1:
                    try:
                        value=getIdForLabel(value)
                        data['parentTerm'] = f"/terms/{value}"
                    except ValueError:
                        print(f"No ID found for label {value}, skipping")
                        continue
                else:
                    for value in vals:
                        #value = vals[0]
                        try:
                            value = getIdForLabel(value)
                            data['parentTerm'] = f"/terms/{value}"
                            break
                        except ValueError:
                            print(f"No ID found for value {value}, skipping...")
                            continue
                    if 'parentTerm' not in data:
                        print(f"No usable parent found for {value}.")
                        continue
            elif links and re.match("REL '(.*)'",headerval):
                rel_name = re.match("REL '(.*)'",headerval).group(1)
                vals = value.split(";")
                vals_to_add = []
                for v in vals:
                    try:
                        v = '/terms/'+getIdForLabel(v)
                        vals_to_add.append(v)
                    except ValueError:
                        print(f"No ID found for linked value {v}, skipping.")
                if len(vals_to_add)>0:
                    if 'termLinks' not in data:
                        data['termLinks'] = []
                    data['termLinks'].append({'type':rel_name,
                                          'linkedTerms':vals_to_add})
            else:
                print(f"Unknown/ignored header: '{headerval}'")

    if 'eCigO' not in data:
        data['eCigO'] = False
    if 'fuzzySet' not in data:
        data['fuzzySet'] = False
    if 'curationStatus' not in data:
        data['curationStatus'] = "Proposed"

    if create:
        headers = {"accept": "application/ld+json",
               "Content-Type": "application/ld+json",
               AUTH_STR:AUTH_KEY}
    else:
        headers = {"accept": "application/ld+json",
               "Content-Type": "application/merge-patch+json",
               AUTH_STR:AUTH_KEY}
        if data['curationStatus'] == 'Published':  # Revision msg needed
            data['revisionMessage'] = revision_msg

    #print(data)

    try:
        if create:
            urlstring = BCIOVOCAB_API + POST_TERMS
            r = requests.post(urlstring, json = data, headers=headers)
            status = r.status_code
        else:
            urlstring = BCIOVOCAB_API + PATCH_TERMS.format(data['id'])
            r = requests.patch(urlstring, json = data, headers=headers)
            status = r.status_code
        print(f"Create returned {r.status_code}, {r.reason}")
        #if r.status_code in ['500',500,'400',400,'404',404]:
            #print(f"Problematic JSON: {json.dumps(data)}")
    except Exception as e:
        traceback.print_exc()
        status = None
    return ( ( status, json.dumps(data) ) )


def deleteTermFromBCIOVocab(id):
    urlstring = BCIOVOCAB_API + DELETE_TERMS.format(id)

    r = requests.delete(urlstring,headers={AUTH_STR:AUTH_KEY})

    print(f"Delete {id}: returned {r.status_code}")


def getDefinitionForProntoTerm(term):
    if term.definition and len(term.definition)>0:
        return (term.definition)
    annots = [a for a in term.annotations]
    for a in annots:
        if isinstance(a, pronto.LiteralPropertyValue):
            if a.property == 'IAO:0000115':  # Definition
                return (a.literal)
            if a.property == 'IAO:0000600':  # Elucidation
                return (a.literal)
    if term.comment:
        return (term.comment)
    return ("None")


# load the dictionary for prefix to URI mapping

dict_file = 'scripts/prefix_to_uri_dictionary.csv'
prefix_dict = {}
reader = csv.DictReader(open(dict_file, 'r'))
for line in reader:
    prefix_dict[line['PREFIX']] = line['URI_PREFIX']

path = 'outputs'

bcio_files = []

for root, dirs_list, files_list in os.walk(path):
    for file_name in files_list:
        full_file_name = os.path.join(root, file_name)
        bcio_files.append(full_file_name)

entries = {}
bad_entries = []
revisionmsg="August BCIO release"

# get the external in the right format for pronto
# robot merge --input Upper\ Level\ BCIO/bcio_external.owl convert --check false --output bcio_external.obo

# All the external content + hierarchy is in the file bcio_external.obo
# Had to manually replace is_metadata_tag: 1 with is_metadata_tag: true

externalonto = pronto.Ontology("scripts/bcio_external.obo")
for term in externalonto.terms():
    label_id_map[term.name] = term.id

# get the "ready" input data, indexed by ID
for filename in bcio_files:
    with open(filename, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        header = next(csvreader)

        for row in csvreader:
            rowdata = row
            id = rowdata[0]
            entries[id] = (header,rowdata)



### Update entries with new data
### Try to create if update fails

#i=0;

# Patch if exists or else create first without links


for (header,test_entity) in entries.values():
    # restrict to a specified count, comment out when done
    #i = i+1
    #print("i=",i)
    #if i<=40: continue
    id = test_entity[0]
    # Redo bad entities, comment out when done:
    #if id not in bad_entries:
    #    continue
    # get it first
    (status,entry) = getFromBCIOVocab(test_entity[0])
    if status == 200:
        print("Found existing entry: ",id)
        # Now check if existing status is 'published'. if yes don't patch without message... manually.
        existing_status = entry['curationStatus']
        if existing_status == 'published':
            print("Not patching ",id," as already published.")
            # Only patch if changed. Get the latest revision:
            termRevision = entry['termRevisions'][0]
            for t in entry['termRevisions']:
                if 'modifiedAt' in t and  t['modifiedAt']>=termRevision['modifiedAt']:
                    termRevision=t
            print("Got latest revision mod. at",termRevision['modifiedAt'])
            termLabel = termRevision['label']
            termDef = termRevision['definition']
            if 'parentTerm' in termRevision:
                termParent = termRevision['parentTerm']
            else:
                termParent = ""

            newLabel = test_entity[header.index("Label")]
            newDef = test_entity[header.index("Definition")]
            try:
                newParent =getIdForLabel(test_entity[header.index('Parent')])
            except ValueError:
                newParent = ""
            newParent = f"/terms/{newParent}"
            CHANGED = False
            if termLabel != newLabel or termDef != newDef or termParent != newParent:
                print("PUBLISHED TERM CHANGED: ",id,"ORIG",termLabel,termDef,termParent,"CH TO",newLabel,newDef,newParent,"Patching...")
                # Patch it:
                (status,jsonstr) = createTermInBCIOVocab(header, test_entity, prefix_dict, create=False, links=True, revision_msg=revisionmsg)
                if status != 200:
                    print(status, ": Problem patching term ",id,"with JSON: ",jsonstr)

        else:
            # Now patch.
            (status, jsonstr) = createTermInBCIOVocab(header,test_entity,prefix_dict, create=False, links=True)
            if status != 200:
                print("Error patching existing entry. Investigate: ",id, status, jsonstr)

    else:
        # Not found by ID. Try submit with post IF NOT OBSOLETE
        if "Curation status" in header and test_entity[header.index("Curation status")] == 'Obsolete':
            print("Skipping obsolete entry: ",test_entity)
        else:
            (status, jsonstr) = createTermInBCIOVocab(header,test_entity,prefix_dict)
            if status != 201:
                id = test_entity[0]
                print (status, ": Problem creating term ",id," with JSON: ",jsonstr)
                bad_entries.append(id)



# Now create additional external entries, first without links
for term in externalonto.terms():
    try:
        id = term.id
        external_header=["ID","Label","Definition","Parent","Curation status"]

        # First round: Create those that are not in
        if id not in entries:
            label = term.name
            definition = getDefinitionForProntoTerm(term)
            parents = []
            for supercls in term.superclasses(distance=1):
                parents.append(supercls.id)
            parent = ";".join(parents)
            #print("TERM DATA: ",id,",",label,",",definition,",",parent)
            # Submit to BCIO Vocab
            (status, jsonstr) = createTermInBCIOVocab(external_header,[id,label,definition,parent,"External"],prefix_dict,create=False,links=False)
            if status != 200:
                (status, jsonstr) = createTermInBCIOVocab(external_header,[id,label,definition,parent,"External"],prefix_dict,create=True,links=False)
                if status != 201:
                    print (status, ": Problem creating term ",id," with JSON: ",jsonstr)
                    bad_entries.append(id)
    except ValueError:
        print("ERROR PROCESSING: ",id)
        continue


# Then add links (own entries)
for id in entries:
    (header,rowdata) = entries[id]
    # Check if need to patch it:
    (status, entry) = getFromBCIOVocab(id)
    if status == 200:
        if entry['curationStatus'].lower() not in ['published','obsolete']:
            (status,jsonstr) = createTermInBCIOVocab(header, rowdata, prefix_dict, create=False, links=True)
            if status != 200:
                print(status, ": Problem patching term ",id,"with JSON: ",jsonstr)
                bad_entries.append(id)


# Then add links (external entries)
for term in externalonto.terms():
    try:
        id = term.id
        external_header=["ID","Label","Definition","Parent","Curation status"]
        # Second round: Should all be in. Patch with parents
        label = term.name
        definition = getDefinitionForProntoTerm(term)
        parents = []
        for supercls in term.superclasses(distance=1):
            if supercls.id != id:
                parents.append(supercls.id)
        parent = ";".join(parents)

        print("TERM DATA: ",id,",",label,",",parent)

        # Patch it:
        (status,jsonstr) = createTermInBCIOVocab(external_header, [id,label,definition,parent,"External"], prefix_dict, create=False, links=True)
        if status != 200:
            print(status, ": Problem patching term ",id,"with JSON: ",jsonstr)
            bad_entries.append(id)
    except ValueError:
        print("ERROR PROCESSING: ",id)
        continue



### Add parents for published entries !!!

#for id in entries:
#    (header,rowdata) = entries[id]
#    # Check if need to patch it:
#    (status, entry) = getFromBCIOVocab(id)
#    if status == 200:
#        if entry['curationStatus'] == 'published':
#            if 'parentTerm' not in entry['termRevisions'][0].keys():
#                #print("Parent of ",id,"is",entry['termRevisions'][0]['parentTerm'])
#                print("Term",id,"appears to have no parent. Patching...")
#                (header,rowdata) = entries[id]
#                # Patch it:
#                (status,jsonstr) = createTermInBCIOVocab(header, rowdata, prefix_dict, create=False, links=True, revision_msg=revisionmsg)
#                if status != 200:
#                    print(status, ": Problem patching term ",id,"with JSON: ",jsonstr)




### Delete entries that should be deleted !!!

delete_ids = [
"BCIO:036071",
"BCIO:036045",
"BCIO:036040",
"BCIO:036079",
"BCIO:050212",
"BCIO:036074",
"BCIO:036101",
"BCIO:036080",
"BCIO:036085",
"BCIO:036060",
"BCIO:036016",
"BCIO:036022",
"BCIO:036023",
"BCIO:036065",
"BCIO:036012",
"BCIO:050292",
"BCIO:036017",
"BCIO:036018",
"BCIO:036009",
"BCIO:036019",
"BCIO:036010",
"BCIO:036077",
"BCIO:036046",
"BCIO:036013",
"BCIO:050314",
"BCIO:036081",
"BCIO:036049",
"BCIO:036003",
"BCIO:036055",
"BCIO:000009",
"BCIO:036082",
"BCIO:036087",
"BCIO:036078",
"BCIO:050313",
"BCIO:036043",
"BCIO:036090",
"BCIO:036091",
"BCIO:036004",
"BCIO:036006",
"BCIO:036044",
"BCIO:036050",
"BCIO:036051",
"BCIO:036052",
"BCIO:036058",
"BCIO:036038",
"BCIO:036020",
"BCIO:036031",
"BCIO:036083",
"BCIO:036088",
"BCIO:036111",
"BCIO:036015",
"BCIO:036053"]


for id in delete_ids:
    deleteTermFromBCIOVocab(id)



## Set term status to obsolete

id = "BCIO:007162"
(status, entry) = getFromBCIOVocab(id)
entry['curationStatus']='obsolete'
entry['displayCurationStatus']='obsolete'
headers = {"accept": "application/ld+json",
               "Content-Type": "application/merge-patch+json",
               AUTH_STR:AUTH_KEY}

data = {  "id": id, "curationStatus": "obsolete", "displayCurationStatus": "obsolete" }

urlstring = BCIOVOCAB_API + PATCH_TERMS.format(id)
r = requests.patch(urlstring, json = data, headers=headers)
status = r.status_code
print(f"Set obsolete returned {r.status_code}, {r.reason}")



## Update lower-level ontology in terms

id_list = [ "BCIO:007010",
"BCIO:007163",
"BCIO:007156",
"BCIO:007164",
"BCIO:007160",
"BCIO:007161",
"BCIO:007165",
"BCIO:050332",
"BCIO:050350",
"BCIO:050333",
"BCIO:050351",
"BCIO:007166",
"BCIO:050336",
"BCIO:050334",
"BCIO:050337",
"BCIO:050335",
"BCIO:007154",
"BCIO:007016",
"BCIO:007147",
"BCIO:050342",
"BCIO:050343",
"BCIO:050344",
"BCIO:050345",
"BCIO:007135",
"BCIO:007167",
"BCIO:050340",
"BCIO:050338",
"BCIO:050341",
"BCIO:050339",
"BCIO:007168",
"BCIO:050330",
"BCIO:007141",
"BCIO:007142",
"BCIO:007033",
"BCIO:007031",
"BCIO:007032",
"BCIO:007030",
"BCIO:007029",
"BCIO:007015",
"BCIO:007159",
"BCIO:007004",
"BCIO:007051",
"BCIO:007006",
"BCIO:007079",
"BCIO:007038",
"BCIO:007036",
"BCIO:007037",
"BCIO:007035",
"BCIO:007087",
"BCIO:007034",
"BCIO:007090",
"BCIO:007091",
"BCIO:007092",
"BCIO:007012",
"BCIO:007072",
"BCIO:033000",
"BCIO:007101",
"BCIO:007136",
"BCIO:007054",
"BCIO:007134",
"BCIO:007069",
"BCIO:007169",
"BCIO:007097",
"BCIO:007096",
"BCIO:007014",
"BCIO:007081",
"BCIO:007082",
"BCIO:007043",
"BCIO:007041",
"BCIO:007042",
"BCIO:007040",
"BCIO:007039",
"BCIO:007055",
"BCIO:007151",
"BCIO:050346",
"BCIO:007057",
"BCIO:007143",
"BCIO:007146",
"BCIO:007085",
"BCIO:007170",
"BCIO:007171",
"BCIO:007099",
"BCIO:007001",
"BCIO:007002",
"BCIO:007008",
"BCIO:007172",
"BCIO:007050",
"BCIO:007158",
"BCIO:007118",
"BCIO:007119",
"BCIO:007078",
"BCIO:007173",
"BCIO:007062",
"BCIO:007174",
"BCIO:007074",
"BCIO:007175",
"BCIO:007068",
"BCIO:007152",
"BCIO:050347",
"BCIO:007067",
"BCIO:007052",
"BCIO:007065",
"BCIO:007176",
"BCIO:007063",
"BCIO:007177",
"BCIO:007178",
"BCIO:007179",
"BCIO:007180",
"BCIO:007181",
"BCIO:007182",
"BCIO:007183",
"BCIO:007184",
"BCIO:007064",
"BCIO:007058",
"BCIO:007122",
"BCIO:007185",
"BCIO:007066",
"BCIO:007017",
"BCIO:007018",
"BCIO:007020",
"BCIO:007186",
"BCIO:007098",
"BCIO:007137",
"BCIO:007061",
"BCIO:007094",
"BCIO:007075",
"BCIO:007187",
"BCIO:007200",
"BCIO:007189",
"BCIO:007195",
"BCIO:007191",
"BCIO:007192",
"BCIO:007194",
"BCIO:007193",
"BCIO:007197",
"BCIO:007199",
"BCIO:007198",
"BCIO:007204",
"BCIO:007205",
"BCIO:007202",
"BCIO:007206",
"BCIO:007207",
"BCIO:007216",
"BCIO:007208",
"BCIO:007210",
"BCIO:007211",
"BCIO:007209",
"BCIO:007212",
"BCIO:007213",
"BCIO:007215",
"BCIO:007214",
"BCIO:007219",
"BCIO:007220",
"BCIO:007218",
"BCIO:007221",
"BCIO:007222",
"BCIO:007224",
"BCIO:007223",
"BCIO:007225",
"BCIO:007226",
"BCIO:007227",
"BCIO:007228",
"BCIO:007229",
"BCIO:007230",
"BCIO:007188",
"BCIO:007201",
"BCIO:007190",
"BCIO:007196",
"BCIO:007231",
"BCIO:007232",
"BCIO:007233",
"BCIO:007234",
"BCIO:007203",
"BCIO:007217",
"BCIO:007235",
"BCIO:007236",
"BCIO:007237",
"BCIO:007238",
"BCIO:007144",
"BCIO:007070",
"BCIO:007139",
"BCIO:007157",
"BCIO:007080",
"BCIO:007138",
"BCIO:007140",
"BCIO:007073",
"BCIO:007239",
"BCIO:007026",
"BCIO:007240",
"BCIO:007250",
"BCIO:007155",
"BCIO:007022",
"BCIO:007023",
"BCIO:007027",
"BCIO:007241",
"BCIO:007246",
"BCIO:007242",
"BCIO:007243",
"BCIO:007245",
"BCIO:007244",
"BCIO:007247",
"BCIO:007249",
"BCIO:007248",
"BCIO:007145",
"BCIO:007251",
"BCIO:007253",
"BCIO:007252",
"BCIO:007254",
"BCIO:007255",
"BCIO:007264",
"BCIO:007256",
"BCIO:007258",
"BCIO:007259",
"BCIO:007257",
"BCIO:007260",
"BCIO:007261",
"BCIO:007263",
"BCIO:007262",
"BCIO:007266",
"BCIO:007267",
"BCIO:007265",
"BCIO:007268",
"BCIO:007269",
"BCIO:007271",
"BCIO:007270",
"BCIO:007272",
"BCIO:007273",
"BCIO:007276",
"BCIO:007274",
"BCIO:007275",
"BCIO:007277",
"BCIO:007278",
"BCIO:007279",
"BCIO:007281",
"BCIO:007280",
"BCIO:007282",
"BCIO:007283",
"BCIO:007053",
"BCIO:007019",
"BCIO:007021",
"BCIO:007084",
"BCIO:007284",
"BCIO:007153",
"BCIO:007056",
"BCIO:007060",
"BCIO:050331",
"BCIO:007285",
"BCIO:007292",
"BCIO:007286",
"BCIO:007289",
"BCIO:007287",
"BCIO:007288",
"BCIO:007290",
"BCIO:007291",
"BCIO:007293",
"BCIO:007296",
"BCIO:007294",
"BCIO:007295",
"BCIO:007297",
"BCIO:007298",
"BCIO:007150",
"BCIO:050348",
"BCIO:050349",
"BCIO:007011",
"BCIO:007299",
"BCIO:007013",
"BCIO:007024",
"BCIO:007025",
"BCIO:007003",
"BCIO:007100",
"BCIO:007300",
"BCIO:007301",
"BCIO:007005",
"BCIO:007028",
"BCIO:007095",
"BCIO:007302",
"BCIO:007303",
"BCIO:007076",
"BCIO:007089",
"BCIO:007077",
"BCIO:007121",
"BCIO:007120" ]


for id in id_list:

    headers = {"accept": "application/ld+json",
                "Content-Type": "application/merge-patch+json",
                AUTH_STR:AUTH_KEY}

    data = {"id": id, "lowerLevelOntology": "behaviour change technique" }

    urlstring = BCIOVOCAB_API + PATCH_TERMS.format(id)
    r = requests.patch(urlstring, json=data, headers=headers)
    status = r.status_code
    print(f"Set lower level ontology returned {r.status_code}, {r.reason}")

