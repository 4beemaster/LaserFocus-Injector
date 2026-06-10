import json

# Type effectiveness chart
# Super effective (2x damage)
SUPER_EFFECTIVE = {
    "Normal": [],
    "Fire": ["Grass", "Ice", "Bug", "Steel"],
    "Water": ["Fire", "Ground", "Rock"],
    "Electric": ["Water", "Flying"],
    "Grass": ["Water", "Ground", "Rock"],
    "Ice": ["Grass", "Ground", "Flying", "Dragon"],
    "Fighting": ["Normal", "Ice", "Rock", "Dark", "Steel"],
    "Poison": ["Grass"],
    "Ground": ["Fire", "Electric", "Poison", "Rock", "Steel"],
    "Flying": ["Grass", "Fighting", "Bug"],
    "Psychic": ["Fighting", "Poison"],
    "Bug": ["Grass", "Psychic", "Dark"],
    "Rock": ["Fire", "Ice", "Flying", "Bug"],
    "Ghost": ["Psychic", "Ghost"],
    "Dragon": ["Dragon"],
    "Dark": ["Psychic", "Ghost"],
    "Steel": ["Ice", "Rock"]
}

# Not very effective (0.5x damage)
NOT_VERY_EFFECTIVE = {
    "Normal": ["Rock", "Steel"],
    "Fire": ["Fire", "Water", "Rock", "Dragon"],
    "Water": ["Water", "Grass", "Dragon"],
    "Electric": ["Electric", "Grass", "Dragon"],
    "Grass": ["Fire", "Grass", "Poison", "Flying", "Bug", "Dragon", "Steel"],
    "Ice": ["Fire", "Water", "Ice", "Steel"],
    "Fighting": ["Poison", "Flying", "Psychic", "Bug"],
    "Poison": ["Poison", "Ground", "Rock", "Ghost"],
    "Ground": ["Grass", "Bug"],
    "Flying": ["Electric", "Rock", "Steel"],
    "Psychic": ["Psychic", "Steel"],
    "Bug": ["Fire", "Fighting", "Poison", "Flying", "Ghost", "Steel"],
    "Rock": ["Fighting", "Ground", "Steel"],
    "Ghost": ["Dark"],
    "Dragon": ["Steel"],
    "Dark": ["Fighting", "Dark"],
    "Steel": ["Fire", "Water", "Electric", "Steel"]
}

# Immunities (0x damage)
IMMUNITIES = {
    "Normal": ["Ghost"],
    "Fire": [],
    "Water": [],
    "Electric": ["Ground"],
    "Grass": [],
    "Ice": [],
    "Fighting": ["Ghost"],
    "Poison": ["Steel"],
    "Ground": ["Flying"],
    "Flying": [],
    "Psychic": ["Dark"],
    "Bug": [],
    "Rock": [],
    "Ghost": ["Normal"],
    "Dragon": [],
    "Dark": [],
    "Steel": []
}

