"""Config flow for TCS Carburant."""

import voluptuous as vol

from homeassistant import config_entries

from .const import (
    DOMAIN,
    DEFAULT_RADIUS_KM,
    DEFAULT_HIDE_OUTDATED,
    DEFAULT_UPDATE_INTERVAL_HOURS,
    MIN_RADIUS_KM,
    MAX_RADIUS_KM,
    MIN_UPDATE_INTERVAL_HOURS,
    MAX_UPDATE_INTERVAL_HOURS,
    CONF_RADIUS_KM,
    CONF_HIDE_OUTDATED,
    CONF_UPDATE_INTERVAL_HOURS,
)


def build_schema(
    radius_km: int,
    hide_outdated: bool,
    update_interval_hours: int,
) -> vol.Schema:
    return vol.Schema(
        {
            vol.Optional(
                CONF_RADIUS_KM,
                default=radius_km,
            ): vol.All(
                vol.Coerce(int),
                vol.Range(
                    min=MIN_RADIUS_KM,
                    max=MAX_RADIUS_KM,
                ),
            ),
            vol.Optional(
                CONF_HIDE_OUTDATED,
                default=hide_outdated,
            ): bool,
            vol.Optional(
                CONF_UPDATE_INTERVAL_HOURS,
                default=update_interval_hours,
            ): vol.All(
                vol.Coerce(int),
                vol.Range(
                    min=MIN_UPDATE_INTERVAL_HOURS,
                    max=MAX_UPDATE_INTERVAL_HOURS,
                ),
            ),
        }
    )


class TCSCarburantConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for TCS Carburant."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            await self.async_set_unique_id(DOMAIN)
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title="TCS Carburant",
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=build_schema(
                DEFAULT_RADIUS_KM,
                DEFAULT_HIDE_OUTDATED,
                DEFAULT_UPDATE_INTERVAL_HOURS,
            ),
        )

    @staticmethod
    def async_get_options_flow(config_entry):
        return TCSCarburantOptionsFlow(config_entry)


class TCSCarburantOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for TCS Carburant."""

    def __init__(self, config_entry):
        self._config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(
                title="",
                data=user_input,
            )

        radius_km = self._config_entry.options.get(
            CONF_RADIUS_KM,
            self._config_entry.data.get(
                CONF_RADIUS_KM,
                DEFAULT_RADIUS_KM,
            ),
        )

        hide_outdated = self._config_entry.options.get(
            CONF_HIDE_OUTDATED,
            self._config_entry.data.get(
                CONF_HIDE_OUTDATED,
                DEFAULT_HIDE_OUTDATED,
            ),
        )

        update_interval_hours = self._config_entry.options.get(
            CONF_UPDATE_INTERVAL_HOURS,
            self._config_entry.data.get(
                CONF_UPDATE_INTERVAL_HOURS,
                DEFAULT_UPDATE_INTERVAL_HOURS,
            ),
        )

        return self.async_show_form(
            step_id="init",
            data_schema=build_schema(
                radius_km,
                hide_outdated,
                update_interval_hours,
            ),
        )