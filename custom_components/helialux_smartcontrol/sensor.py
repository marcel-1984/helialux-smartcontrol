"""Sensors for HeliaLux SmartControl."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import HeliaLuxCoordinator


@dataclass(frozen=True, kw_only=True)
class HeliaLuxSensorDescription(SensorEntityDescription):
    """HeliaLux sensor description."""


# Names are no longer set here; they come from translations/<lang>.json via
# translation_key. This also makes the generated entity_ids deterministic,
# which prevents the "undefinedtype" entity_id fallback from ever happening
# again on a fresh install.
SENSORS = [
    HeliaLuxSensorDescription(
        key="white",
        translation_key="white",
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:white-balance-sunny",
    ),
    HeliaLuxSensorDescription(
        key="blue",
        translation_key="blue",
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:water",
    ),
    HeliaLuxSensorDescription(
        key="green",
        translation_key="green",
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:leaf",
    ),
    HeliaLuxSensorDescription(
        key="red",
        translation_key="red",
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:circle",
    ),
    HeliaLuxSensorDescription(
        key="controller_time",
        translation_key="controller_time",
        icon="mdi:clock-outline",
    ),
    HeliaLuxSensorDescription(
        key="simulation_time",
        translation_key="simulation_time",
        icon="mdi:timer-outline",
    ),
    HeliaLuxSensorDescription(
        key="cloud_active",
        translation_key="cloud_active",
        icon="mdi:weather-cloudy",
    ),
    HeliaLuxSensorDescription(
        key="time_simulation_active",
        translation_key="time_simulation_active",
        icon="mdi:timer-cog-outline",
    ),
    HeliaLuxSensorDescription(
        key="target_time",
        translation_key="target_time",
        icon="mdi:sun-clock",
    ),
    HeliaLuxSensorDescription(
        key="cloud_time",
        translation_key="cloud_time",
        icon="mdi:weather-cloudy-clock",
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities,
) -> None:
    """Set up HeliaLux sensors."""
    coordinator: HeliaLuxCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        HeliaLuxSensor(coordinator, entry.entry_id, description)
        for description in SENSORS
    )


class HeliaLuxSensor(CoordinatorEntity, SensorEntity):
    """HeliaLux sensor."""

    def __init__(
        self,
        coordinator: HeliaLuxCoordinator,
        entry_id: str,
        description: HeliaLuxSensorDescription,
    ) -> None:
        """Initialize sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_has_entity_name = True
        self._attr_unique_id = f"{entry_id}_{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry_id)},
            "name": "HeliaLux SmartControl",
            "manufacturer": "Juwel",
            "model": "SmartControl",
        }

    @property
    def native_value(self) -> Any:
        """Return sensor value."""
        return getattr(self.coordinator.data, self.entity_description.key)