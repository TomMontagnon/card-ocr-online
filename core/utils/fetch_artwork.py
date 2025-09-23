from __future__ import annotations
from core.api.types import Meta
from PySide6 import QtCore
from core.utils.imaging import np_from_url
from core.utils.network import request_url
import numpy as np

class _Emitter(QtCore.QObject):
    frame_ready = QtCore.Signal(np.ndarray, Meta)

class FetchArtwork:
    _processed = QtCore.Signal()
    def __init__(self) -> None:
        self._em = _Emitter()

    def connect(self, slot) -> None:
        # Connection queued => thread-safe si push() vient d'un thread worker
        self._em.frame_ready.connect(slot, QtCore.Qt.ConnectionType.QueuedConnection)

    def process(self, dico : dict[str]) -> None:
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
            ("filters[$and][0][variantOf][id][$null]", "true"),
            ("filters[$and][1][cardNumber][$eq]", card_number),
            ("aspectMethod", "0"),
            ("aspect", "0"),
            ("traitMethod", "0"),
            ("trait", "0"),
        ]
        if exp is not None:
            params.append(("filters[$and][2][expansion][id][$eq]", exp))
        resp = request_url(url, headers, params)
        data = resp.json()
        url = data["data"][0]["attributes"]["artFront"]["data"]["attributes"]["formats"]["card"]["url"]
        self.process2(url)

    def process2(self, url : str) -> None:
        img = np_from_url(url)
        self._em.frame_ready.emit(img, Meta(0))
