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
      './Source/inputs/BCIO_Source.xlsx',
      './MechanismOfAction/inputs/BCIO_MoA.xlsx',
      './Behaviour/BCIO_behaviour.xlsx',
      './Setting/inputs/Setting.xlsx',
      './ModeOfDelivery/inputs/MoD.xlsx',
      './BehaviourChangeTechniques/inputs/BCIO_BehaviourChangeTechniques.xlsx',
      './StyleOfDelivery/BCIO_StyleOfDelivery.xlsx']


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

