import json

with open("consistency-stats-amount.json") as file:
    data = json.load(file)

# #find perfect to everything ratio per file
# results = dict()

# for model_id, rules in data.items():
#     results[model_id] = rules
#     for rule, filenames in rules.items():
#         results[model_id][rule] = filenames
#         for filename, values in filenames.items():
#             results[model_id][rule][filename] = round(((values["perfect_lists"]/values["everything_lists"]) * 100), 2)

# with open("data\\consistency\\consistency-perfect-perfile.json", 'w') as file:
#     json.dump(results, file, indent=4)

# # find perfect to everythin ratio per rule
# results = dict()

# for model_id, rules in data.items():
#     results[model_id] = rules
#     for rule, filenames in rules.items():
#         everything = 0
#         perfect = 0
#         for filename, values in filenames.items():
#             everything += values["everything_lists"]
#             perfect += values["perfect_lists"]
#         print(everything, perfect, model_id)
#         results[model_id][rule] = round(((perfect/everything) * 100), 2)

# with open("data\\consistency\\consistency-perfect-perrule.json", 'w') as file:
#     json.dump(results, file, indent=4)

# find perfect to everything ratio per category
with open("data\\unified_data\\everything_unified.json") as file:
    everything_data = json.load(file)

with open("data\\unified_data\\perfect_unified.json") as file:
    perfect_data = json.load(file)

results = dict()

for model_id, categories in everything_data.items():
    results[model_id] = categories
    for category, values in categories.items():
        try:
            score = round(((len(perfect_data[model_id][category])/len(values)) * 100), 2)
        except ZeroDivisionError:
            score = 100
        results[model_id][category] = score

with open("data\\consistency\\consistency-perfect-percat.json", 'w') as file:
    json.dump(results, file, indent=4)

print("Code is finished!!!")