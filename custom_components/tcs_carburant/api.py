import math
import aiohttp

from datetime import datetime, timezone

from .const import URL


BODY = {
    "structuredQuery": {
        "from": [{"collectionId": "stations"}],
        "where": {
            "fieldFilter": {
                "field": {"fieldPath": "isDeleted"},
                "op": "EQUAL",
                "value": {"booleanValue": False},
            }
        },
    }
}


def _get_value(field):
    if not field:
        return None

    if "stringValue" in field:
        return field["stringValue"]

    if "doubleValue" in field:
        return field["doubleValue"]

    if "integerValue" in field:
        return int(field["integerValue"])

    if "booleanValue" in field:
        return field["booleanValue"]

    if "timestampValue" in field:
        return field["timestampValue"]

    return None


def distance_km(lat1, lon1, lat2, lon2):
    radius = 6371

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )

    return radius * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def extract_city(address):
    if not address:
        return ""

    parts = address.split(",")

    if len(parts) < 2:
        return ""

    city_part = parts[-1].strip()
    city_words = city_part.split(" ")

    if len(city_words) >= 2 and city_words[0].isdigit():
        return " ".join(city_words[1:])

    return city_part


def clean_brand(brand, name):
    if not brand:
        return ""

    brand = brand.strip()

    if brand.upper() == "UNDEFINED":
        return ""

    if name and brand.lower() in name.lower():
        return ""

    return brand


def brand_logo(brand):
    if not brand:
        return "/local/tcs_carburant/logos/default.png"

    brand_clean = brand.lower().replace(" ", "_")

    mapping = {
        "agrola": "agrola.png",
        "avia": "avia.png",
        "bp": "bp.png",
        "coop": "coop.png",
        "eni": "eni.png",
        "jubin": "jubin.png",
        "migrol": "migrol.png",
        "miniprix": "miniprix.png",
        "ruedirussel": "ruedirussel.png",
        "shell": "shell.png",
        "socar": "socar.png",
        "tamoil": "tamoil.png",
    }

    return "/local/tcs_carburant/logos/" + mapping.get(
        brand_clean,
        "default.png",
    )


def price_is_recent(last_update, max_age_days=20):
    if not last_update:
        return False

    try:
        update_date = datetime.fromisoformat(
            last_update.replace("Z", "+00:00")
        )

        now = datetime.now(timezone.utc)
        age_days = (now - update_date).days

        return age_days <= max_age_days

    except Exception:
        return False


class TCSCarburantApi:
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session

    async def fetch_stations(self):
        async with self.session.post(URL, json=BODY) as response:
            response.raise_for_status()
            data = await response.json()

        stations = []

        for item in data:
            document = item.get("document")

            if not document:
                continue

            fields = document.get("fields", {})

            try:
                name = _get_value(fields.get("displayName"))
                address = _get_value(fields.get("formattedAddress"))
                brand = _get_value(fields.get("brand", {"stringValue": "UNKNOWN"}))

                location_fields = fields["location"]["mapValue"]["fields"]
                lat = _get_value(location_fields.get("lat"))
                lng = _get_value(location_fields.get("lng"))

                fuel_fields = fields["fuelCollection"]["mapValue"]["fields"]

                station = {
                    "id": document["name"].split("/")[-1],
                    "name": name,
                    "address": address,
                    "brand": brand,
                    "lat": lat,
                    "lng": lng,
                    "fuels": {},
                }

                for fuel_type, fuel_data in fuel_fields.items():
                    fuel_info = fuel_data["mapValue"]["fields"]

                    if fuel_info.get("isDeleted", {}).get("booleanValue") is True:
                        continue

                    price = _get_value(fuel_info.get("displayPrice"))

                    fiability = (
                        fuel_info
                        .get("fiability", {})
                        .get("mapValue", {})
                        .get("fields", {})
                    )

                    level = _get_value(
                        fiability.get("level", {"stringValue": "UNKNOWN"})
                    )

                    score = _get_value(
                        fiability.get("score", {"doubleValue": 0})
                    )

                    last_update = _get_value(
                        fiability.get("lastPriceUpdate")
                    )

                    if price:
                        station["fuels"][fuel_type] = {
                            "price": round(float(price), 3),
                            "fiability_level": level,
                            "fiability_score": score,
                            "last_price_update": last_update,
                        }

                stations.append(station)

            except Exception:
                continue

        return stations


def top_stations(stations, fuel_type, home_lat, home_lng, radius_km, limit=10):
    candidates = []

    for station in stations:
        if fuel_type not in station["fuels"]:
            continue

        dist = distance_km(
            home_lat,
            home_lng,
            station["lat"],
            station["lng"],
        )

        if dist <= radius_km:
            fuel = station["fuels"][fuel_type]

            if not price_is_recent(
                fuel["last_price_update"],
                max_age_days=20,
            ):
                continue

            city = extract_city(station["address"])
            display_brand = clean_brand(station["brand"], station["name"])
            logo = brand_logo(station["brand"])

            candidates.append({
                "name": station["name"],
                "brand": display_brand,
                "raw_brand": station["brand"],
                "address": station["address"],
                "city": city,
                "logo": logo,
                "lat": station["lat"],
                "lng": station["lng"],
                "distance_km": round(dist, 2),
                "price": round(fuel["price"], 3),
                "fiability_level": fuel["fiability_level"],
                "fiability_score": fuel["fiability_score"],
                "last_price_update": fuel["last_price_update"],
                "maps_url": (
                    "https://www.google.com/maps/search/?api=1&query="
                    f"{station['lat']},{station['lng']}"
                ),
                "station_display": (
                    f"<img src='{logo}' width='28' "
                    f"style='vertical-align:middle;margin-right:8px;'>"
                    f"<b>{display_brand + ' - ' if display_brand else ''}"
                    f"{station['name']}</b><br>"
                    f"<span style='font-size:11px;opacity:0.75'>{city}</span>"
                ),
            })

    candidates = sorted(
        candidates,
        key=lambda x: (
            x["price"],
            x["distance_km"],
        ),
    )

    return candidates[:limit]