import json
import pymupdf

UPPERCASE_LIST = ['A', 'Á', 'B', 'C', 'D', 'E', 'É', 'F', 'G', 'H', 'I', 'Í', 'J', 'K', 'L', 'M', 'N', 'Ñ', 'O', 'Ó', 'P', 'Q', 'R', 'S', 'T', 'U', 'Ú', 'V', 'W', 'X', 'Y', 'Z']
UPPERCASE_BOOK_LIST = ['A', 'B', 'Cc', 'Ch', 'D', 'E', 'F', 'G', 'H', 'J']

START_PAGE = 199
END_PAGE = 620

doc = pymupdf.open("tomo1.pdf")


def filter_name(potential_name: str, discart_list: list[str]) -> bool:
    # Start with uppercase
    if not potential_name[0] in UPPERCASE_LIST and not potential_name[0] == '(':
        discart_list.append(potential_name)
        return False
    # Has at leat 3 letters
    if len(potential_name.replace(" ", "")) < 3:
        discart_list.append(potential_name)
        return False
    
    for i in range(len(potential_name) - 1):
        if potential_name[i].isupper() and potential_name[i + 1].isupper():
            discart_list.append(potential_name)
            return False
        
    return True

def add_missing_plants(plants: list[str]):
    if len(plants) == 0: return

    if plants[len(plants)-1] == "Bosborín ":
        plants.append("Botija ")
    elif plants[len(plants)-1] == "Botón de oro ":
        plants.append("Brasilete ")
    elif plants[len(plants)-1] == "Gavilán ":
        plants.append("Genciana de la tierra ")




def parse():
    plants: list[str] = []
    discart_list: list[str] = []

    for page in doc.pages(199, 620):
        blocks = page.get_text("dict", flags=11)["blocks"]

        for b in blocks:  # iterate through the text blocks
            for l in b["lines"]:  # iterate through the text lines
                plant_name = ""
                plant_name_flag = False

                for token in l['spans']:  # iterate through the text tokens
                    text: str = token['text']
                    size = token['size']

                    if size > 12:
                        plant_name += text
                        plant_name_flag = True
                    else:
                        plant_name_flag = False
                        plant_name = ""


                if plant_name_flag:
                    if filter_name(plant_name, discart_list):
                        # Save parenthesis in previous plant
                        if plant_name.startswith("("):
                            plants[len(plants)-1] += plant_name
                        else:
                            plants.append(plant_name)

                add_missing_plants(plants)


    # Save to json
    names = plants
    names_corrected = []
    for n in names:
        if n == 'GuaguasíÍ ':
            names_corrected.append("Guaguasí ")
        elif n == 'Gúiira cimarrona ':
            names_corrected.append("Güira cimarrona ")
        elif n == 'Gitirito de pasión ':
            names_corrected.append("Güirito de pasión ")
        elif n == 'Gúliro amargo ':
            names_corrected.append("Güiro amargo ")
        elif n == 'Jagiley ':
            names_corrected.append("Jagüey ")
        else:
            names_corrected.append(n)
            
    with open('t1_monographs.json', 'w', encoding='utf-8') as f:
        json.dump({'names': plants, 'names_corrected': names_corrected}, f, indent=4)


    print(f"\n\n🌱 Names({len(plants)}):")
    for i in plants:
        print(i)

    print(f"\n\n❌ Discarted({len(discart_list)}):")
    for i in discart_list:
        print(i)



parse()