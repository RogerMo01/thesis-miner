import json

data: dict = dict()

# Open and read the JSON files
with open('t1_details.json', 'r') as file:
    data.update(json.load(file))
with open('t2_details.json', 'r') as file:
    data.update(json.load(file))

# Fill new format dictionary
new_format_data = dict()
for k, v in data.items():
    new_format_data[k] = dict()
    new_format_data[k]['genus'] = v['Sc']['genus']
    new_format_data[k]['species'] = v['Sc']['species']
    new_format_data[k]['authors'] = v['Sc']['authors']
    new_format_data[k]['var'] = v['Sc']['var']
    new_format_data[k]['subsp'] = v['Sc']['subsp']
    new_format_data[k]['f'] = v['Sc']['f']
    new_format_data[k]['family'] = v['Sc']['family']
    new_format_data[k]['subfamily'] = v['Sc']['subfamily']
    new_format_data[k]['Sy'] = v['Sy']

    new_format_data[k]['Vul'] = []
    for country, names in v['Vul'].items():
        for name in names:
            new_format_data[k]['Vul'].append(f"{name} ({country})")

    new_format_data[k]['Hab'] = v['Hab']
    new_format_data[k]['Des'] = v['Des']
    new_format_data[k]['Cmp'] = v['Cmp']
    new_format_data[k]['Use'] = v['Use']
    new_format_data[k]['Pro'] = v['Pro']
    new_format_data[k]['App'] = v['App']
    new_format_data[k]['Cul'] = v['Cul']
    new_format_data[k]['Bib'] = v['Bib']



# Save monographs
with open('monographs.json', 'w', encoding='utf-8') as f:
    json.dump(new_format_data, f, indent=4)