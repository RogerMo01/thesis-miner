import json
import pdfplumber

start_page = 34
end_page = 71

FILE = "t1.pdf"

# Proportions are calculated using the base page size (18cm x 27.15cm)
W, H = 18, 27.15
class Dimensions:
    def __init__(self):
        with pdfplumber.open(FILE) as pdf:
            page = pdf.pages[start_page]
            self.height = page.height
            self.width = page.width
            pdf.close()
            
        cm_5 = self._proportion_calculator(5)
        cm_2_3 = self._proportion_calculator(2.3)
        cm_6_65 = self._proportion_calculator(6.65)
        cm_11_35 = self._proportion_calculator(11.35)
        
        self.firstpage_start_h = 0 + cm_5
        # self.firstpage_start_h = 0 + cm_2_3
        self.defaultpage_start_h = 0 + cm_2_3
        
        self.defaultpage_third_sep_1 = cm_6_65
        self.defaultpage_third_sep_2 = cm_11_35
        

    
    def _proportion_calculator(self, value_cm: float) -> float:
        return ((value_cm * self.width) / W)
        
        
        
    
    
        


def extract_raw_text() -> str:
    d = Dimensions()
    full_text = ""
    with pdfplumber.open(FILE) as pdf:
        firstpage = True
        for page_num in range(start_page, end_page):
            page = pdf.pages[page_num]
            print(f"\nPage {page_num+1}")
            
            page_start_h = d.defaultpage_start_h
            if firstpage:
                page_start_h = d.firstpage_start_h
                firstpage = False
            
            # Extraer texto de cada columna
            col1 = page.within_bbox((0, page_start_h, d.defaultpage_third_sep_1, page.height)).extract_text()
            col2 = page.within_bbox((d.defaultpage_third_sep_1, page_start_h, d.defaultpage_third_sep_2, page.height)).extract_text()
            col3 = page.within_bbox((d.defaultpage_third_sep_2, page_start_h, d.width, page.height)).extract_text()

            # Concatenar el texto en orden de columnas
            combined_text = f"{col1}\n{col2}\n{col3}"
            full_text += f"\n{combined_text}"
        pdf.close()
    return full_text


# Application header cases
def fix_app_headers(l: list):
    result = []
    wait_string = ""
    for token in l:
        if token == "":
            continue
        
        if all(char.isupper() for char in token if char.isalpha()):
            wait_string += f"{token} "
            
            if token.endswith(":"):
                result.append(wait_string.replace("- ", ""))
                wait_string = ""
            continue
        
        result.append(token)
        
    # hardcoded fix
    index = result.index("HIPOSTENI ZANTES CARDIOVASCULARES: ")
    result[index] = "HIPOSTENIZANTES CARDIOVASCULARES: "
    
    return result


# Application plant names cases
def fix_plants_names(d: dict[str, list[str]]):
    for app, items in d.items():
        
        result = []
        last = ""
        for item in items:
            
            # Hardcoded fixes
            if item.startswith("Domingo") and last.startswith("Mamey de Santo"):
                result[-1] = "Mamey de Santo Domingo"
                continue
            if item.startswith("Rico") and last.startswith("Tamarindo de Puerto"):
                result[-1] = "Tamarindo de Puerto Rico"
                continue
            
            # continuation lowercase case
            if item[:1].islower():
                value = f"{last} {item}"
                value = value.replace("- ", "")
                result[-1] = value
                last = value
                continue
                
            result.append(item)
            last = item
        
        d[app] = result
            
            
            
        
        




#########################################################################################

raw_text = extract_raw_text()
splitted = raw_text.split('\n')

splitted = fix_app_headers(splitted)

# Group plants in json format (key: app)
apps: dict[str, list[str]] = dict()
current_app = ""
for token in splitted:
    if all(char.isupper() for char in token if char.isalpha()):
        if token.endswith(": "):
            current_app = token[:-2]
            apps[current_app] = []
        else:
            raise Exception(f"Does not ends with (:): '{token}'")
    else:
        apps[current_app].append(token)
        
        
fix_plants_names(apps)
        
    
with open('apps.json', 'w', encoding='utf-8') as f:
    json.dump(apps, f, indent=4)