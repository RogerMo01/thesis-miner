import pymupdf
from fitz import Document, Page
import json
from utils import levenshtein_distance
from detailed_parser import parse_detailed_sections, del_spaces
from outliers import solve_1_outliers, solve_2_outliers

tomo1: Document = pymupdf.open("t1.pdf")
tomo2: Document = pymupdf.open("t2.pdf")

T1_M_START = 106
T1_M_END = 561
T2_M_START = 23
T2_M_END = 458

# Start plant monograph by name triggers
def t1_start_plant_trigger(s: dict):
    return s['font'] == "PalatinoLinotype-Bold" and s['size'] == 16
def t2_start_plant_trigger(s: dict):
    return s['font'] == "LiberationSerif-Bold" and s['size'] > 24.99 and s['size'] < 25


def check_type_clarification(span, current_plant: str, progressive_clarified_name: str, clarification_type_flag: bool, result: dict) -> bool:
    text: str = span['text']
    progressive_clarified_name += text

    if current_plant.startswith("Espuela"):
        print(span)

    if clarification_type_flag and progressive_clarified_name == "" and not progressive_clarified_name.startswith("("):
        return False

    # Add clarification type to name
    if clarification_type_flag and progressive_clarified_name.startswith("(") and progressive_clarified_name.endswith(")"):
        del result[current_plant]
        result[f"{progressive_clarified_name}"] = ""
        print(f"{current_plant} clarified as {progressive_clarified_name}")
        return False

    if clarification_type_flag and progressive_clarified_name != "":
        return True
    
    return False
    


    


def split_monographs(t: int):
    """Returns a dictionary with plant names as key, and each one contains the list of spans corresponding to monographs"""
    doc = tomo1 if t == 1 else tomo2
    start_page = T1_M_START if t == 1 else T2_M_START
    end_page = T1_M_END if t == 1 else T2_M_END
    trigger = lambda text: t1_start_plant_trigger(text) if t == 1 else t2_start_plant_trigger(text)

    result: dict[str, list] = dict()

    current_plant = ""
    for page in doc.pages(start_page, end_page):
        blocks = page.get_text("dict", flags=11)["blocks"]
        for b in blocks:
            for l in b["lines"]:
                for s in l['spans']:
                    text = s['text']

                    if trigger(s):
                        if text in result:
                            temp = result[text]
                            del result[text]
                            result[f"{text} (1)"] = temp
                            text = f"{text} (2)"
                        result[text] = []
                        current_plant = text
                    else:
                        if current_plant != "":
                            result[current_plant].append(s)
    return result






def extract_raw_monograph(plant: str, spans: list):
    extra_name_flag = False
    extra_name = ""

    return_data = {'Sc': "", 'Sy': "", 'Vul': "", 'Hab': "", 'Des': "", 'Cmp': "", 'Use': "", 'Pro': "", 'App': "", 'Cul': "", 'Bib': "", 'Bb': ""}
    FLAGS_TRIGGERS = ['SINÓNIMOS: ', 'OTROS NOMBRES VULGARES: ', 'HÁBITAT Y DISTRIBUCIÓN: ', 'DESCRIPCIÓN BOTÁNICA: ', 'COMPOSICIÓN: ', 'PARTES EMPLEADAS: ', 'PROPIEDADES: ', 'APLICACIONES: ', 'CULTIVO: ', 'Bibliografía ', 'BIBLIOGRAFÍA ']

    content = ""

    for s in spans:
        text: str = s['text']

        ########## Fix extra names for equal plant names ##########
        if s == spans[0] and text.startswith("("):
            extra_name_flag = True

        if extra_name_flag:
            extra_name += text

            if extra_name.endswith(")"):

                old_extra = ""
                if plant.endswith("(1)"): old_extra = "(1)"
                if plant.endswith("(2)"): old_extra = "(2)"

                plant = plant.removesuffix(old_extra)
                plant = f"{plant}{extra_name}"
                extra_name_flag = False
        ############################################################

        ########## Get all monograph content in a string ###########
        else:
            if len(content) > 0 and content[-1] != " " and len(text) > 0 and not text[0] in [':', '.', ',', ';']: content += " "
            content += text
        ############################################################

    return plant, content







