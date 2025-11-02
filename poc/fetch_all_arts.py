import asyncio
from card_scanner.core.utils.imaging import np_from_url_async
from card_scanner.core.utils.network import request_url_async
from enum import Enum
from pathlib import Path
import cv2


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


MAX = 200  # nombre d'erreurs consécutives autorisées


async def get_card(
    exp, lan: str, card_number: int, filter_out_variant: bool
) -> dict | None:
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
        ("orderBy[expansion][id]", "asc"),
        ("sort[0]", "type.sortValue:asc,expansion.sortValue:desc,cardNumber:asc"),
        ("filters[$and][2][type][value][$notContainsi]", "Token"),
    ]
    if card_number > 0:
        params.append(("filters[$and][1][cardNumber][$eq]", card_number))
    if filter_out_variant:
        params.append(("filters[$and][0][variantOf][id][$null]", "true"))
    if exp is not None:
        params.append(("filters[$and][2][expansion][id][$eq]", exp.value))

    try:
        resp = await request_url_async(url, headers=headers, params=params, timeout=30)
        return resp.json()
    except Exception as e:
        # Log l'erreur et continue
        async with asyncio.Lock():  # éviter d'écrire dans le fichier en même temps
            with Path("errors.log").open("a") as f:
                f.write(f"Error: {e}\n")
                f.write(
                    f"exp={exp}, lan={lan}, card_number={card_number}, filter_out_variant={filter_out_variant}\n\n"
                )
                f.flush()
        return None


async def download_variant(exp_name: str, id_card: int, variant_name: str, url: str):
    path = Path(f"cards/{exp_name}/{id_card}")
    file = path / f"{variant_name}.png"

    if file.is_file():
        print(f"{exp_name} | {id_card} | {variant_name} ALREADY OK")
        return

    img = await np_from_url_async(url)
    if img is None:
        print(f"======ERROR Failed to download: {url}======")
        return

    path.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(file), img)
    print(f"Saved: {file}")


async def fetch_cards_for_expansion(exp, lan: str):
    id_card = 1
    stop = False
    nb_fails = 0

    while not stop:
        res = await get_card(exp, lan, id_card, filter_out_variant=False)
        if res is None or len(res.get("data", [])) == 0:
            nb_fails += 1
            if nb_fails > MAX:
                stop = True
                print(
                    f"{exp.name} | {id_card} | Stopping expansion after {MAX} consecutive errors."
                )
            else:
                print(
                    f"{exp.name} | {id_card} | Fetch failed or empty data consecutively: {nb_fails}"
                )
            if res is not None:
                id_card += 1  # passer à la carte suivante
            continue

        nb_fails = 0  # succès → reset compteur
        tasks = []
        for variant in res["data"]:
            try:
                url = variant["attributes"]["artFront"]["data"]["attributes"][
                    "formats"
                ]["card"]["url"]
                nb_var = len(variant["attributes"]["variantTypes"]["data"])
                if nb_var == 0:
                    print(f"{exp.name} | {id_card} | No variantTypes available")
                    variant_name = "DEFAULT_VARIANT"
                else:
                    variant_name = variant["attributes"]["variantTypes"]["data"][0][
                        "attributes"
                    ]["name"]
                tasks.append(download_variant(exp.name, id_card, variant_name, url))
            except Exception as e:
                print(e)
                print("==================")
                print(exp, id_card)
        await asyncio.gather(*tasks)
        id_card += 1


async def fetch_all_arts() -> None:
    tasks = []
    for exp in Expansion:
        lan = exp.name.split("_")[1].lower()
        if lan not in ["fr"]:
            continue
        tasks.append(fetch_cards_for_expansion(exp, lan))

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(fetch_all_arts())
