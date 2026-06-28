"""Light entity for HeliaLux SmartControl."""

from __future__ import annotations

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_RGB_COLOR,
    ColorMode,
    LightEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import HeliaLuxCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities,
) -> None:
    """Set up HeliaLux light."""
    coordinator: HeliaLuxCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([HeliaLuxLight(coordinator, entry.entry_id)])


class HeliaLuxLight(CoordinatorEntity, LightEntity):
    """HeliaLux SmartControl light."""

    _attr_has_entity_name = True
    _attr_name = "Light"
    _attr_supported_color_modes = {ColorMode.RGB}
    _attr_color_mode = ColorMode.RGB
    _attr_supported_features = 0

    def __init__(self, coordinator: HeliaLuxCoordinator, entry_id: str) -> None:
        """Initialize light."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry_id}_light"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry_id)},
            "name": "HeliaLux SmartControl",
            "manufacturer": "Juwel",
            "model": "SmartControl",
        }

    @property
    def is_on(self) -> bool:
        """Return if light is on."""
        return any(
            value and value > 0
            for value in (
                self.coordinator.data.white,
                self.coordinator.data.blue,
                self.coordinator.data.green,
                self.coordinator.data.red,
            )
        )

    @property
    def rgb_color(self) -> tuple[int, int, int]:
        """Return approximate RGB color."""
        red = int((self.coordinator.data.red or 0) * 2.55)
        green = int((self.coordinator.data.green or 0) * 2.55)
        blue = int((self.coordinator.data.blue or 0) * 2.55)
        return red, green, blue

    @property
    def brightness(self) -> int:
        """Return brightness."""
        values = [
            self.coordinator.data.white or 0,
            self.coordinator.data.blue or 0,
            self.coordinator.data.green or 0,
            self.coordinator.data.red or 0,
        ]

        if max(values) == 0:
            return 0

        return round(max(values) * 255 / 100)

    async def async_turn_on(self, **kwargs) -> None:
        """Turn on or set color."""
        white = self.coordinator.data.white or 90
        blue = self.coordinator.data.blue or 40
        green = self.coordinator.data.green or 8
        red = self.coordinator.data.red or 18

        if ATTR_RGB_COLOR in kwargs:
            rgb = kwargs[ATTR_RGB_COLOR]
            red = round(rgb[0] / 2.55)
            green = round(rgb[1] / 2.55)
            blue = round(rgb[2] / 2.55)

        if ATTR_BRIGHTNESS in kwargs:
            factor = kwargs[ATTR_BRIGHTNESS] / 255

            white = round(white * factor)
            blue = round(blue * factor)
            green = round(green * factor)
            red = round(red * factor)

        await self.coordinator.api.set_colors(
            white=white,
            blue=blue,
            green=green,
            red=red,
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Set light to low night mode."""
        await self.coordinator.api.set_colors(
            white=1,
            blue=1,
            green=0,
            red=1,
        )
        await self.coordinator.async_request_refresh()