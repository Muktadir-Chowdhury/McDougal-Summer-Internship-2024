import json 
import requests 

with open('data\\unified_data\\everything_unified.json') as file:
    data_dict = json.load(file)


key_map = {"celltypes": "neurons", "currents": "currents", "genes":"gene", "modelconcepts": "model_concept", "modeltypes": "model_type", "receptors":"receptors", "regions":"region", "simenvironments":"modeling_application","transmitters":"neurotransmitters"}
content_url = lambda id: "https://modeldb.science/api/v1/models/" + str(id)

def structure(content):
    structured = dict()
    for key, value in key_map.items():
        try:
            structured[key] = [item["object_name"] for item in content[value]["value"]]
        except KeyError:
            structured[key] = []
    return structured

modeldb_dict = dict()

with requests.session() as session:
        for model_id, categories in data_dict.items():
            content = session.get(content_url(model_id)).json()
            api_data = structure(content)
            modeldb_dict[model_id] = dict()
            for category in api_data:
                modeldb_dict[model_id][category] = dict()
                print(categories, model_id)
                for tag in api_data[category]:
                    if tag in categories[category]:
                        modeldb_dict[model_id][category][tag] = 1
                    else:
                        modeldb_dict[model_id][category][tag] = -1

with open('modeldb_score_dataset.json', 'w') as file:
    json.dump(modeldb_dict, file, indent=4)
                
print("code finished!!!")

