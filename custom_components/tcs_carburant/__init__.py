from pathlib import Path
import shutil
import logging

from homeassistant.core import HomeAssistant


_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config):
    component_path = Path(__file__).parent
    source_logos = component_path / "logos"

    target_dir = Path(hass.config.path("www/tcs_carburant/logos"))

    target_dir.mkdir(parents=True, exist_ok=True)

    for logo in source_logos.glob("*"):
        destination = target_dir / logo.name

        if not destination.exists():
            shutil.copy2(logo, destination)

    _LOGGER.info("TCS Carburant logos installed")

    return True