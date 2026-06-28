"""Button entities for HeliaLux SmartControl."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import HeliaLuxCoordinator


@dataclass(frozen=True, kw_only=True)
class HeliaLuxButtonDescription(ButtonEntityDescription):
    white: int
    blue: int
    green: int
    red: int


BUTTONS = [
    HeliaLuxButtonDescription(
        key="mode_day",
        name="Day Mode",
        icon="mdi:white-balance-sunny",
        white=90,
        blue=40,
        green=8,
        red=18,
    ),
    HeliaLuxButtonDescription(
        key="mode_sunset",
        name="Sunset Mode",
        icon="mdi:weather-sunset-down",
        white=35,
        blue=14,
        green=2,
        red=10,
    ),
    HeliaLuxButtonDescription(
        key="mode_night",
        name="Night Mode",
        icon="mdi:weather-night",
        white=1,
        blue=1,
        green=0,
        red=1,
    ),
    HeliaLuxButtonDescription(
        key="mode_maintenance",
        name="Maintenance Mode",
        icon="mdi:wrench",
        white=100,
        blue=45,
        green=12,
        red=25,
    ),
    HeliaLuxButtonDescription(
        key="mode_photo",
        name="Photo Mode",
        icon="mdi:camera",
        white=95,
        blue=45,
        green=10,
        red=20,
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities,
) -> None:
    """Set up HeliaLux buttons."""
    coordinator: HeliaLuxCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        HeliaLuxButton(coordinator, entry.entry_id, description)
        for description in BUTTONS
    )


class HeliaLuxButton(CoordinatorEntity, ButtonEntity):
    """HeliaLux mode button."""

    def __init__(
        self,
        coordinator: HeliaLuxCoordinator,
        entry_id: str,
        description: HeliaLuxButtonDescription,
    ) -> None:
        """Initialize button."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_has_entity_name = True
        self._attr_unique_id = f"{entry_id}_{description.key}_button"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry_id)},
            "name": "HeliaLux SmartControl",
            "manufacturer": "Juwel",
            "model": "SmartControl",
        }

    async def async_press(self) -> None:
        """Apply preset mode."""
        await self.coordinator.api.set_colors(
            white=self.entity_description.white,
            blue=self.entity_description.blue,
            green=self.entity_description.green,
            red=self.entity_description.red,
        )
        await self.coordinator.async_request_refresh()