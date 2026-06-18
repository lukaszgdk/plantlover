from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import DOMAIN
from .coordinator import PlantLoverCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator: PlantLoverCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for plant_id in coordinator.data:
        entities.append(DaysUntilWateringSensor(coordinator, plant_id))
        entities.append(LastWateredSensor(coordinator, plant_id))
    async_add_entities(entities)


def _device_info(coordinator: PlantLoverCoordinator, plant: dict) -> DeviceInfo:
    room = plant.get("room")
    return DeviceInfo(
        identifiers={(DOMAIN, plant["id"])},
        name=plant["name"],
        manufacturer="PlantLover",
        model=plant.get("species") or plant.get("common_name") or "Plant",
        suggested_area=room["name"] if room else None,
        configuration_url=coordinator.base_url,
    )


class DaysUntilWateringSensor(CoordinatorEntity, SensorEntity):
    _attr_icon = "mdi:watering-can"
    _attr_native_unit_of_measurement = "d"

    def __init__(self, coordinator: PlantLoverCoordinator, plant_id: str) -> None:
        super().__init__(coordinator)
        self._plant_id = plant_id
        self._attr_unique_id = f"{plant_id}_days_until_watering"

    @property
    def _plant(self) -> dict:
        return self.coordinator.data[self._plant_id]

    @property
    def name(self) -> str:
        return f"{self._plant['name']} — dni do podlania"

    @property
    def native_value(self):
        return self._plant.get("days_until_watering")

    @property
    def device_info(self) -> DeviceInfo:
        return _device_info(self.coordinator, self._plant)

    @property
    def extra_state_attributes(self) -> dict:
        p = self._plant
        room = p.get("room")
        return {
            "species": p.get("species"),
            "common_name": p.get("common_name"),
            "room": room["name"] if room else None,
            "sunlight": p.get("sunlight"),
            "watering_interval_days": p.get("watering_interval_days"),
        }


class LastWateredSensor(CoordinatorEntity, SensorEntity):
    _attr_icon = "mdi:calendar-check"
    _attr_device_class = SensorDeviceClass.DATE

    def __init__(self, coordinator: PlantLoverCoordinator, plant_id: str) -> None:
        super().__init__(coordinator)
        self._plant_id = plant_id
        self._attr_unique_id = f"{plant_id}_last_watered"

    @property
    def _plant(self) -> dict:
        return self.coordinator.data[self._plant_id]

    @property
    def name(self) -> str:
        return f"{self._plant['name']} — ostatnie podlanie"

    @property
    def native_value(self):
        val = self._plant.get("last_watered")
        if not val:
            return None
        from datetime import date
        return date.fromisoformat(val[:10])

    @property
    def device_info(self) -> DeviceInfo:
        return _device_info(self.coordinator, self._plant)
