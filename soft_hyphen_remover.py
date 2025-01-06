def remove_soft_hyphens(monographs: dict):
    for plant, data in monographs.items():
        for field, content in data.items():
            if isinstance(content, str):
                monographs[plant][field] = monographs[plant][field].replace("\u00ad ", "")

            elif isinstance(content, list):
                for i in range(len(content)):
                    monographs[plant][field][i] = monographs[plant][field][i].replace("\u00ad ", "")

            elif isinstance(content, dict):
                keys = []
                for k, v in content.items():
                    keys.append(k)

                    if isinstance(v, str):
                        monographs[plant][field][k] = monographs[plant][field][k].replace("\u00ad ", "")

                    elif isinstance(v, list):
                        for i in range(len(v)):
                            monographs[plant][field][k][i] = monographs[plant][field][k][i].replace("\u00ad ", "")

                # Replace also in country names
                for k in keys:
                    if "\u00ad " in k:
                        new_k = k.replace("\u00ad ", "")
                        value = monographs[plant][field][k]
                        del monographs[plant][field][k]
                        monographs[plant][field][new_k] = value



            else:
                raise Exception("Error: Field was not of type (str, list, or dict)")