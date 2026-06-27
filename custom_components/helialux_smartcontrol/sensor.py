"""Sensors for HeliaLux SmartControl."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import HeliaLuxCoordinator


@dataclass
class HeliaLuxSensorDescription:
    key: str
    name: str
    unit: str | None = None
    icon: str | None = None


SENSORS = [
    HeliaLuxSensorDescription("white", "White", PERCENTAGE, "mdi:white-balance-sunny"),
    HeliaLuxSensorDescription("blue", "Blue", PERCENTAGE, "mdi:water"),
    HeliaLuxSensorDescription("green", "Green", PERCENTAGE, "mdi:leaf"),
    HeliaLuxSensorDescription("red", "Red", PERCENTAGE, "mdi:circle"),
    HeliaLuxSensorDescription("controller_time", "Controller Time", None, "mdi:clock-outline"),
    HeliaLuxSensorDescription("simulation_time", "Simulation Time", None, "mdi:timer-outline"),
    HeliaLuxSensorDescription("cloud_active", "Cloud Active", None, "mdi:weather-cloudy"),
    HeliaLuxSensorDescription("time_simulation_active", "Time Simulation Active", None, "mdi:timer-cog-outline"),
    HeliaLuxSensorDescription("target_time", "Target Time", None, "mdi:sun-clock"),
    HeliaLuxSensorDescription("cloud_time", "Cloud Time", None, "mdi:weather-cloudy-clock"),
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
        self._attr_name = f"HeliaLux {description.name}"
        self._attr_unique_id = f"{entry_id}_{description.key}"
        self._attr_native_unit_of_measurement = description.unit
        self._attr_icon = description.icon
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