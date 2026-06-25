"""TCS Carburant integration."""

from pathlib import Path
import logging
import shutil

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, PLATFORMS


_LOGGER = logging.getLogger(__name__)


def _install_logos(hass: HomeAssistant) -> None:
    component_path = Path(__file__).parent
    source_logos = component_path / "logos"
    target_dir = Path(hass.config.path("www/tcs_carburant/logos"))

    if not source_logos.exists():
        _LOGGER.warning("TCS Carburant logos source directory does not exist")
        return

    target_dir.mkdir(parents=True, exist_ok=True)

    for logo in source_logos.iterdir():
        if not logo.is_file():
            continue

        destination = target_dir / logo.name

        if not destination.exists():
            shutil.copy2(logo, destination)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    await hass.async_add_executor_job(_install_logos, hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    await hass.async_add_executor_job(_install_logos, hass)

    entry.async_on_unload(
        entry.add_update_listener(async_update_options)
    )

    await hass.config_entries.async_forward_entry_setups(
        entry,
        PLATFORMS,
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(
        entry,
        PLATFORMS,
    )


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)