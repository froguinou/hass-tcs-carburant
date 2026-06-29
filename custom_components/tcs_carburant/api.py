"""TCS Carburant API client."""

import math
import aiohttp

from .const import FUEL_TYPES, OUTDATED_LEVEL


URL = (
    "https://europe-west6-tcs-digitalbackend.cloudfunctions.net/"
    "benzinGetStationByBbox"
)

GRID_SIZE = 4


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


def build_bbox(lat, lon, radius_km):
    lat_delta = radius_km / 111.0
    lon_delta = radius_km / (111.0 * math.cos(math.radians(lat)))

    return [
        lon - lon_delta,
        lat - lat_delta,
        lon + lon_delta,
        lat + lat_delta,
    ]


def split_bbox(bbox, grid_size=GRID_SIZE):
    min_lon, min_lat, max_lon, max_lat = bbox

    lon_step = (max_lon - min_lon) / grid_size
    lat_step = (max_lat - min_lat) / grid_size

    boxes = []

    for x in range(grid_size):
        for y in range(grid_size):
            boxes.append(
                [
                    min_lon + x * lon_step,
                    min_lat + y * lat_step,
                    min_lon + (x + 1) * lon_step,
                    min_lat + (y + 1) * lat_step,
                ]
            )

    return boxes


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
        "laposte": "laposte.png",
        "migrol": "migrol.png",
        "miniprix": "miniprix.png",
        "ruedirussel": "ruedirussel.png",
        "shell": "shell.png",
        "simond": "simond.png",
        "socar": "socar.png",
        "tamoil": "tamoil.png",
    }

    return "/local/tcs_carburant/logos/" + mapping.get(
        brand_clean,
        "default.png",
    )


def fiability_display(level):
    if level == "CONFIDENT":
        return "OK"

    if level == "FEW_RECENT_PRICES":
        return "Moyen"

    if level == "OLD_LAST_UPDATE":
        return "Vieux"

    if level == "OUTDATED_LAST_PRICE_UPDATE":
        return "Très vieux"

    return level or "N/D"


def fiability_color(level):
    if level == "CONFIDENT":
        return "#00ff00"

    if level == "FEW_RECENT_PRICES":
        return "#ffd166"

    if level == "OLD_LAST_UPDATE":
        return "#ff8c42"

    if level == "OUTDATED_LAST_PRICE_UPDATE":
        return "#ff4d4d"

    return "rgba(255,255,255,0.6)"


def normalize_fuel_type(value):
    if not value:
        return None

    value = str(value).upper()

    if value in ["SP95", "SP98", "DIESEL"]:
        return value

    if value in ["95", "E5", "UNLEADED95"]:
        return "SP95"

    if value in ["98", "UNLEADED98"]:
        return "SP98"

    if value in ["D", "GASOIL"]:
        return "DIESEL"

    return value


def get_raw_items(data):
    if isinstance(data, list):
        return data

    if not isinstance(data, dict):
        return []

    return (
        data.get("stations")
        or data.get("data")
        or data.get("results")
        or data.get("features")
        or []
    )


def normalize_station(raw, requested_fuel_type):
    if not isinstance(raw, dict):
        return None

    if raw.get("cluster") is True:
        return None

    if raw.get("isDeleted") is True:
        return None

    properties = raw.get("properties", raw)
    geometry = raw.get("geometry", {})

    real_fuel_type = normalize_fuel_type(
        properties.get("fuel")
        or properties.get("fuelType")
        or properties.get("type")
        or requested_fuel_type
    )

    requested_fuel_type = normalize_fuel_type(requested_fuel_type)

    if real_fuel_type != requested_fuel_type:
        return None

    name = properties.get("displayName") or properties.get("name") or ""
    address = properties.get("formattedAddress") or properties.get("address") or ""
    brand = properties.get("brand") or "UNKNOWN"

    lat = properties.get("latitude") or properties.get("lat")
    lng = properties.get("longitude") or properties.get("lng")

    if geometry and lat is None and lng is None:
        coordinates = geometry.get("coordinates", [])

        if len(coordinates) >= 2:
            lng = coordinates[0]
            lat = coordinates[1]

    price = (
        properties.get("price")
        or properties.get("displayPrice")
        or properties.get("amount")
    )

    if price is None:
        return None

    try:
        price = round(float(price), 3)
    except (ValueError, TypeError):
        return None

    fiability = (
        properties.get("fiability")
        or properties.get("fiabilityLevel")
        or properties.get("fiability_level")
        or "UNKNOWN"
    )

    station_id = (
        properties.get("id")
        or properties.get("stationId")
        or properties.get("documentId")
        or f"{brand}_{name}_{lat}_{lng}_{real_fuel_type}"
    )

    if lat is None or lng is None:
        return None

    return {
        "id": str(station_id),
        "name": name.strip(),
        "address": address.strip(),
        "brand": brand.strip(),
        "lat": float(lat),
        "lng": float(lng),
        "fuels": {
            real_fuel_type: {
                "price": price,
                "fiability_level": fiability,
                "fiability_score": 0,
                "last_price_update": None,
            }
        },
    }


