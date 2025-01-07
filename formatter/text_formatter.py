import http
import json
import os
import threading
import time
import typing_extensions
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai.types import *

def get_propmt(text: str):
    return f'''Task: Receive the following string and improve its readability for a human by adding appropriate formatting characters where necessary to achieve a clear, well-structured **plain text visualization**.

Rules:  
1. You can add only the following characters to the text:  
   - Newline (`\n`)  
   - Space (` `)  
   - Tab (`\t`)  
   - Punctuation marks such as periods (`.`), commas (`,`), colons (`:`), semicolons (`;`), and dashes (`-`).  
2. You must not modify the original content of the text except by adding these characters. Do not change any existing words or punctuation.  
3. The goal is to provide a **clean and readable plain text format** by:  
   - Splitting text into separate paragraphs using `\n`.  
   - Using tabs (`\t`) to represent indented sections or semi-structured data (e.g., lists, tables, or other logical groupings).  
   - Using dashes (`-`) to create lists or separate individual items clearly when appropriate.  
   - Replacing consecutive periods (`...`) used to separate values with colons (`:`) for clarity.  
   - Adding spaces to separate words or fix unnatural breaks in the text.  
   - Adding punctuation marks to clarify the structure of the text.  
4. Only add newlines at the end of complete sentences to separate ideas clearly. Do not split sentences in unnatural ways.  
5. If the input text is already short or reads naturally as a single paragraph, do not add any formatting characters.  
6. Only add characters when they significantly improve the **visual clarity** of the text when viewed in a plain text editor.  

Input string:
"{text}"
'''



class FormattedText(typing_extensions.TypedDict):
    formatted_text: str

FIELDS_TO_REFORMATT = ["Hab", "Des", "Cmp", "Use", "Pro", "App", "Cul"]
class Formatter:
    def __init__(self):
        load_dotenv()
        key = os.getenv("API_KEY")
        genai.configure(api_key=key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Load configurations
        configuration = dict()
        with open('formatter/config.json', 'r') as file:
            configuration.update(json.load(file))
        self.current_plant = configuration['current_plant']
        
        # Load source data
        self.source_data: dict[str, dict[str, str]] = dict()
        with open('monographs.json', 'r') as file:
            self.source_data.update(json.load(file))
            file.close()
        
        # Load progress
        self.result: dict[str, dict[str, str]] = dict()
        self._load_progress()
        
        self.end_flag = False
        pass
    
    def run(self):
        self._log("engine", "started")
        plants_names = [k for k, _ in self.source_data.items()]
        
        for plant in plants_names:
            # Copy all plant data
            self.result[plant] = self.source_data[plant]
            
            # Replace corrected information
            for field in FIELDS_TO_REFORMATT:
                content = self.source_data[plant][field]
                
                if content == "":
                    self.result[plant][field] = ""
                    self._log("success", f"{plant}, {field}")
                
                else:
                    # Empty field
                    prompt = get_propmt(content)
                    
                    tries = 0
                    tryagain = True
                    while tryagain:
                        try:
                            tries+=1
                            llm_response = self.model.generate_content(
                                prompt,
                                generation_config=genai.GenerationConfig(
                                    response_mime_type="application/json", response_schema=FormattedText
                                ),
                                safety_settings={
                                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                                }
                            ).text
                            formatted_text = json.loads(llm_response)['formatted_text']
                            
                            self.result[plant][field] = formatted_text
                            self._log("success", f"{plant}, {field}")
                            tryagain = False
                            tries = 0
                            
                        except Exception as e:
                            if e.code == http.HTTPStatus.REQUEST_TIMEOUT or e.code == http.HTTPStatus.TOO_MANY_REQUESTS or e.code == http.HTTPStatus.INTERNAL_SERVER_ERROR or e.code == http.HTTPStatus.SERVICE_UNAVAILABLE:
                                if tries == 3:
                                    # enougth trying
                                    tryagain = False
                                    tries = 0
                                    self.result[plant][field] = "fail"
                                    self._log("fail", f"{plant} {field} {e.code}")
                                    self._report_fail(plant, field)
                                else:
                                    time.sleep(15)
                            else:
                                raise e
                        
                        
                            
            
            self._save_progress()
                
            # Go next plant
            end_of_plants = self._go_next_plant(plants_names)
            if end_of_plants:
                print("All plants formatted successfully")
                self.end_flag = True
            
            # Log progress
            count = plants_names.index(self.current_plant)
            self._log("count", f"{count+1} of {len(plants_names)}")
            
            # Check stop flag
            if self.end_flag:
                self._log("engine", "stopped")
                print("Progress saved")
                print("You can clse the app now")
                return
                
                
    def stop(self):
        print("Wait for end message before closing...")
        self.current_plant = ""
    
    def _go_next_plant(self, plants: list[str]) -> bool:
        p_i = plants.index(self.current_plant)
        
        if p_i == len(plants)-1:
            # End case
            return True
        else:
            self.current_plant = plants[p_i+1]
            self._save_config()
            return False
            
    def _report_fail(self, plant: str, field:str):
        fails: dict[str, list[str]] = dict()
        with open('formatter/fails.json', 'r') as file:
            fails.update(json.load(file))
            file.close()
            
        if plant in fails:
            if field not in fails[plant]:
                fails[plant].append(field)
        else:
            fails[plant] = [field]
        
        with open('formatter/fails.json', 'w', encoding='utf-8') as file:
            json.dump(fails, file, indent=4)
            file.close()
    
    def _log(self, type: str, msg: str):
        with open('formatter/logs.txt', 'a', encoding='utf-8') as file:
            text = f"[{type}] {msg}\n"
            file.write(text)
    
    
    def _save_progress(self):
        with open('formatter/data.json', 'w', encoding='utf-8') as file:
            json.dump(self.result, file, indent=4)
            file.close()
    
    def _load_progress(self):
        with open('formatter/data.json', 'r') as file:
            self.result.update(json.load(file))
            file.close()
    
    def _save_config(self):
        new_config = { "current_plant": self.current_plant }
        with open('formatter/config.json', 'w', encoding='utf-8') as file:
            json.dump(new_config, file, indent=4)
            file.close()
        
    

if __name__ == "__main__":
    formatter = Formatter()
    
    while True:
        command = input("> ")
        
        if command == "stop":
            threading.Thread(target=formatter.stop).start()
        
        if command == "start":
            threading.Thread(target=formatter.run).start()
        
    