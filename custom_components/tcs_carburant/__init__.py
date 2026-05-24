"""TCS Carburant integration."""

from pathlib import Path
import logging
import shutil

from homeassistant.core import HomeAssistant


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


async def async_setup(hass: HomeAssistant, config):
    await hass.async_add_executor_job(_install_logos, hass)

    _LOGGER.info("TCS Carburant logos installed")

    return True
