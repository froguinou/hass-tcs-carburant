"""Coordinator for TCS Carburant."""

from datetime import timedelta
import logging

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .api import TCSCarburantApi, top_stations
from .const import (
    DOMAIN,
    FUEL_TYPES,
    TOP_LIMIT,
    DEFAULT_RADIUS_KM,
    DEFAULT_HIDE_OUTDATED,
    DEFAULT_UPDATE_INTERVAL_HOURS,
    CONF_RADIUS_KM,
    CONF_HIDE_OUTDATED,
    CONF_UPDATE_INTERVAL_HOURS,
)


_LOGGER = logging.getLogger(__name__)


class TCSCarburantCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, entry, session):
        self.hass = hass
        self.entry = entry
        self.api = TCSCarburantApi(session)

        self.home_lat = hass.config.latitude
        self.home_lng = hass.config.longitude

        self.radius_km = self._option(
            CONF_RADIUS_KM,
            DEFAULT_RADIUS_KM,
        )

        self.hide_outdated = self._option(
            CONF_HIDE_OUTDATED,
            DEFAULT_HIDE_OUTDATED,
        )

        update_interval_hours = self._option(
            CONF_UPDATE_INTERVAL_HOURS,
            DEFAULT_UPDATE_INTERVAL_HOURS,
        )

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(hours=update_interval_hours),
        )

    def _option(self, key, default):
        return self.entry.options.get(
            key,
            self.entry.data.get(
                key,
                default,
            ),
        )

    async def _async_update_data(self):
        stations = await self.api.fetch_stations(
            self.home_lat,
            self.home_lng,
            self.radius_km,
        )

        result = {}

        for fuel in FUEL_TYPES:
            result[fuel] = top_stations(
                stations=stations,
                fuel_type=fuel,
                home_lat=self.home_lat,
                home_lng=self.home_lng,
                radius_km=self.radius_km,
                limit=TOP_LIMIT,
                hide_outdated=self.hide_outdated,
            )

        return result