import json


def fix_syn(syn: str) -> str:
    """Fix wrong or unnecesary characters in synonyms"""

    # Remove unnecesary spaces
    while syn.startswith(" "):
        syn = syn.removeprefix(" ")
    while syn.endswith(" "):
        syn = syn.removesuffix(" ")

    # Replace (1.) by (I.)
    replaced_syn = syn.replace("1.", "I.")
    syn = replaced_syn

    return syn

def format_synonyms(monographs: dict):
    """Returns a dict, using plant names as key, and each key store the list of synonyms"""
    response_dict = dict()

    for plant, monograph in monographs.items():
        response_dict[plant] = []

        syns_raw = monograph['Sy']

        # Separate syns by (, or ;)
        count = 1
        temp_syn = ""
        for char in syns_raw:
            if count == len(syns_raw) or char == ',' or char == ';':

                response_dict[plant].append(fix_syn(temp_syn))
                temp_syn = ""
            else:
                temp_syn += char

            count += 1


        
    return response_dict

    


# Open and read the JSON file
with open('t1_monographs.json', 'r') as file:
    data: dict = json.load(file)

syns = format_synonyms(monographs=data)


# Update changes
new_data = data.copy()
for plant, _ in data.items():
    new_data[plant]['Sy'] = syns[plant]

# Save changes
with open('t1_monographs_formated.json', 'w', encoding='utf-8') as f:
    json.dump(new_data, f, indent=4)

