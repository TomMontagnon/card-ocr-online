from __future__ import annotations
from card_scanner.core.utils import np_from_url, request_url
from PySide6 import QtCore
from importlib import resources
from pathlib import Path
import cv2

class FetchArtsWorker(QtCore.QObject):
    arts_ready = QtCore.Signal(dict, list)

    def __init__(self) -> None:
        super().__init__()
        with resources.path(
            "card_scanner.apps.gui_qt.assets.images", "no_card_available.png"
        ) as p:
            self._default_card_image = cv2.imread(str(p))
        self.is_online = True

    def get_arts(self, dico: dict[str]) -> None:
        lan = dico["exp"].name.split("_")[1].lower()
        exp = dico["exp"].value
        exp_name = dico["exp"].name
        card_number = dico["card_id"]
        data = self.get_variants_online(lan, exp, card_number)
        arr = []
        for variant_name, url in data:
            file = Path(f"cards/{exp_name}/{card_number}/{variant_name}.png")
            if file.is_file():
                # print("OFFLINE :", card_number, variant_name)
                img = cv2.imread(file)
            elif self.is_online:
                print("ONLINE :", url)
                img = np_from_url(url)
            else:
                img = self._default_card_image
            arr.append((variant_name, img))
        self.arts_ready.emit(dico, arr)

    def get_variants_online(self, lan, exp, card_number) -> list:
        url = "https://admin.starwarsunlimited.com/api/card-list"
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:139.0) Gecko/20100101 Firefox/139.0",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip",
            "Origin": "https://starwarsunlimited.com",
            "Referer": "https://starwarsunlimited.com/",
        }

        params = [
            ("locale", lan),
            ("sort[0]", "type.sortValue:asc,expansion.sortValue:desc,cardNumber:asc"),
            ("filters[$and][1][expansion][id][$eq]", exp),
            ("filters[$and][1][cardNumber][$eq]", card_number),
            ("filters[$and][1][type][value][$notContainsi]", "Token"),
        ]
        resp = request_url(url, headers, params)
        data = resp.json()

        arr = []
        for d in data["data"]:
            url = d["attributes"]["artFront"]["data"]["attributes"]["formats"]["card"][
                "url"
            ]
            variant = d["attributes"]["variantTypes"]["data"][0]["attributes"]["name"]
            arr.append((variant, url))
        return arr
