import logging
from datetime import timedelta

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .api import TCSCarburantApi, top_stations
from .const import DOMAIN, FUEL_TYPES, DEFAULT_RADIUS_KM


_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(hours=6)
TOP_LIMIT = 10


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    session = async_get_clientsession(hass)
    api = TCSCarburantApi(session)

    home_lat = hass.config.latitude
    home_lng = hass.config.longitude
    radius_km = config.get("radius_km", DEFAULT_RADIUS_KM)

    async def async_update_data():
        stations = await api.fetch_stations()

        result = {}

        for fuel in FUEL_TYPES:
            result[fuel] = top_stations(
                stations,
                fuel,
                home_lat,
                home_lng,
                radius_km,
                limit=TOP_LIMIT,
            )

        return result

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=DOMAIN,
        update_method=async_update_data,
        update_interval=SCAN_INTERVAL,
    )

    await coordinator.async_config_entry_first_refresh()

    entities = []

    for fuel in FUEL_TYPES:
        entities.append(TCSBestFuelSensor(coordinator, fuel))

        for rank in range(1, TOP_LIMIT + 1):
            entities.append(TCSRankedFuelSensor(coordinator, fuel, rank))

    async_add_entities(entities)


class TCSBestFuelSensor(SensorEntity):
    def __init__(self, coordinator, fuel_type):
        self.coordinator = coordinator
        self.fuel_type = fuel_type

        self._attr_name = f"TCS {fuel_type} moins cher"
        self._attr_unique_id = f"tcs_carburant_{fuel_type.lower()}_moins_cher"
        self._attr_native_unit_of_measurement = "CHF/l"
        self._attr_icon = "mdi:gas-station"

    @property
    def native_value(self):
        stations = self.coordinator.data.get(self.fuel_type)

        if not stations:
            return None

        return stations[0]["price"]

    @property
    def extra_state_attributes(self):
        stations = self.coordinator.data.get(self.fuel_type)

        if not stations:
            return {}

        best = stations[0]

        return {
            "station": best["name"],
            "brand": best["brand"],
            "address": best["address"],
            "city": best.get("city"),
            "logo": best.get("logo"),
            "station_display": best.get("station_display"),
            "distance_km": best["distance_km"],
            "latitude": best["lat"],
            "longitude": best["lng"],
            "fiability_level": best["fiability_level"],
            "fiability_score": best["fiability_score"],
            "last_price_update": best["last_price_update"],
            "maps_url": best.get("maps_url"),
            "top_3": stations[:3],
            "top_10": stations[:10],
        }

    @property
    def available(self):
        return self.coordinator.last_update_success

    async def async_update(self):
        await self.coordinator.async_request_refresh()


class TCSRankedFuelSensor(SensorEntity):
    def __init__(self, coordinator, fuel_type, rank):
        self.coordinator = coordinator
        self.fuel_type = fuel_type
        self.rank = rank
        self.index = rank - 1

        self._attr_name = f"TCS {fuel_type} Top {rank}"
        self._attr_unique_id = f"tcs_carburant_{fuel_type.lower()}_top_{rank}"
        self._attr_native_unit_of_measurement = "CHF/l"
        self._attr_icon = "mdi:gas-station"

    @property
    def native_value(self):
        station = self._station()

        if not station:
            return None

        return station["price"]

    @property
    def extra_state_attributes(self):
        station = self._station()

        if not station:
            return {}

        return {
            "rank": self.rank,
            "fuel_type": self.fuel_type,
            "station": station["name"],
            "brand": station["brand"],
            "address": station["address"],
            "city": station.get("city"),
            "logo": station.get("logo"),
            "station_display": station.get("station_display"),
            "distance_km": station["distance_km"],
            "latitude": station["lat"],
            "longitude": station["lng"],
            "fiability_level": station["fiability_level"],
            "fiability_score": station["fiability_score"],
            "last_price_update": station["last_price_update"],
            "maps_url": station.get("maps_url"),
        }

    def _station(self):
        stations = self.coordinator.data.get(self.fuel_type)

        if not stations:
            return None

        if len(stations) <= self.index:
            return None

        return stations[self.index]

    @property
    def available(self):
        return self.coordinator.last_update_success and self._station() is not None

    async def async_update(self):
        await self.coordinator.async_request_refresh()