# Flags
FLAGS_TRIGGERS = ['SINÓNIMOS:', 'OTROS NOMBRES VULGARES:', 'HÁBITAT Y DISTRIBUCIÓN:', 'DESCRIPCIÓN BOTÁNICA:', 'COMPOSICIÓN:', 'PARTES EMPLEADAS:', 'PROPIEDADES:', 'APLICACIONES:', 'CULTIVO:', 'Bibliografía', 'BIBLIOGRAFÍA ']
FLAGS = ['Sy', 'Vul', 'Hab', 'Des', 'Cmp', 'Use', 'Pro', 'App', 'Cul', 'Bib', 'Bb']


def prefix_posibility(prefix: str):
    for trigger in FLAGS_TRIGGERS:
        trigger_prefix = trigger[0:len(prefix)]
        if levenshtein_distance(prefix, trigger_prefix) <= 2: return True
    return False

def find_flag(potential_flag: str, start_index: int = 0) -> tuple[bool, int]:
    '''Finds or not, potential flag in flags list, and returns also its index'''
    for i in range(start_index, len(FLAGS_TRIGGERS)):
        if levenshtein_distance(potential_flag, FLAGS_TRIGGERS[i]) <= 2:
            return True, i
    return False, -1

def parse_sections(raw: str):
    """Returns the dictionary that constains the parsed monography"""
    current_flag = "Sc"
    current_index = -1
    potential_flag = ''
    tokens = raw.split(' ')

    response = {'Sc': "", 'Sy': "", 'Vul': "", 'Hab': "", 'Des': "", 'Cmp': "", 'Use': "", 'Pro': "", 'App': "", 'Cul': "", 'Bib': "", 'Bb': ""}
    for token in tokens:
        if token.strip() == "":
            continue

        token += " "

        if len(potential_flag + token) > 3 and any(c.isalpha() for c in token) and prefix_posibility(potential_flag + token):
            potential_flag += token
            found, flag_index = find_flag(potential_flag, current_index+1)

            if found:
                # Format current content
                response[current_flag] = del_spaces(response[current_flag])

                current_flag = FLAGS[flag_index]
                response[current_flag] = ""
                potential_flag = ""

        else:
            if potential_flag != "":
                response[current_flag] += potential_flag
                potential_flag = ""
            response[current_flag] += token
    
    # Unify bibliographs
    response['Bib'] += response['Bb']
    del response['Bb']

    return response






########################################################################


SELECTOR = 1

splitted_monographs = split_monographs(SELECTOR)


# Extract raw content from monographs
monographs = dict()
for plant, spans in splitted_monographs.items():
    p, s = extract_raw_monograph(plant, spans)
    print(f"Extracted: {plant}")
    monographs[p]= s

# Save raw monographs
with open(f't{SELECTOR}_raw.json', 'w', encoding='utf-8') as f:
    json.dump(monographs, f, indent=4)



# Extract parsed content from monographs
for plant, content in monographs.items():
    parsed_content = parse_sections(content)
    print(f"Parsed: {plant}")
    monographs[plant] = parsed_content

# Save parsed monographs
with open(f't{SELECTOR}_parsed.json', 'w', encoding='utf-8') as f:
    json.dump(monographs, f, indent=4)



# Extract parsed detailed content from monographs
monographs = parse_detailed_sections(SELECTOR, monographs)

# Solve outliers hardcoded
if SELECTOR == 1:
    solve_1_outliers(monographs)
elif SELECTOR == 2:
    solve_2_outliers(monographs)


# Save detailed parsed monographs
with open(f't{SELECTOR}_details.json', 'w', encoding='utf-8') as f:
    json.dump(monographs, f, indent=4)