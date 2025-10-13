from core.utils.imaging import np_from_url
from core.utils.network import request_url

from core.api.types import Frame, Meta, Expansion


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
            ("filters[$and][2][type][value][$containsi]","Token"),
            ("filters[$and][2][expansion][id][$eq]", exp),
        ]
        # if exp is not None:
        #     params.append()
        resp = request_url(url, headers, params)
        data = resp.json()
        # print(data["id"])
        print(len(data["data"]))
        url = data["data"][0]["attributes"]["artFront"]["data"]["attributes"][
            "formats"
        ]["card"]["url"]
        return url

    def emit_card_from_url(self, url: str) -> None:
        img = np_from_url(url)
        return img


foo = FetchArtWorker()

dico = {"exp" : Expansion.LOF_FR,"card_id":1}

res = foo.emit_card_from_name(dico)

print(res)