# Pokemon types - National Dex 001-649 (Gen 1-5)
POKEMON_TYPES = {
    "000": [],
    "001": ["Grass", "Poison"], "002": ["Grass", "Poison"], "003": ["Grass", "Poison"],
    "004": ["Fire"], "005": ["Fire"], "006": ["Fire", "Flying"],
    "007": ["Water"], "008": ["Water"], "009": ["Water"],
    "010": ["Bug"], "011": ["Bug"], "012": ["Bug", "Flying"],
    "013": ["Bug", "Poison"], "014": ["Bug", "Poison"], "015": ["Bug", "Poison"],
    "016": ["Normal", "Flying"], "017": ["Normal", "Flying"], "018": ["Normal", "Flying"],
    "019": ["Normal"], "020": ["Normal"],
    "021": ["Normal", "Flying"], "022": ["Normal", "Flying"],
    "023": ["Poison"], "024": ["Poison"],
    "025": ["Electric"], "026": ["Electric"],
    "027": ["Ground"], "028": ["Ground"],
    "029": ["Poison"], "030": ["Poison"], "031": ["Poison", "Ground"],
    "032": ["Poison"], "033": ["Poison"], "034": ["Poison", "Ground"],
    "035": ["Normal"], "036": ["Normal"],
    "037": ["Fire"], "038": ["Fire"],
    "039": ["Normal"], "040": ["Normal"],
    "041": ["Poison", "Flying"], "042": ["Poison", "Flying"],
    "043": ["Grass", "Poison"], "044": ["Grass", "Poison"], "045": ["Grass", "Poison"],
    "046": ["Bug", "Grass"], "047": ["Bug", "Grass"],
    "048": ["Bug", "Poison"], "049": ["Bug", "Poison"],
    "050": ["Ground"], "051": ["Ground"],
    "052": ["Normal"], "053": ["Normal"],
    "054": ["Water"], "055": ["Water"],
    "056": ["Fighting"], "057": ["Fighting"],
    "058": ["Fire"], "059": ["Fire"],
    "060": ["Water"], "061": ["Water"], "062": ["Water", "Fighting"],
    "063": ["Psychic"], "064": ["Psychic"], "065": ["Psychic"],
    "066": ["Fighting"], "067": ["Fighting"], "068": ["Fighting"],
    "069": ["Grass", "Poison"], "070": ["Grass", "Poison"], "071": ["Grass", "Poison"],
    "072": ["Water", "Poison"], "073": ["Water", "Poison"],
    "074": ["Rock", "Ground"], "075": ["Rock", "Ground"], "076": ["Rock", "Ground"],
    "077": ["Fire"], "078": ["Fire"],
    "079": ["Water", "Psychic"], "080": ["Water", "Psychic"],
    "081": ["Electric", "Steel"], "082": ["Electric", "Steel"],
    "083": ["Normal", "Flying"],
    "084": ["Normal", "Flying"], "085": ["Normal", "Flying"],
    "086": ["Water"], "087": ["Water", "Ice"],
    "088": ["Poison"], "089": ["Poison"],
    "090": ["Water"], "091": ["Water", "Ice"],
    "092": ["Ghost", "Poison"], "093": ["Ghost", "Poison"], "094": ["Ghost", "Poison"],
    "095": ["Rock", "Ground"],
    "096": ["Psychic"], "097": ["Psychic"],
    "098": ["Water"], "099": ["Water"],
    "100": ["Electric"], "101": ["Electric"],
    "102": ["Grass", "Psychic"], "103": ["Grass", "Psychic"],
    "104": ["Ground"], "105": ["Ground"],
    "106": ["Fighting"], "107": ["Fighting"],
    "108": ["Normal"],
    "109": ["Poison"], "110": ["Poison"],
    "111": ["Ground", "Rock"], "112": ["Ground", "Rock"],
    "113": ["Normal"],
    "114": ["Grass"],
    "115": ["Normal"],
    "116": ["Water"], "117": ["Water"],
    "118": ["Water"], "119": ["Water"],
    "120": ["Water"], "121": ["Water", "Psychic"],
    "122": ["Psychic"],
    "123": ["Bug", "Flying"],
    "124": ["Ice", "Psychic"],
    "125": ["Electric"],
    "126": ["Fire"],
    "127": ["Bug"],
    "128": ["Normal"],
    "129": ["Water"], "130": ["Water", "Flying"],
    "131": ["Water", "Ice"],
    "132": ["Normal"],
    "133": ["Normal"],
    "134": ["Water"], "135": ["Electric"], "136": ["Fire"],
    "137": ["Normal"],
    "138": ["Rock", "Water"], "139": ["Rock", "Water"],
    "140": ["Rock", "Water"], "141": ["Rock", "Water"],
    "142": ["Rock", "Flying"],
    "143": ["Normal"],
    "144": ["Ice", "Flying"], "145": ["Electric", "Flying"], "146": ["Fire", "Flying"],
    "147": ["Dragon"], "148": ["Dragon"], "149": ["Dragon", "Flying"],
    "150": ["Psychic"], "151": ["Psychic"],
    "152": ["Grass"], "153": ["Grass"], "154": ["Grass"],
    "155": ["Fire"], "156": ["Fire"], "157": ["Fire"],
    "158": ["Water"], "159": ["Water"], "160": ["Water"],
    "161": ["Normal"], "162": ["Normal"],
    "163": ["Normal", "Flying"], "164": ["Normal", "Flying"],
    "165": ["Bug", "Flying"], "166": ["Bug", "Flying"],
    "167": ["Bug", "Poison"], "168": ["Bug", "Poison"],
    "169": ["Poison", "Flying"],
    "170": ["Water", "Electric"], "171": ["Water", "Electric"],
    "172": ["Electric"],
    "173": ["Normal"], "174": ["Normal"], "175": ["Normal"], "176": ["Normal", "Flying"],
    "177": ["Psychic", "Flying"], "178": ["Psychic", "Flying"],
    "179": ["Electric"], "180": ["Electric"], "181": ["Electric"],
    "182": ["Grass"],
    "183": ["Water"], "184": ["Water"],
    "185": ["Rock"],
    "186": ["Water"],
    "187": ["Grass", "Flying"], "188": ["Grass", "Flying"], "189": ["Grass", "Flying"],
    "190": ["Normal"],
    "191": ["Grass"], "192": ["Grass"],
    "193": ["Bug", "Flying"],
    "194": ["Water", "Ground"], "195": ["Water", "Ground"],
    "196": ["Psychic"], "197": ["Dark"],
    "198": ["Dark", "Flying"],
    "199": ["Water", "Psychic"],
    "200": ["Ghost"],
    "201": ["Psychic"],
    "202": ["Psychic"],
    "203": ["Normal", "Psychic"],
    "204": ["Bug"], "205": ["Bug", "Steel"],
    "206": ["Normal"],
    "207": ["Ground", "Flying"],
    "208": ["Steel", "Ground"],
    "209": ["Normal"], "210": ["Normal"],
    "211": ["Water", "Poison"],
    "212": ["Bug", "Steel"],
    "213": ["Bug", "Rock"],
    "214": ["Bug", "Fighting"],
    "215": ["Dark", "Ice"],
    "216": ["Normal"], "217": ["Normal"],
    "218": ["Fire"], "219": ["Fire", "Rock"],
    "220": ["Ice", "Ground"], "221": ["Ice", "Ground"],
    "222": ["Water", "Rock"],
    "223": ["Water"], "224": ["Water"],
    "225": ["Ice", "Flying"],
    "226": ["Water", "Flying"],
    "227": ["Steel", "Flying"],
    "228": ["Dark", "Fire"], "229": ["Dark", "Fire"],
    "230": ["Water", "Dragon"],
    "231": ["Ground"], "232": ["Ground"],
    "233": ["Normal"], "234": ["Normal"], "235": ["Normal"],
    "236": ["Fighting"], "237": ["Fighting"],
    "238": ["Ice", "Psychic"],
    "239": ["Electric"], "240": ["Fire"], "241": ["Normal"], "242": ["Normal"],
    "243": ["Electric"], "244": ["Fire"], "245": ["Water"],
    "246": ["Rock", "Ground"], "247": ["Rock", "Ground"], "248": ["Rock", "Dark"],
    "249": ["Psychic", "Flying"], "250": ["Fire", "Flying"], "251": ["Psychic", "Grass"],
    
    # Generation 3 (252-386)
    "252": ["Grass"], "253": ["Grass"], "254": ["Grass"],
    "255": ["Fire"], "256": ["Fire", "Fighting"], "257": ["Fire", "Fighting"],
    "258": ["Water"], "259": ["Water", "Ground"], "260": ["Water", "Ground"],
    "261": ["Dark"], "262": ["Dark"],
    "263": ["Normal"], "264": ["Normal"],
    "265": ["Bug"], "266": ["Bug"], "267": ["Bug", "Flying"], "268": ["Bug"], "269": ["Bug", "Poison"],
    "270": ["Water", "Grass"], "271": ["Water", "Grass"], "272": ["Water", "Grass"],
    "273": ["Grass"], "274": ["Grass", "Dark"], "275": ["Grass", "Dark"],
    "276": ["Normal", "Flying"], "277": ["Normal", "Flying"],
    "278": ["Water", "Flying"], "279": ["Water", "Flying"],
    "280": ["Psychic"], "281": ["Psychic"], "282": ["Psychic"],
    "283": ["Bug", "Water"], "284": ["Bug", "Flying"],
    "285": ["Grass"], "286": ["Grass", "Fighting"],
    "287": ["Normal"], "288": ["Normal"], "289": ["Normal"],
    "290": ["Bug", "Ground"], "291": ["Bug", "Flying"],
    "292": ["Bug", "Ghost"],
    "293": ["Normal"], "294": ["Normal"], "295": ["Normal"],
    "296": ["Fighting"], "297": ["Fighting"],
    "298": ["Normal"],
    "299": ["Rock"],
    "300": ["Normal"], "301": ["Normal"],
    "302": ["Dark", "Ghost"],
    "303": ["Steel"],
    "304": ["Steel", "Rock"], "305": ["Steel", "Rock"], "306": ["Steel", "Rock"],
    "307": ["Fighting", "Psychic"], "308": ["Fighting", "Psychic"],
    "309": ["Electric"], "310": ["Electric"],
    "311": ["Electric"], "312": ["Electric"],
    "313": ["Bug"], "314": ["Bug"],
    "315": ["Grass", "Poison"],
    "316": ["Poison"], "317": ["Poison"],
    "318": ["Water", "Dark"], "319": ["Water", "Dark"],
    "320": ["Water"], "321": ["Water"],
    "322": ["Fire", "Ground"], "323": ["Fire", "Ground"],
    "324": ["Fire"],
    "325": ["Psychic"], "326": ["Psychic"],
    "327": ["Normal"],
    "328": ["Ground"], "329": ["Ground", "Dragon"], "330": ["Ground", "Dragon"],
    "331": ["Grass"], "332": ["Grass", "Dark"],
    "333": ["Normal", "Flying"], "334": ["Dragon", "Flying"],
    "335": ["Normal"],
    "336": ["Poison"],
    "337": ["Rock", "Psychic"],
    "338": ["Rock", "Ground"],
    "339": ["Water", "Ground"], "340": ["Water", "Ground"],
    "341": ["Water"], "342": ["Water", "Dark"],
    "343": ["Ground", "Psychic"], "344": ["Ground", "Psychic"],
    "345": ["Rock", "Grass"], "346": ["Rock", "Grass"],
    "347": ["Rock", "Bug"], "348": ["Rock", "Bug"],
    "349": ["Water"], "350": ["Water"],
    "351": ["Normal"],
    "352": ["Normal"],
    "353": ["Ghost"], "354": ["Ghost"],
    "355": ["Ghost"], "356": ["Ghost"],
    "357": ["Grass", "Flying"],
    "358": ["Psychic"],
    "359": ["Dark"],
    "360": ["Psychic"],
    "361": ["Ice"], "362": ["Ice"], "363": ["Ice", "Water"], "364": ["Ice", "Water"], "365": ["Ice", "Water"],
    "366": ["Water"], "367": ["Water"], "368": ["Water"],
    "369": ["Water", "Rock"],
    "370": ["Water"],
    "371": ["Dragon"], "372": ["Dragon"], "373": ["Dragon", "Flying"],
    "374": ["Steel", "Psychic"], "375": ["Steel", "Psychic"], "376": ["Steel", "Psychic"],
    "377": ["Rock"], "378": ["Ice"], "379": ["Steel"],
    "380": ["Dragon", "Psychic"], "381": ["Dragon", "Psychic"],
    "382": ["Water"], "383": ["Ground"], "384": ["Dragon", "Flying"],
    "385": ["Steel", "Psychic"], "386": ["Psychic"],
    
    # Generation 4 (387-493)
    "387": ["Grass"], "388": ["Grass"], "389": ["Grass", "Ground"],
    "390": ["Fire"], "391": ["Fire", "Fighting"], "392": ["Fire", "Fighting"],
    "393": ["Water"], "394": ["Water"], "395": ["Water", "Steel"],
    "396": ["Normal", "Flying"], "397": ["Normal", "Flying"],
    "398": ["Normal", "Flying"],
    "399": ["Normal"], "400": ["Normal", "Water"],
    "401": ["Bug"], "402": ["Bug"],
    "403": ["Electric"], "404": ["Electric"], "405": ["Electric"],
    "406": ["Grass", "Poison"], "407": ["Grass", "Poison"],
    "408": ["Rock"], "409": ["Rock"],
    "410": ["Rock", "Steel"], "411": ["Rock", "Steel"],
    "412": ["Bug"], "413": ["Bug", "Grass"], "414": ["Bug", "Flying"],
    "415": ["Bug", "Flying"], "416": ["Bug", "Flying"],
    "417": ["Electric"],
    "418": ["Water"], "419": ["Water"],
    "420": ["Grass"], "421": ["Grass"],
    "422": ["Water"], "423": ["Water", "Ground"],
    "424": ["Normal"],
    "425": ["Ghost", "Flying"], "426": ["Ghost", "Flying"],
    "427": ["Normal"], "428": ["Normal"],
    "429": ["Ghost"],
    "430": ["Dark", "Flying"],
    "431": ["Normal"],
    "432": ["Normal"],
    "433": ["Psychic"],
    "434": ["Poison", "Dark"], "435": ["Poison", "Dark"],
    "436": ["Steel", "Psychic"], "437": ["Steel", "Psychic"],
    "438": ["Rock"],
    "439": ["Psychic"],
    "440": ["Normal"],
    "441": ["Normal", "Flying"],
    "442": ["Ghost", "Dark"],
    "443": ["Dragon", "Ground"], "444": ["Dragon", "Ground"], "445": ["Dragon", "Ground"],
    "446": ["Normal"],
    "447": ["Fighting"], "448": ["Fighting", "Steel"],
    "449": ["Ground"], "450": ["Ground"],
    "451": ["Poison", "Bug"], "452": ["Poison", "Dark"],
    "453": ["Poison", "Fighting"], "454": ["Poison", "Fighting"],
    "455": ["Grass"],
    "456": ["Water"], "457": ["Water"],
    "458": ["Water", "Flying"],
    "459": ["Grass", "Ice"], "460": ["Grass", "Ice"],
    "461": ["Dark", "Ice"],
    "462": ["Electric", "Steel"],
    "463": ["Normal"],
    "464": ["Ground", "Rock"],
    "465": ["Grass"],
    "466": ["Electric"],
    "467": ["Fire"],
    "468": ["Normal", "Flying"],
    "469": ["Bug", "Flying"],
    "470": ["Grass"],
    "471": ["Ice"],
    "472": ["Ground", "Flying"],
    "473": ["Ice", "Ground"],
    "474": ["Normal"],
    "475": ["Psychic", "Fighting"],
    "476": ["Rock", "Steel"],
    "477": ["Ghost"],
    "478": ["Ice", "Ghost"],
    "479": ["Electric", "Ghost"],
    "480": ["Psychic"], "481": ["Psychic"], "482": ["Psychic"],
    "483": ["Steel", "Dragon"], "484": ["Water", "Dragon"], "485": ["Fire", "Steel"],
    "486": ["Normal"], "487": ["Ghost", "Dragon"], "488": ["Psychic"],
    "489": ["Water"], "490": ["Water"],
    "491": ["Dark"],
    "492": ["Grass"],
    "493": ["Normal"],
    
    # Generation 5 (494-649)
    "494": ["Psychic", "Fire"],
    "495": ["Grass"], "496": ["Grass"], "497": ["Grass"],
    "498": ["Fire"], "499": ["Fire", "Fighting"], "500": ["Fire", "Fighting"],
    "501": ["Water"], "502": ["Water"], "503": ["Water"],
    "504": ["Normal"], "505": ["Normal"],
    "506": ["Normal"], "507": ["Normal"], "508": ["Normal"],
    "509": ["Dark"], "510": ["Dark"],
    "511": ["Grass"], "512": ["Grass"],
    "513": ["Fire"], "514": ["Fire"],
    "515": ["Water"], "516": ["Water"],
    "517": ["Psychic"], "518": ["Psychic"],
    "519": ["Normal", "Flying"], "520": ["Normal", "Flying"], "521": ["Normal", "Flying"],
    "522": ["Electric"], "523": ["Electric"],
    "524": ["Rock"], "525": ["Rock"], "526": ["Rock"],
    "527": ["Psychic", "Flying"], "528": ["Psychic", "Flying"],
    "529": ["Ground"], "530": ["Ground", "Steel"],
    "531": ["Normal"],
    "532": ["Fighting"], "533": ["Fighting"], "534": ["Fighting"],
    "535": ["Water"], "536": ["Water", "Ground"], "537": ["Water", "Ground"],
    "538": ["Fighting"], "539": ["Fighting"],
    "540": ["Bug", "Grass"], "541": ["Bug", "Grass"], "542": ["Bug", "Grass"],
    "543": ["Bug", "Poison"], "544": ["Bug", "Poison"], "545": ["Bug", "Poison"],
    "546": ["Grass"], "547": ["Grass"],
    "548": ["Grass"], "549": ["Grass"],
    "550": ["Water"],
    "551": ["Ground", "Dark"], "552": ["Ground", "Dark"], "553": ["Ground", "Dark"],
    "554": ["Fire"], "555": ["Fire"],
    "556": ["Grass"],
    "557": ["Bug", "Rock"], "558": ["Bug", "Rock"],
    "559": ["Dark", "Fighting"], "560": ["Dark", "Fighting"],
    "561": ["Psychic", "Flying"],
    "562": ["Ghost"], "563": ["Ghost"],
    "564": ["Water", "Rock"], "565": ["Water", "Rock"],
    "566": ["Rock", "Flying"], "567": ["Rock", "Flying"],
    "568": ["Poison"], "569": ["Poison"],
    "570": ["Dark"], "571": ["Dark"],
    "572": ["Normal"], "573": ["Normal"],
    "574": ["Psychic"], "575": ["Psychic"], "576": ["Psychic"],
    "577": ["Psychic"], "578": ["Psychic"], "579": ["Psychic"],
    "580": ["Water", "Flying"], "581": ["Water", "Flying"],
    "582": ["Ice"], "583": ["Ice"], "584": ["Ice"],
    "585": ["Normal", "Grass"], "586": ["Normal", "Grass"],
    "587": ["Electric", "Flying"],
    "588": ["Bug"], "589": ["Bug", "Steel"],
    "590": ["Grass", "Poison"], "591": ["Grass", "Poison"],
    "592": ["Water", "Ghost"], "593": ["Water", "Ghost"],
    "594": ["Water"],
    "595": ["Bug", "Electric"], "596": ["Bug", "Electric"],
    "597": ["Grass", "Steel"], "598": ["Grass", "Steel"],
    "599": ["Steel"], "600": ["Steel"], "601": ["Steel"],
    "602": ["Electric"], "603": ["Electric"], "604": ["Electric"],
    "605": ["Psychic"], "606": ["Psychic"],
    "607": ["Ghost", "Fire"], "608": ["Ghost", "Fire"], "609": ["Ghost", "Fire"],
    "610": ["Dragon"], "611": ["Dragon"], "612": ["Dragon"],
    "613": ["Ice"], "614": ["Ice"],
    "615": ["Ice"],
    "616": ["Bug"], "617": ["Bug"],
    "618": ["Ground", "Electric"],
    "619": ["Fighting"], "620": ["Fighting"],
    "621": ["Dragon"],
    "622": ["Ground", "Ghost"], "623": ["Ground", "Ghost"],
    "624": ["Dark", "Steel"], "625": ["Dark", "Steel"],
    "626": ["Normal"],
    "627": ["Normal", "Flying"], "628": ["Normal", "Flying"],
    "629": ["Dark", "Flying"], "630": ["Dark", "Flying"],
    "631": ["Fire"],
    "632": ["Bug", "Steel"],
    "633": ["Dark", "Dragon"], "634": ["Dark", "Dragon"], "635": ["Dark", "Dragon"],
    "636": ["Bug", "Fire"], "637": ["Bug", "Fire"],
    "638": ["Steel", "Fighting"], "639": ["Rock", "Fighting"], "640": ["Grass", "Fighting"],
    "641": ["Flying"], "642": ["Electric", "Flying"],
    "643": ["Dragon", "Fire"], "644": ["Dragon", "Electric"],
    "645": ["Ground", "Flying"],
    "646": ["Dragon", "Ice"],
    "647": ["Water", "Fighting"],
    "648": ["Normal", "Psychic"],
    "649": ["Bug", "Steel"],
    
    # Alternate forms and special entries
    "652": ["Psychic"], "653": ["Psychic"], "654": ["Psychic"], "655": ["Psychic"],
    "656": ["Psychic"], "657": ["Psychic"], "658": ["Psychic"], "659": ["Psychic"],
    "660": ["Psychic"], "661": ["Psychic"], "662": ["Psychic"], "663": ["Psychic"],
    "664": ["Psychic"], "665": ["Psychic"], "666": ["Psychic"], "667": ["Psychic"],
    "668": ["Psychic"], "669": ["Psychic"], "670": ["Psychic"], "671": ["Psychic"],
    "672": ["Psychic"], "673": ["Psychic"], "674": ["Psychic"], "675": ["Psychic"],
    "676": ["Psychic"], "677": ["Psychic"], "678": ["Psychic"],  # Unown forms (original: 201)
    "679": ["Fire"],  # Castform Sunny Form (original: 351)
    "680": ["Water"],  # Castform Rainy Form (original: 351)
    "681": ["Ice"],  # Castform Snowy Form (original: 351)
    "682": ["Psychic"], "683": ["Psychic"], "684": ["Psychic"],  # Deoxys forms - Attack, Defense, Speed (original: 386)
    "685": ["Bug"], "686": ["Bug"],  # Burmy forms (original: 412)
    "687": ["Bug", "Ground"], "688": ["Bug", "Steel"],  # Wormadam forms (original: 413)
    "689": ["Grass"],  # Cherrim Sunshine Form (original: 421)
    "690": ["Water"],  # Shellos East Sea (original: 422)
    "691": ["Water", "Ground"],  # Gastrodon East Sea (original: 423)
    "692": ["Electric", "Fire"],  # Heat Rotom (original: 479)
    "693": ["Electric", "Water"],  # Wash Rotom (original: 479)
    "694": ["Electric", "Ice"],  # Frost Rotom (original: 479)
    "695": ["Electric", "Flying"],  # Fan Rotom (original: 479)
    "696": ["Electric", "Grass"],  # Mow Rotom (original: 479)
    "697": ["Ghost", "Dragon"],  # Giratina Origin Form (original: 487)
    "698": ["Grass", "Flying"],  # Shaymin Sky Form (original: 492)
    "699": ["Water"],  # Basculin Blue Striped (original: 550)
    "700": ["Fire", "Psychic"],  # Darmanitan Zen Mode (original: 555)
    "701": ["Normal", "Grass"], "702": ["Normal", "Grass"], "703": ["Normal", "Grass"],  # Deerling seasons (original: 585)
    "704": ["Normal", "Grass"], "705": ["Normal", "Grass"], "706": ["Normal", "Grass"],  # Sawsbuck seasons (original: 586)
    "707": ["Normal", "Fighting"],  # Meloetta Pirouette Form (original: 648)
    "708": ["Bug", "Steel"], "709": ["Bug", "Steel"], "710": ["Bug", "Steel"], "711": ["Bug", "Steel"]  # Genesect drives (original: 649)
}


