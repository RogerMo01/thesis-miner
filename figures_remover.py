figures1: list[str] = [
    " Fig. 2. AJENJO. Artemisia absinthium L., ramas con frutos.",
    " Fig. 3. ALBAHACA. Ocimum basi\u00ad licum L., ramas con flores.",
    " Fig. 10. CABALONGA. Thevetia. peruviana (Pers.) K. Schum., ramas con frutos y flores.",
    " Fig. 13. CEREZA DEL PA\u00cdS. Malpighia puncifo\u00ad lia L., ramas con flores y frutas.",
    " Fig. 14. COCA. Erythroxylon coca Lam., rama con flores y frutos.",
    " Fig. 16. CULANTRO Coriandrum sativum L., ramas con flores.",
    " Fig. 17. CURBANA. Canella winterana (L.) Gaertn., rama con frutos.",
    " Fig. 18. CHAMICO. Datura stramonium L., ramas con flores y frutos.",
    " Fig. 19 CHAYOTE. Sechium edule (Jacq.) Sw., ramas y frutos.",
    " Fig. 24 HINOJO. Foeniculum vulgare Mill., campo de hinojo.",
    " Fig. 25 HINOJO. Foeniculum vulgare Miller, ramas con flores."
]
figures2: list[str] = [
    " Fig. 30. LAUREL. Laurus nobilis L., ramas con flores y frutos.",
    " Fig. 31. LOBELIA. Lobelia inflata ., ramas con flores",
    " Fig. 32. Llant\u00e9n. Plantago major L., planta con frutos.",
    " Fig. 37. MARA\u00d1\u00d3N. Anacardium occidentale L., parte de una planta con ramas, flores y frutos.",
    " Fig.47. PLATANILLO DE CUBA. Piper aduncum L., rama de la planta.",
    " Fig. 48. PONAS\u00cd. Hamelia patents Jacq., ramas con flores.",
    " Fig. 51. RUDA. Ruta chalepensis L., parte de la planta.",
    " Fig. 56. VAINILLA. Vanilla phalantha Andr., rama con frutos y flores.",
    " Fig. 61 ZARAGATONA. Plantago psyllium. L., planta completa."
]

class FiguresRemover():
    def __init__(self, selector: int):
        if selector not in [1, 2]:
            raise Exception("SELECTOR must be 1 or 2")
        self.s = selector
        self.current_i = 0

    def remove_figures(self, monographs: dict):
        for plant, data in monographs.items():
            for field, content in data.items():
                if isinstance(content, str):
                    monographs[plant][field] = self._remove_from_str(content)

                elif isinstance(content, list):
                    for i in range(len(content)):
                        monographs[plant][field][i] = self._remove_from_str(content[i])

                elif isinstance(content, dict):
                    for k, v in content.items():
                        if isinstance(v, str):
                            monographs[plant][field][k] = self._remove_from_str(v)

                        elif isinstance(v, list):
                            for i in range(len(v)):
                                monographs[plant][field][k][i] = self._remove_from_str(v[i])

                else:
                    raise Exception("Error: Field was not of type (str, list, or dict)")
                
                if self.current_i == len(figures1 if self.s == 1 else figures2): return



    def _remove_from_str(self, text: str) -> str:
        figures = figures1 if self.s == 1 else figures2
        subs = figures[self.current_i]
        contains = subs in text
        result = text.replace(subs, "") if contains else text
        self.current_i = self.current_i + 1 if contains else self.current_i
        if contains: print(f"Removed: {subs}")
        return result
    
