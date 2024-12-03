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

def format_synonyms(monographs: dict) -> list[str]:
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

    

def format_scientific_name(monographs: dict) -> dict[str, dict]:
    """Returns a dict, using plant names as key, and each key store a dictionary with scientifi name information"""
    response_dict = dict()
    fileds = ['raw', 'genus', 'species', 'authors', 'var', 'subsp', 'f', 'subfamily', 'family']

    for plant, monograph in monographs.items():
        response_dict[plant] = dict()

        sc_raw: str = monograph['Sc']

        response_dict[plant]['raw'] = sc_raw

        current_flag_i = 0
        props = {'var.':"var", 'Subfam.':"subfamily", 'Fam.':"family"}
        current_prop = 'authors'
        current_str = ""
        flags = ['var.', 'Subfam.', 'Fam.']
        tokens = sc_raw.split(" ")
        for i, token in enumerate(tokens):
            if i == 0:
                # Gender
                response_dict[plant]['genus'] = token
            elif i == 1:
                # Species
                response_dict[plant]['species'] = token
            else:
                # Flags
                if token in flags or i == len(tokens)-1:
                    response_dict[plant][current_prop] = current_str
                    current_prop = props[token] if not i == len(tokens)-1 else ""
                    current_str = ""

                else:
                    current_str += f"{token} "

            response_dict[plant]['subsp'] = ""
            response_dict[plant]['f'] = ""

        # Fill with empty fields
        for field in fileds:
            if not field in response_dict[plant]: response_dict[plant][field] = ""
        
        # Set Family names in uppercase
        response_dict[plant]['family'] = response_dict[plant]['family'].capitalize()
        response_dict[plant]['subfamily'] = response_dict[plant]['subfamily'].capitalize()

    return response_dict



def fix_vulgar_name(name: str) -> str:
    def remove_prefix(name_: str) -> str:
        prefix = ""
        for i in name_:
            if i in [' ', '.', ';']:
                prefix += i
            else: break
        return name_.removeprefix(prefix)
    
    name = remove_prefix(name)
    name = name[::-1]
    name = remove_prefix(name)
    name = name[::-1]
    return name

def extract_vulgar_names(raw: str) -> tuple[str, list[str]]:
    region = "No Especificada"

    # Extract region
    temp_region = ""
    found = False
    for c in raw:
        if c == '(':
            found = True
        elif c == ')':
            region = temp_region
            break
        elif found:
            temp_region += c

    raw = raw.replace(f"({region})", "")

    # Extract names
    names = [fix_vulgar_name(x) for x in raw.split(',')]
    names = [name for name in names if name != '']
    return region, names


def split_regions(raw: str) -> str:
    response = []

    potential = ""
    for c in raw:
        potential += c
        if c == ')':
            response.append(potential)
            potential = ""
    
    return response


def format_other_vulgar_names(monographs: dict):
    """Returns a dict, using plant names as key, and each key store a dictionary with other vulgar names by region"""
    response_dict = dict()
    unknown_only_region = ["Avellano de costa "]

    for plant, monograph in monographs.items():
        response_dict[plant] = dict()

        vul_raw: str = monograph['Vul']

        splitted_by_region = split_regions(vul_raw)

        # Vulgar names of one unespecified region
        if plant in unknown_only_region:
            splitted_by_region = [vul_raw]

        for names_in_region in splitted_by_region:
            region, names = extract_vulgar_names(names_in_region)
            response_dict[plant][region] = names
    
    return response_dict


# Open and read the JSON file
with open('t1_monographs.json', 'r') as file:
    data: dict = json.load(file)

syns = format_synonyms(monographs=data)
sc_names = format_scientific_name(monographs=data)
vul_names = format_other_vulgar_names(monographs=data)

# Update changes
new_data = data.copy()
for plant, _ in data.items():
    new_data[plant]['Sy'] = syns[plant]
    new_data[plant]['Sc'] = sc_names[plant]
    new_data[plant]['Vul'] = vul_names[plant]

# Save changes
with open('t1_monographs_formated.json', 'w', encoding='utf-8') as f:
    json.dump(new_data, f, indent=4)

