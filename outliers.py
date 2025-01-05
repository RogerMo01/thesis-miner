
values1: dict[str, dict] = {
    "Alm\u00e1cigo": {
        "Sy": [
            "Bursera gummifera L.",
            "Elaphrium simaruba (L.) Rose",
            "Pistacia simaruba L.",
            "Terebinthus simaruba W. F. Wright."
        ],
        "Vul": {
            "Cuba": ["Azucarero", "aceitero", "alm\u00e1cigo colorado"],
            "Florida y Antillas Inglesas": ["gum tree", "turpentine", "West Indian birch"],
            "M\u00e9xico": ["chaca piocha", "palo mulato", "palo colorado", "quiote", "zongolica"],
            "Puerto Rico": ["archip\u00edn", "alm\u00e1cigo encarnado"],
            "Nicaragua": ["ji\u00f1ocuabe"],
            "Costa Rica": ["ji\u00f1ocuave", "carana"],
            "Guatemala": ["chinacahuite", "jicote chino", "palo chino"],
            "Honduras": ["cop\u00f3n", "palo chino"],
            "Guayana": ["indio desnudo", "pellejo de indio"],
            "Colombia": ["caratero"]
        }
    },
    "Calaminta*": {
        "Des": "Es una planta vivaz que emite v\u00e1stagos de 30 a 90 cm de altura, con las hojas acopladas, aovados o redondeadas, obtusas, abruptamente contra\u00eddas en la base, con dientes superficiales en los bordes. De la axila superior nacen los ramilletes florales. Corola a lo sumo de 15 mm mas largo que el c\u00e1liz; florece en verano.",
        "Cmp": "Contiene mucha esencia con el 57 % de pulegoma y mentosa y pireno. En las hojas se encuentra oxidasa."
    }
}
values2: dict[str, dict] = {
    "Tebenque (1)": {
        "Use": "Toda la planta.",
        "App": "Esta planta es muy popular en Trinidad, Cienfuegos y Camag\u00fcey para remedio contra las infecciones intestinales. El doctor Jos\u00e9 Morte y Ech\u00e1niz, de Trinidad, ten\u00eda patentado un medicamento a base de tebenque. Tambi\u00e9n se considera muy bueno para las enfermedades del pecho, bronquitis, tos y asma. \u00abPlanta casi rastrera, arom\u00e1tica, de las playas arenosas, abundante por el Castillo de Jagua y otros parajes; florecitas amarillas y las hojas saben a an\u00eds. Es muy eficaz contra las enfermedades del pecho\u00bb (Pichardo). Existen en Cuba otras 14 especies de Pectis, todas arom\u00e1ticas. Una de ellas P. floribunda A. Rich. (P. elongata H.B.K., P. Plumieri Griseb.) es muy com\u00fan en las colinas calc\u00e1reas de las cercan\u00edas de La Habana y lo llaman romero cimarr\u00f3n, comino cimarr\u00f3n, y yerba chinchera y tambi\u00e9n la usan como medicinal. Esta planta cuando joven tiene un olor penetrante a lim\u00f3n, pero en la floraci\u00f3n este olor se transforma en olor a comino y a veces m\u00e1s bien huele a chinches. En Venezuela, seg\u00fan Pittier, llaman comino cimarr\u00f3n a las especies P. ciliaris L. y P. prostrata Cav., que son muy comunes en Cuba. Seg\u00fan dicho autor son medicinales y se emplean tanto en las enfermedades del tubo digestivo como en las enfermedades de las mujeres. El tebenque que se usa en Trinidad, Camag\u00fcey y Cienfuegos difiere del tebenque de Oriente, que es pectoral, y es una especie diferente (V. tebenque, convolvul\u00e1cea)."
    }
}

def solve_2_outliers(input: dict[str, dict]):
    for plant, data in values2.items():
        for field, content in data.items():
            input[plant][field] = content

def solve_1_outliers(input: dict[str, dict]):
    for plant, data in values1.items():
        for field, content in data.items():
            input[plant][field] = content