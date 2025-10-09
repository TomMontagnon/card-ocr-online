from __future__ import annotations
from core.utils.imaging import np_from_url
from core.utils.network import request_url

from PySide6 import QtCore

from core.api.types import Frame, Meta


class FetchArtWorker(QtCore.QObject):
    frame_ready = QtCore.Signal(Frame, Meta)

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
            ("orderBy[expansion][id]", "asc"),
            ("sort[0]", "type.sortValue:asc,expansion.sortValue:desc,cardNumber:asc"),
            # ("filters[$and][0][variantOf][id][$null]", "true"),
            ("filters[$and][1][cardNumber][$eq]", card_number),
            # ("aspectMethod", "0"),
            # ("aspect", "0"),
            # ("traitMethod", "0"),
            # ("trait", "0"),
        ]
        if exp is not None:
            params.append(("filters[$and][2][expansion][id][$eq]", exp))
        resp = request_url(url, headers, params)
        data = resp.json()
        url = data["data"][0]["attributes"]["artFront"]["data"]["attributes"][
            "formats"
        ]["card"]["url"]
        self.emit_card_from_url(url)

    def emit_card_from_url(self, url: str) -> None:
        img = np_from_url(url)
        self.frame_ready.emit(img, Meta())
