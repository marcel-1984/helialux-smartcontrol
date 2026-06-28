"""Time entities for HeliaLux SmartControl."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import time

from homeassistant.components.time import TimeEntity, TimeEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import HeliaLuxCoordinator


@dataclass(frozen=True, kw_only=True)
class HeliaLuxTimeDescription(TimeEntityDescription):
    action: int
    source_key: str


TIMES = [
    HeliaLuxTimeDescription(
        key="target_time",
        name="Target Time",
        icon="mdi:sun-clock",
        action=13,
        source_key="target_time",
    ),
    HeliaLuxTimeDescription(
        key="cloud_time",
        name="Cloud Time",
        icon="mdi:weather-cloudy-clock",
        action=15,
        source_key="cloud_time",
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities,
) -> None:
    """Set up HeliaLux time entities."""
    coordinator: HeliaLuxCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        HeliaLuxTime(coordinator, entry.entry_id, description)
        for description in TIMES
    )


class HeliaLuxTime(CoordinatorEntity, TimeEntity):
    """HeliaLux time entity."""

    def __init__(
        self,
        coordinator: HeliaLuxCoordinator,
        entry_id: str,
        description: HeliaLuxTimeDescription,
    ) -> None:
        """Initialize time entity."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_has_entity_name = True
        self._attr_unique_id = f"{entry_id}_{description.key}_time"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry_id)},
            "name": "HeliaLux SmartControl",
            "manufacturer": "Juwel",
            "model": "SmartControl",
        }

    @property
    def native_value(self) -> time | None:
        """Return time value."""
        value = getattr(self.coordinator.data, self.entity_description.source_key)

        if not value:
            return None

        try:
            hour, minute = str(value).split(":")
            return time(int(hour), int(minute))
        except (ValueError, TypeError):
            return None

    async def async_set_value(self, value: time) -> None:
        """Set time value."""
        new_value = f"{value.hour:02d}:{value.minute:02d}"

        target_time = self.coordinator.data.target_time or "01:00"
        cloud_time = self.coordinator.data.cloud_time or "01:00"

        if self.entity_description.key == "target_time":
            target_time = new_value

        if self.entity_description.key == "cloud_time":
            cloud_time = new_value

        await self.coordinator.api.set_simulation(
            simulation_time=self.coordinator.data.simulation_time or 0,
            cloud_active=bool(self.coordinator.data.cloud_active),
            time_simulation_active=bool(self.coordinator.data.time_simulation_active),
            target_time=target_time,
            cloud_time=cloud_time,
            action=self.entity_description.action,
        )
        await self.coordinator.async_request_refresh()