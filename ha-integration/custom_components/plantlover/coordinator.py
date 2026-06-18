import logging
from datetime import timedelta

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(minutes=30)


class PlantLoverCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, base_url: str) -> None:
        super().__init__(hass, _LOGGER, name="PlantLover", update_interval=SCAN_INTERVAL)
        self.base_url = base_url.rstrip("/")

    async def _async_update_data(self) -> dict:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/plants", timeout=aiohttp.ClientTimeout(total=15)) as resp:
                    resp.raise_for_status()
                    plants: list[dict] = await resp.json()
        except aiohttp.ClientError as exc:
            raise UpdateFailed(f"Cannot connect to PlantLover: {exc}") from exc

        return {plant["id"]: plant for plant in plants}
