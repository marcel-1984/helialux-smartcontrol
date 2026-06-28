"""HeliaLux SmartControl integration."""

from __future__ import annotations

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant, ServiceCall
import homeassistant.helpers.config_validation as cv

from .api import HeliaLuxProgram
from .const import DOMAIN
from .coordinator import HeliaLuxCoordinator

PLATFORMS = ["sensor", "light", "number", "switch", "button", "time"]


SAVE_PROGRAM_SCHEMA = vol.Schema(
    {
        vol.Required("name"): cv.string,
        vol.Required("times"): [cv.positive_int],
        vol.Required("white"): [cv.positive_int],
        vol.Required("blue"): [cv.positive_int],
        vol.Required("green"): [cv.positive_int],
        vol.Required("red"): [cv.positive_int],
        vol.Required("cloud_intensity"): [cv.positive_int],
        vol.Required("cloud_motion"): [cv.positive_int],
    }
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up HeliaLux SmartControl from a config entry."""
    coordinator = HeliaLuxCoordinator(hass, entry.data[CONF_HOST])

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    async def async_save_program(call: ServiceCall) -> None:
        """Upload a full HeliaLux lighting program."""
        program = HeliaLuxProgram(
            name=call.data["name"],
            times=call.data["times"],
            white=call.data["white"],
            blue=call.data["blue"],
            green=call.data["green"],
            red=call.data["red"],
            cloud_intensity=call.data["cloud_intensity"],
            cloud_motion=call.data["cloud_motion"],
        )

        await coordinator.api.save_program(program)
        await coordinator.async_request_refresh()

    hass.services.async_register(
        DOMAIN,
        "save_program",
        async_save_program,
        schema=SAVE_PROGRAM_SCHEMA,
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload HeliaLux SmartControl."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok