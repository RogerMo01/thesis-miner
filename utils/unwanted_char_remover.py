black_list = [
    "\u00ad ",   # soft hyphen
    "\t",        # tabulations
    "\ufffd"     # replacement character 
]

def remove_unwanted_chars(monographs: dict):
    for plant, data in monographs.items():
        for field, content in data.items():
            if isinstance(content, str):
                for s in black_list:
                    monographs[plant][field] = monographs[plant][field].replace(s, "")

            elif isinstance(content, list):
                for i in range(len(content)):
                    for s in black_list:
                        monographs[plant][field][i] = monographs[plant][field][i].replace(s, "")

            elif isinstance(content, dict):
                keys = []
                for k, v in content.items():
                    keys.append(k)

                    if isinstance(v, str):
                        for s in black_list:
                            monographs[plant][field][k] = monographs[plant][field][k].replace(s, "")

                    elif isinstance(v, list):
                        for i in range(len(v)):
                            for s in black_list:
                                monographs[plant][field][k][i] = monographs[plant][field][k][i].replace(s, "")

                # Replace also in country names
                for k in keys:
                    for s in black_list:
                        if s in k:
                            new_k = k.replace(s, "")
                            value = monographs[plant][field][k]
                            del monographs[plant][field][k]
                            monographs[plant][field][new_k] = value



            else:
                raise Exception("Error: Field was not of type (str, list, or dict)")