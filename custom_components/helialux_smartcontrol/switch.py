"""Switch entities for HeliaLux SmartControl."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import HeliaLuxCoordinator


@dataclass(frozen=True, kw_only=True)
class HeliaLuxSwitchDescription(SwitchEntityDescription):
    action: int


SWITCHES = [
    HeliaLuxSwitchDescription(
        key="cloud_active",
        name="Cloud Simulation",
        icon="mdi:weather-cloudy",
        action=14,
    ),
    HeliaLuxSwitchDescription(
        key="time_simulation_active",
        name="Time Simulation",
        icon="mdi:timer-cog-outline",
        action=12,
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities,
) -> None:
    coordinator: HeliaLuxCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        HeliaLuxSwitch(coordinator, entry.entry_id, description)
        for description in SWITCHES
    )


class HeliaLuxSwitch(CoordinatorEntity, SwitchEntity):
    def __init__(
        self,
        coordinator: HeliaLuxCoordinator,
        entry_id: str,
        description: HeliaLuxSwitchDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_has_entity_name = True
        self._attr_unique_id = f"{entry_id}_{description.key}_switch"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry_id)},
            "name": "HeliaLux SmartControl",
            "manufacturer": "Juwel",
            "model": "SmartControl",
        }

    @property
    def is_on(self) -> bool:
        return bool(getattr(self.coordinator.data, self.entity_description.key))

    async def async_turn_on(self, **kwargs) -> None:
        await self._set_state(True)

    async def async_turn_off(self, **kwargs) -> None:
        await self._set_state(False)

    async def _set_state(self, enabled: bool) -> None:
        cloud_active = bool(self.coordinator.data.cloud_active)
        time_simulation_active = bool(self.coordinator.data.time_simulation_active)

        if self.entity_description.key == "cloud_active":
            cloud_active = enabled
            if enabled:
                time_simulation_active = False

        if self.entity_description.key == "time_simulation_active":
            time_simulation_active = enabled
            if enabled:
                cloud_active = False

        await self.coordinator.api.set_simulation(
            simulation_time=self.coordinator.data.simulation_time or 0,
            cloud_active=cloud_active,
            time_simulation_active=time_simulation_active,
            target_time=self.coordinator.data.target_time or "01:00",
            cloud_time=self.coordinator.data.cloud_time or "01:00",
            action=self.entity_description.action,
        )
        await self.coordinator.async_request_refresh()