def calculate_weakness_multiplier(pokemon_types, attacking_type):
    """Calculate the multiplier for a given attacking type against pokemon types.
    
    Accounts for:
    - Immunities (0x): Complete negation
    - Resistances (0.5x): Reduces effectiveness
    - Super effective (2x): Increases effectiveness
    - Multiple types stack multiplicatively
    """
    multiplier = 1.0
    
    for ptype in pokemon_types:
        # Check for immunity first (0x damage)
        if ptype in IMMUNITIES.get(attacking_type, []):
            return 0.0  # Immunity overrides everything
        
        # Check for resistance (0.5x damage)
        if ptype in NOT_VERY_EFFECTIVE.get(attacking_type, []):
            multiplier *= 0.5
        
        # Check for super effective (2x damage)
        if ptype in SUPER_EFFECTIVE.get(attacking_type, []):
            multiplier *= 2.0
    
    return multiplier

def get_weaknesses(pokemon_types):
    """Get all weaknesses with their multipliers for a Pokemon.
    
    Only returns types that deal more than 1x damage (actual weaknesses).
    """
    weaknesses = {}
    for attacking_type in SUPER_EFFECTIVE.keys():
        mult = calculate_weakness_multiplier(pokemon_types, attacking_type)
        if mult > 1.0:
            weaknesses[attacking_type] = int(mult)
    
    # Convert to list of dicts
    result = []
    for wtype, mult in sorted(weaknesses.items()):
        result.append({"type": wtype, "multiplier": mult})
    return result

# Generate the full weaknesses dict
weaknesses_data = {
    "comment": "Pokemon weakness lookup table - maps National Dex number to weakness objects with type and multiplier (2x or 4x)"
}

for dex_num, types in POKEMON_TYPES.items():
    weaknesses_data[dex_num] = get_weaknesses(types)

# Write to file
with open("pokemon_weaknesses.json", "w", encoding="utf-8") as f:
    json.dump(weaknesses_data, f, indent=2, ensure_ascii=False)

print("Generated pokemon_weaknesses.json with 4x weakness support!")
print(f"Total Pokemon: {len(POKEMON_TYPES)}")
