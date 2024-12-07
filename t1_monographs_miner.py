import json
import pymupdf
from utils import levenshtein_distance

UPPERCASE_LIST = ['A', 'Á', 'B', 'C', 'D', 'E', 'É', 'F', 'G', 'H', 'I', 'Í', 'J', 'K', 'L', 'M', 'N', 'Ñ', 'O', 'Ó', 'P', 'Q', 'R', 'S', 'T', 'U', 'Ú', 'V', 'W', 'X', 'Y', 'Z']
UPPERCASE_BOOK_LIST = ['A', 'B', 'Cc', 'Ch', 'D', 'E', 'F', 'G', 'H', 'J']

START_PAGE = 199
END_PAGE = 621

doc = pymupdf.open("tomo1.pdf")


def load_names():
    with open('t1_plants.json', 'r') as file:
        data = json.load(file)
    return data['names'], data['names_corrected']

def skips_this(name: str, skips: dict[str, int]):
    try:
        if skips[name] > 0:
            skips[name] -= 1
            return True
    except KeyError:
        pass
    return False

def extract_tokenized_plants():
    plants_names, corrected_plants_names = load_names()
    next_index = 0
    next_plant = plants_names[next_index]
    current_plant = ""
    skips = {'Artemisa ': 1}


    tokenized_plants = dict()

    for page in doc.pages(START_PAGE, END_PAGE):
        blocks = page.get_text("dict", flags=11)["blocks"]

        potential_name = ""
        potential_tokens = []

        for b in blocks:  # iterate through the text blocks
            for l in b["lines"]:  # iterate through the text lines
                for token in l['spans']:  # iterate through the text spans

                    skip = skips_this(potential_name + token['text'], skips)
                    
                    if any(plant.startswith(potential_name + token['text']) for plant in plants_names[next_index:]) and not skip:
                        # Keep extending prefix
                        potential_name += token['text']
                        potential_tokens.append(token)

                        if potential_name == next_plant:
                            # Found monograph
                            current_plant = next_plant

                            tokenized_plants[current_plant] = []

                            potential_name = ""
                            next_index+=1
                            print(f"Tokenized: {next_plant}")
                            next_plant = plants_names[next_index] if next_index < len(plants_names) else ""
                        

                    else:
                        if potential_name != "" and current_plant != "":
                            tokenized_plants[current_plant].extend(potential_tokens)

                            # Reset prefix
                            potential_name = ""

                        # Hacer algo con los tokens que forman parte de la monografia
                        if current_plant != "":
                            tokenized_plants[current_plant].append(token)

    return tokenized_plants



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
    


def extract_monographs(tokenized_plants):
    monographs = dict()

    for plant, tokens in tokenized_plants.items():
        current_flag = "Sc"
        current_index = -1
        potential_flag = ''

        monographs[plant] = {'Sc': "", 'Sy': "", 'Vul': "", 'Hab': "", 'Des': "", 'Cmp': "", 'Use': "", 'Pro': "", 'App': "", 'Cul': "", 'Bib': "", 'Bb': ""}
        for token in tokens:

            if prefix_posibility(potential_flag + token['text']):
                # Keep extending prefix
                potential_flag += token['text']

                found, flag_index = find_flag(potential_flag, current_index+1)
                if found:
                    current_flag = FLAGS[flag_index]
                    monographs[plant][current_flag] = ""
                    potential_flag = ""

            else:
                if potential_flag != "":
                    monographs[plant][current_flag] += potential_flag

                    # Reset prefix
                    potential_flag = ""

                monographs[plant][current_flag] += token['text']

        print(f'Extracted: {plant}')

    return monographs



def fix_errors_manually(monographs: dict[str, dict]):
    # Sticked sections
    monographs['Almácigo']['Sy'] = "Bursera gummifera L., Elaphrium simaruba (L.) Rose, Pistacia simaruba L., Terebinthus simaruba W. F. Wright."
    monographs['Almácigo']['Vul'] = "Azucarero, aceitero, alm\u00e1cigo colorado (Cuba); gum tree, turpentine, West Indian birch (Florida y Antillas Inglesas); chaca piocha, palo mulato, palo colorado, quiote, zongolica (M\u00e9xico); alm\u00e1cigo encarnado, archip\u00edn (Puerto Rico); ji\u00f1ocuabe (Nicaragua); carana, ji\u00f1ocuave (Costa Rica); chinacahuite, jicote chino, palo chino (Guatemala); cop\u00f3n, palo chino (Honduras); indio desnudo, pellejo de indio (Guayana); caratero (Colombia)."

    monographs['Chichicate ']['Sy'] = "Urtica baccifera L."
    monographs['Chichicate ']['Vul'] = "Chichicastre: hoja de chichicastre, jamo (Cuba); ortiga blanca, ortiga de la tierra (Puerto Rico); pringamozo (Venezuela); nettle (Antillas Inglesas); chichacastle, ortiga de caballo (M\u00e9xico); chichicazte (Guatemala); chichicazte nigua (El Salvador); ortiga (Panam\u00e1); guaina, pringamosa (Colombia)."

    monographs['Guamá candelón ']['Sy'] = "Erythrina piscipula L., 1. piscipula (L.) Hitch., P. erythrina L."
    monographs['Guamá candelón ']['Vul'] = "Candel\u00f3n, guam\u00e1 hediondo (Cuba); dogwood (Jamaica); ventura (Puerto Rico); fish poison (Florida); palo emborrachador (Venezuela); bois de chiens, bois enivrent, mort a poissons (Antillas Francesas); colango naranga (Brasil); cocuite, chijol, flor de papagallo, habi, javin (M\u00e9xico)"




tokenized_plants = extract_tokenized_plants()
monographs = extract_monographs(tokenized_plants)

# Unify biblios
for plant, _ in monographs.items():
    monographs[plant]['Bib'] += monographs[plant]['Bb']
    del monographs[plant]['Bb']

# Fix puntual stuff
fix_errors_manually(monographs)


with open('t1_monographs.json', 'w', encoding='utf-8') as f:
    json.dump(monographs, f, indent=4)
