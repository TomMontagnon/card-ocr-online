from card_scanner.core.utils.imaging import np_from_url
import json
from card_scanner.core.utils.network import request_url

from card_scanner.core.api.types import Expansion


class FetchArtWorker:
    def __init__(self) -> None:
        super().__init__()

    def emit_card_from_name(self, dico: dict[str]) -> None:
        lan = dico["exp"].name.split("_")[1].lower()
        exp = dico["exp"].value
        card_number = dico["card_id"]
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
            ("sort[0]", "type.sortValue:asc,expansion.sortValue:desc,cardNumber:asc"),
            ("filters[$and][1][cardNumber][$eq]", card_number),
            ("filters[$and][2][type][value][$notContainsi]", "Token"),
            ("filters[$and][2][expansion][id][$eq]", exp),
        ]
        resp = request_url(url, headers, params)
        data = resp.json()
        # print(data)
        print("nb variant : ", len(data["data"]))
        return data

    def emit_card_from_url(self, url: str) -> None:
        img = np_from_url(url)
        return img


def register(res) -> None:
    for i in res["data"]:
        # name = i["attributes"]["artFront"]["data"]["attributes"]["name"]
        name = "default"

        with open(f"{name}.json", "w") as f:
            json.dump(i, f, indent=2, ensure_ascii=False)


def print_url(res) -> None:
    for i in res["data"]:
        print(
            i["attributes"]["artFront"]["data"]["attributes"]["formats"]["card"]["url"]
        )


def associated_variant(res) -> None:
    arr = []
    for i in res["data"]:
        url = i["attributes"]["artFront"]["data"]["attributes"]["formats"]["card"][
            "url"
        ]
        variant = i["attributes"]["variantTypes"]["data"][0]["attributes"]["name"]
        print(url, variant)
        arr.append((variant, url))

dico = {"exp": Expansion.SOR_EN, "card_id": 364}
res = FetchArtWorker().emit_card_from_name(dico)

# register(res)
print_url(res)
# associated_variant(res)
