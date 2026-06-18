import aiohttp
import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import DOMAIN
from .coordinator import PlantLoverCoordinator
from .sensor import _device_info

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator: PlantLoverCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([WaterButton(coordinator, plant_id) for plant_id in coordinator.data])


class WaterButton(CoordinatorEntity, ButtonEntity):
    _attr_icon = "mdi:watering-can-outline"

    def __init__(self, coordinator: PlantLoverCoordinator, plant_id: str) -> None:
        super().__init__(coordinator)
        self._plant_id = plant_id
        self._attr_unique_id = f"{plant_id}_water"

    @property
    def _plant(self) -> dict:
        return self.coordinator.data[self._plant_id]

    @property
    def name(self) -> str:
        return f"{self._plant['name']} — podlej"

    @property
    def device_info(self) -> DeviceInfo:
        return _device_info(self.coordinator, self._plant)

    async def async_press(self) -> None:
        from datetime import datetime, timezone
        watered_at = datetime.now(timezone.utc).date().isoformat()
        url = f"{self.coordinator.base_url}/api/plants/{self._plant_id}/care-log"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json={"action": "watered", "watered_at": watered_at},
                                        timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    resp.raise_for_status()
            _LOGGER.info("Watered plant %s via HA button", self._plant["name"])
            await self.coordinator.async_request_refresh()
        except aiohttp.ClientError as exc:
            _LOGGER.error("Failed to water plant %s: %s", self._plant_id, exc)
