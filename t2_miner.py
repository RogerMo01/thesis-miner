import json
import pymupdf
from utils import levenshtein_distance

UPPERCASE_LIST = ['L', 'Ll', 'M', 'N', 'Ñ', 'O', 'Ó', 'P', 'Q', 'R', 'S', 'T', 'U', 'Ú', 'V', 'W', 'X', 'Y', 'Z']

doc = pymupdf.open("tomo2.pdf")


def load_names():
    """Returns the list of plants in the book"""
    plants = []

    for page in doc.pages(2, 21):
        blocks = page.get_text("dict", flags=11)["blocks"]

        for b in blocks:  # iterate through the text blocks
            for l in b["lines"]:  # iterate through the text lines
                for token in l['spans']:  # iterate through the text tokens
                    text = token['text']
                    if text.lower() != "bibliografía" and text != "Índice de contenido" and not text in UPPERCASE_LIST:
                        plants.append(text)
        
    plants.append("Zarzaparrilla*") # Alone in next page
    plants.append("Zarzaparrilla de palito") # Not in index

    return plants


def load_monographs(plants: list[str]):
    """Return the dictionary of monographs"""
    response_dict = dict()

    current_index = 0
    current_monograph = ""
    
    for page in doc.pages(23, 459):
        blocks = page.get_text("dict", flags=11)["blocks"]

        for b in blocks:  # iterate through the text blocks
            for l in b["lines"]:  # iterate through the text lines
                for token in l['spans']:  # iterate through the text tokens
                    text = token['text']

                    if current_index < len(plants_names) and text == plants_names[current_index]:
                        # Save current plant monograph
                        if current_index > 0:
                            response_dict[plants_names[current_index-1]] = current_monograph

                        current_index += 1
                        current_monograph = ""
                    else:
                        current_monograph += text
                if len(current_monograph) > 0 and current_monograph[-1] != " ": current_monograph += " "

        response_dict[plants_names[-1]] = current_monograph

    return response_dict


# Flags
FLAGS_TRIGGERS = ['SINÓNIMOS: ', 'OTROS NOMBRES VULGARES: ', 'HÁBITAT Y DISTRIBUCIÓN: ', 'DESCRIPCIÓN BOTÁNICA: ', 'COMPOSICIÓN: ', 'PARTES EMPLEADAS: ', 'PROPIEDADES: ', 'APLICACIONES: ', 'CULTIVO: ', 'Bibliografía ', 'BIBLIOGRAFÍA ']
FLAGS = ['Sy', 'Vul', 'Hab', 'Des', 'Cmp', 'Use', 'Pro', 'App', 'Cul', 'Bib', 'Bb']

def find_flag(potential_flag: str, start_index: int = 0) -> tuple[bool, int]:
    '''Finds or not, potential flag in flags list, and returns also its index'''
    for i in range(start_index, len(FLAGS_TRIGGERS)):
        if levenshtein_distance(potential_flag, FLAGS_TRIGGERS[i]) <= 2:
            return True, i
    return False, -1

def prefix_posibility(prefix: str):
    for trigger in FLAGS_TRIGGERS:
        trigger_prefix = trigger[0:len(prefix)]
        if levenshtein_distance(prefix, trigger_prefix) <= 2: return True
    return False

def parse_monography(raw: str) -> dict:
    current_flag = "Sc"
    current_index = -1
    potential_flag = ''
    tokens = raw.split(' ')

    response = {'Sc': "", 'Sy': "", 'Vul': "", 'Hab': "", 'Des': "", 'Cmp': "", 'Use': "", 'Pro': "", 'App': "", 'Cul': "", 'Bib': "", 'Bb': ""}
    for token in tokens:
        token += " "

        if prefix_posibility(potential_flag + token):
            potential_flag += token
            found, flag_index = find_flag(potential_flag, current_index+1)
            if found:
                current_flag = FLAGS[flag_index]
                response[current_flag] = ""
                potential_flag = ""

        else:
            if potential_flag != "":
                response[current_flag] += potential_flag
                potential_flag = ""
            response[current_flag] += token
    
    return response



def fix_errors_manually(monographs: dict[str, dict]):
    monographs['Manzanilla*']['Sc'] = "Matricaria chamomilla L. Fam. COMPUESTAS"
    monographs['Manzanilla*']['Cul'] = "En 1939 fue introducida en Cuba la especie M. chamomilla L., llamada camomilla y manzanilla dulce o manzanilla alemana y desde entonces se ha venido experimentando con la aclimatación y el cultivo de esta especie en la Estación Experimental Agronómica de Santiago de las Vegas, en La Habana, Cuba. " + monographs['Manzanilla*']['Cul']






plants_names = load_names()
raw_monographs = load_monographs(plants_names)

# Group plants
monographs = dict()
for plant in plants_names:
    mono = parse_monography(raw_monographs[plant])
    print(f"Parsed: {plant}")
    monographs[plant] = mono

fix_errors_manually

# Unify biblios
for plant, _ in monographs.items():
    monographs[plant]['Bib'] += monographs[plant]['Bb']
    del monographs[plant]['Bb']

# Fix puntual stuff
fix_errors_manually(monographs)

# Save changes
with open('t2_monographs.json', 'w', encoding='utf-8') as f:
    json.dump(monographs, f, indent=4)
