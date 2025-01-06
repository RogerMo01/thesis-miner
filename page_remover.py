class PageRemover:
    def __init__(self):
        self.letters = ['A', 'B', 'C', 'CH', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
        self.current_i = 0
        self.last_number = 81

    def remove(self, text: str):
        tokens = text.split(" ")

        result = []

        page = ""
        flag = False

        for token in tokens:
            if token == "": continue

            if flag:
                # if token.isnumeric() and int(token) > self.last_number:
                if token.isalpha() and len(token) < 3 and token.isupper():
                    if token == self.letters[self.current_i]:
                        print(f"Found: {page} {token}")
                        self.last_number += 1
                        flag = False
                        page = ""
                        continue
                    elif self.current_i < len(self.letters) - 1 and token == self.letters[self.current_i + 1]:
                        print(f"Found: {page} {token}")
                        self.last_number += 1
                        self.current_i += 1
                        flag = False
                        page = ""
                        continue

                result.append(page)
                result.append(token)
                flag = False
                page = ""
            else:
                # if token.isalpha() and len(token) < 3 and token.isupper():
                if token.isnumeric() and int(token) > self.last_number:
                    flag = True
                    page = token
                else:
                    result.append(token)
                    flag = False
                    page = ""
            
        return ' '.join(result)



# Remove pages numbers
def remove_pages(monographs: dict):
    pr = PageRemover()
    for plant, data in monographs.items():
        for field, content in data.items():
            if isinstance(content, str):
                result = pr.remove(content)
                monographs[plant][field] = result

            elif isinstance(content, list):
                for i in range(len(content)):
                    result = pr.remove(content[i])
                    monographs[plant][field][i] = result

            elif isinstance(content, dict):
                for k, v in content.items():
                    if isinstance(v, str):
                        result = pr.remove(v)
                        monographs[plant][field][k] = result

                    elif isinstance(v, list):
                        for i in range(len(v)):
                            result = pr.remove(v[i])
                            monographs[plant][field][k][i] = result

            else:
                raise Exception("Error: Field was not of type (str, list, or dict)")
