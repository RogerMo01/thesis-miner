import json

data: dict = dict()

# Open and read the JSON files
with open('t1_details.json', 'r') as file:
    data.update(json.load(file))
with open('t2_details.json', 'r') as file:
    data.update(json.load(file))

# Save monographs
with open('monographs.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4)