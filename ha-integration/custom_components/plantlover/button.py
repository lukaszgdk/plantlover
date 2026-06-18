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
    entities: list = [WaterButton(coordinator, plant_id) for plant_id in coordinator.data]

    # Jeden przycisk "Podlej wszystkie" per pokój
    rooms_seen: set = set()
    for plant in coordinator.data.values():
        room = plant.get("room")
        if room and room["id"] not in rooms_seen:
            rooms_seen.add(room["id"])
            entities.append(WaterRoomButton(coordinator, room["id"], room["name"]))

    async_add_entities(entities)


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


class WaterRoomButton(CoordinatorEntity, ButtonEntity):
    """Podlewa wszystkie rośliny w danym pokoju jednym kliknięciem."""
    _attr_icon = "mdi:watering-can"

    def __init__(self, coordinator: PlantLoverCoordinator, room_id: str, room_name: str) -> None:
        super().__init__(coordinator)
        self._room_id = room_id
        self._room_name = room_name
        self._attr_unique_id = f"room_{room_id}_water_all"

    @property
    def name(self) -> str:
        return f"{self._room_name} — podlej wszystkie"

    async def async_press(self) -> None:
        from datetime import datetime, timezone
        watered_at = datetime.now(timezone.utc).date().isoformat()
        plants_in_room = [
            p for p in self.coordinator.data.values()
            if (p.get("room") or {}).get("id") == self._room_id
        ]
        async with aiohttp.ClientSession() as session:
            for plant in plants_in_room:
                url = f"{self.coordinator.base_url}/api/plants/{plant['id']}/care-log"
                try:
                    async with session.post(url, json={"action": "watered", "watered_at": watered_at},
                                            timeout=aiohttp.ClientTimeout(total=10)) as resp:
                        resp.raise_for_status()
                    _LOGGER.info("Watered %s (room batch)", plant["name"])
                except aiohttp.ClientError as exc:
                    _LOGGER.error("Failed to water %s: %s", plant["id"], exc)
        await self.coordinator.async_request_refresh()
