"""Number entities for HeliaLux SmartControl."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.number import NumberEntity, NumberEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import HeliaLuxCoordinator


@dataclass(frozen=True, kw_only=True)
class HeliaLuxNumberDescription(NumberEntityDescription):
    """HeliaLux number description."""


NUMBERS = [
    HeliaLuxNumberDescription(key="white", name="White", icon="mdi:white-balance-sunny"),
    HeliaLuxNumberDescription(key="blue", name="Blue", icon="mdi:water"),
    HeliaLuxNumberDescription(key="green", name="Green", icon="mdi:leaf"),
    HeliaLuxNumberDescription(key="red", name="Red", icon="mdi:circle"),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities,
) -> None:
    """Set up HeliaLux number entities."""
    coordinator: HeliaLuxCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        HeliaLuxNumber(coordinator, entry.entry_id, description)
        for description in NUMBERS
    )


class HeliaLuxNumber(CoordinatorEntity, NumberEntity):
    """HeliaLux number entity."""

    def __init__(
        self,
        coordinator: HeliaLuxCoordinator,
        entry_id: str,
        description: HeliaLuxNumberDescription,
    ) -> None:
        """Initialize number."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_has_entity_name = True
        self._attr_unique_id = f"{entry_id}_{description.key}_number"
        self._attr_native_min_value = 0
        self._attr_native_max_value = 100
        self._attr_native_step = 1
        self._attr_native_unit_of_measurement = PERCENTAGE
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry_id)},
            "name": "HeliaLux SmartControl",
            "manufacturer": "Juwel",
            "model": "SmartControl",
        }

    @property
    def native_value(self):
        """Return current value."""
        return getattr(self.coordinator.data, self.entity_description.key)

    async def async_set_native_value(self, value: float) -> None:
        """Set channel value."""
        white = self.coordinator.data.white or 0
        blue = self.coordinator.data.blue or 0
        green = self.coordinator.data.green or 0
        red = self.coordinator.data.red or 0

        if self.entity_description.key == "white":
            white = int(value)
        elif self.entity_description.key == "blue":
            blue = int(value)
        elif self.entity_description.key == "green":
            green = int(value)
        elif self.entity_description.key == "red":
            red = int(value)

        await self.coordinator.api.set_colors(
            white=white,
            blue=blue,
            green=green,
            red=red,
        )
        await self.coordinator.async_request_refresh()