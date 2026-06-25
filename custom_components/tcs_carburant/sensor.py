"""Sensors for TCS Carburant."""

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import FUEL_TYPES, TOP_LIMIT
from .coordinator import TCSCarburantCoordinator


async def async_setup_entry(hass, entry, async_add_entities):
    session = async_get_clientsession(hass)

    coordinator = TCSCarburantCoordinator(
        hass,
        entry,
        session,
    )

    await coordinator.async_config_entry_first_refresh()

    entities = []

    for fuel in FUEL_TYPES:
        entities.append(TCSBestFuelSensor(coordinator, fuel))

        for rank in range(1, TOP_LIMIT + 1):
            entities.append(
                TCSRankedFuelSensor(
                    coordinator,
                    fuel,
                    rank,
                )
            )

    async_add_entities(entities)


class TCSBaseSensor(CoordinatorEntity, SensorEntity):
    _attr_icon = "mdi:gas-station"
    _attr_native_unit_of_measurement = "CHF/l"

    def __init__(self, coordinator, fuel_type):
        super().__init__(coordinator)
        self.fuel_type = fuel_type

    @property
    def available(self):
        return (
            super().available
            and self.station is not None
        )

    @property
    def native_value(self):
        if not self.station:
            return None

        return self.station["price"]

    @property
    def extra_state_attributes(self):
        station = self.station

        if not station:
            return {}

        return {
            "station": station["name"],
            "brand": station["brand"],
            "raw_brand": station.get("raw_brand"),
            "address": station["address"],
            "city": station.get("city"),
            "logo": station.get("logo"),
            "station_display": station.get("station_display"),
            "distance_km": station["distance_km"],
            # Uncomment these two lines if you want stations visible on Home Assistant Map
            # "latitude": station["lat"],
            # "longitude": station["lng"],
            "fiability_level": station["fiability_level"],
            "fiability_score": station["fiability_score"],
            "last_price_update": station["last_price_update"],
            "price_age_days": station.get("price_age_days"),
            "maps_url": station.get("maps_url"),
        }


class TCSBestFuelSensor(TCSBaseSensor):
    def __init__(self, coordinator, fuel_type):
        super().__init__(coordinator, fuel_type)

        self._attr_name = f"TCS {fuel_type} moins cher"
        self._attr_unique_id = f"tcs_carburant_{fuel_type.lower()}_moins_cher"

    @property
    def station(self):
        stations = self.coordinator.data.get(self.fuel_type)

        if not stations:
            return None

        return stations[0]

    @property
    def extra_state_attributes(self):
        attributes = super().extra_state_attributes

        stations = self.coordinator.data.get(self.fuel_type)

        if stations:
            attributes["top_3"] = stations[:3]
            attributes["top_10"] = stations[:10]

        return attributes


class TCSRankedFuelSensor(TCSBaseSensor):
    def __init__(self, coordinator, fuel_type, rank):
        super().__init__(coordinator, fuel_type)

        self.rank = rank
        self.index = rank - 1

        self._attr_name = f"TCS {fuel_type} Top {rank}"
        self._attr_unique_id = f"tcs_carburant_{fuel_type.lower()}_top_{rank}"

    @property
    def station(self):
        stations = self.coordinator.data.get(self.fuel_type)

        if not stations:
            return None

        if len(stations) <= self.index:
            return None

        return stations[self.index]

    @property
    def extra_state_attributes(self):
        attributes = super().extra_state_attributes
        attributes["rank"] = self.rank
        attributes["fuel_type"] = self.fuel_type
        return attributes