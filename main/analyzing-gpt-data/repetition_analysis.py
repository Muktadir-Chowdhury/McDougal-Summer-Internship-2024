import json 

with open('organized-datadict-20240808.json') as file:
    data_dict = json.load(file)

with open('vocabularygpt.json') as file:
    vocab_dict = json.load(file)

results = {}

# is the category or tag in the controlled vocabulary?
def in_controlled_vocab(category, value=None):
    if category not in vocab_dict:
        return False
    if bool(value) and value not in vocab_dict[category]:
        return False
    return True

def two_matches(q1, q2, q3): # tags that match twice or more
    return list((set(q1) & set(q2)) | (set(q1) & set(q3)) | (set(q2) & set(q3)))

def perfect_matches(q1, q2, q3): # tags that perfectly match altogether
    return list(set(q1) & set(q2) & set(q3))
    
for model_id in data_dict:
    results[model_id] = dict()
    for file_category in data_dict[model_id]:
        results[model_id][file_category] = dict()
        for file_name in data_dict[model_id][file_category]:
            if "readme" in file_name.lower():
                continue # exclude readme
            content = data_dict[model_id][file_category][file_name]

            everything_lists = {category:[] for category in vocab_dict}
            two_lists = {category:[] for category in vocab_dict}
            perfect_lists = {category:[] for category in vocab_dict}

            queryone = {category:[] for category in vocab_dict}
            querytwo = {category:[] for category in vocab_dict}
            querythree = {category:[] for category in vocab_dict}

            for i in range(3): # three queries
                query_content = content[str(i+1)]
                for category in query_content:
                    if in_controlled_vocab(category):
                        query_tags = [tag for tag in query_content[category] if in_controlled_vocab(category, value=tag)]
                        if i == 0:
                            queryone[category] = query_tags
                        if i == 1:
                            querytwo[category] = query_tags
                        if i == 2:
                            querythree[category] = query_tags

            for category in vocab_dict:
                querycat_1 = queryone[category]
                querycat_2 = querytwo[category]
                querycat_3 = querythree[category]

                everything_lists[category] = list(set(querycat_1 + querycat_2 + querycat_3))
                two_lists[category] = two_matches(querycat_1, querycat_2, querycat_3)
                perfect_lists[category] = perfect_matches(querycat_1, querycat_2, querycat_3)
            
            results[model_id][file_category][file_name] = {"everything_lists": everything_lists, "two_lists": two_lists, "perfect_lists": perfect_lists}

with open("consistency-results.json", 'w') as file:
    json.dump(results, file, indent=6)

print("done!!!")

