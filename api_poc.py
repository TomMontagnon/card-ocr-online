import requests
from enum import Enum
import re


class Expansion(Enum):
    SOR_EN = 2
    SOR_DE = 3
    SOR_FR = 4
    SOR_ES = 5
    SOR_IT = 6
    SHD_EN = 8
    SHD_DE = 9
    SHD_FR = 10
    SHD_ES = 11
    SHD_IT = 12
    C24_EN = 13
    C24_DE = 14
    C24_FR = 15
    C24_ES = 16
    C24_IT = 17
    TWI_EN = 18
    TWI_DE = 19
    TWI_FR = 20
    TWI_ES = 21
    TWI_IT = 22
    JTL_EN = 23
    JTL_DE = 24
    JTL_ES = 25
    JTL_IT = 26
    JTL_FR = 27
    J24_EN = 28
    J24_DE = 29
    J24_FR = 30
    J24_ES = 31
    J24_IT = 32
    J25_EN = 33
    J25_DE = 34
    J25_FR = 35
    J25_ES = 36
    J25_IT = 37
    P25_EN = 38
    P25_DE = 39
    P25_FR = 40
    P25_ES = 41
    P25_IT = 42
    GG_EN = 43
    GG_DE = 44
    GG_FR = 45
    GG_ES = 46
    GG_IT = 47
    JTLW_EN = 48
    JTLW_DE = 49
    JTLW_FR = 50
    JTLW_ES = 51
    JTLW_IT = 52
    LOF_EN = 53
    LOF_DE = 54
    LOF_FR = 55
    LOF_ES = 56
    LOF_IT = 57
    LOFW_EN = 58
    LOFW_DE = 59
    LOFW_FR = 60
    LOFW_ES = 61
    LOFW_IT = 62
    C25_EN = 63
    C25_DE = 64
    C25_FR = 65
    C25_ES = 66
    C25_IT = 67
    IBH_EN = 68
    IBH_DE = 69
    IBH_FR = 70
    IBH_ES = 71
    IBH_IT = 72
    SEC_EN = 73
    SEC_DE = 74
    SEC_FR = 75
    SEC_ES = 76
    SEC_IT = 77

def foo(
    exp: Expansion = None, lan: str = "fr", card_number: int = 1
) -> requests.models.Response:
    url = "https://admin.starwarsunlimited.com/api/card-list"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:139.0) Gecko/20100101 Firefox/139.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip",
        "Origin": "https://starwarsunlimited.com",
        "Referer": "https://starwarsunlimited.com/",
    }

    # One param per line
    params = [
        ("locale", lan),
        ("orderBy[expansion][id]", "asc"),
        ("sort[0]", "type.sortValue:asc,expansion.sortValue:desc,cardNumber:asc"),
        ("filters[$and][0][variantOf][id][$null]", "true"),
        ("filters[$and][1][cardNumber][$eq]", card_number),
        ("aspectMethod", "0"),
        ("aspect", "0"),
        ("traitMethod", "0"),
        ("trait", "0"),
    ]
    if exp is not None:
        params.append(("filters[$and][2][expansion][id][$eq]", exp.value))

    resp = requests.get(url, headers=headers, params=params, timeout=30)
    resp.raise_for_status()  # raises if HTTP status is 4xx/5xx
    return resp


def fetch_exp_ids() -> list:
    def iter_objects(o):
        # Génère tous les dicts rencontrés dans l'arbre JSON
        if isinstance(o, dict):
            yield o
            for v in o.values():
                yield from iter_objects(v)
        elif isinstance(o, list):
            for v in o:
                yield from iter_objects(v)

    result = []
    for lan in ["en", "fr", "de", "es", "it"]:
        resp = foo(None, lan, 1)

        result += [
            f"{obj['expansion']['data']['attributes']['code']}_{lan.upper()} = {obj['expansion']['data']['id']}"
            for obj in iter_objects(resp.json())
            if isinstance(obj, dict)
            and "expansion" in obj
            and isinstance(obj["expansion"].get("data"), dict)
            and isinstance(obj["expansion"]["data"].get("attributes"), dict)
            and "code" in obj["expansion"]["data"]["attributes"]
            and "id" in obj["expansion"]["data"]
        ]
    return result


def sort_and_display_exp_ids(lst: list) -> None:
    def key_num(s: str) -> int:
        # extrait le nombre après "=" (tolère espaces)
        m = re.search(r"=\s*(\d+)\s*$", s)
        return int(m.group(1)) if m else float("inf")

    unique_sorted = sorted(set(lst), key=key_num)
    print("\n".join(unique_sorted))


resp = foo(Expansion.SOR_FR)
data = resp.json()
url = data["data"][0]["attributes"]["artFront"]["data"]["attributes"]["formats"]["card"]["url"]
print(url)
# lst = fetch_exp_ids()
# sort_and_display_exp_ids(lst)