class TCSCarburantApi:
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session

    async def fetch_stations_by_fuel(
        self,
        fuel_type,
        home_lat,
        home_lng,
        radius_km,
    ):
        main_bbox = build_bbox(home_lat, home_lng, radius_km)
        bboxes = split_bbox(main_bbox)

        headers = {
            "Content-Type": "application/json",
            "Origin": "https://benzin.tcs.ch",
            "Referer": "https://benzin.tcs.ch/",
            "User-Agent": (
                "Mozilla/5.0 "
                "(Home Assistant TCS Carburant custom integration)"
            ),
        }

        stations = {}
        requested_fuel = normalize_fuel_type(fuel_type)

        for bbox in bboxes:
            payload = {
                "zoom": 15,
                "pixelRatio": 1,
                "bbox": bbox,
                "filters": {
                    "fuel": requested_fuel,
                    "brands": [],
                },
            }

            async with self.session.post(
                URL,
                json=payload,
                headers=headers,
            ) as response:
                response.raise_for_status()
                data = await response.json()

            for raw in get_raw_items(data):
                station = normalize_station(raw, requested_fuel)

                if not station:
                    continue

                key = f"{station['id']}_{requested_fuel}"
                stations[key] = station

        return list(stations.values())

    async def fetch_stations(
        self,
        home_lat,
        home_lng,
        radius_km,
    ):
        all_stations = []

        for fuel_type in FUEL_TYPES:
            stations = await self.fetch_stations_by_fuel(
                fuel_type,
                home_lat,
                home_lng,
                radius_km,
            )

            all_stations.extend(stations)

        return all_stations


def top_stations(
    stations,
    fuel_type,
    home_lat,
    home_lng,
    radius_km,
    limit,
    hide_outdated,
):
    candidates = []
    fuel_type = normalize_fuel_type(fuel_type)

    for station in stations:
        if fuel_type not in station["fuels"]:
            continue

        dist = distance_km(
            home_lat,
            home_lng,
            station["lat"],
            station["lng"],
        )

        if dist > radius_km:
            continue

        fuel = station["fuels"][fuel_type]

        if fuel["price"] is None:
            continue

        if hide_outdated and fuel["fiability_level"] == OUTDATED_LEVEL:
            continue

        city = extract_city(station["address"])
        display_brand = clean_brand(station["brand"], station["name"])
        logo = brand_logo(station["brand"])

        reliability_text = fiability_display(fuel["fiability_level"])
        reliability_color = fiability_color(fuel["fiability_level"])

        candidates.append(
            {
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
                "price_age_days": None,
                "maps_url": (
                    "https://www.google.com/maps/search/?api=1&query="
                    f"{station['lat']},{station['lng']}"
                ),
                "station_display": (
                    f"<a href='https://www.google.com/maps/search/?api=1&query="
                    f"{station['lat']},{station['lng']}' target='_blank' "
                    f"style='text-decoration:none;color:inherit;display:flex;align-items:center;'>"
                    f"<img src='{logo}' width='34' "
                    f"style='margin-right:9px;flex-shrink:0;'>"
                    f"<div style='line-height:1.25;overflow:hidden;'>"
                    f"<div style='font-weight:700;font-size:13px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;'>"
                    f"{display_brand + ' - ' if display_brand else ''}{station['name']}"
                    f"</div>"
                    f"<div style='font-size:11px;opacity:0.8;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;'>"
                    f"{city} · {round(dist, 1)} km · "
                    f"<span style='color:{reliability_color};font-weight:700'>{reliability_text}</span>"
                    f"</div>"
                    f"</div>"
                    f"</a>"
                ),
            }
        )

    candidates = sorted(
        candidates,
        key=lambda x: (
            x["price"],
            x["distance_km"],
        ),
    )

    return candidates[:limit]