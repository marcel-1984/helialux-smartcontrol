"""Config flow for HeliaLux SmartControl."""

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import HeliaLuxApi, HeliaLuxApiError
from .const import DEFAULT_NAME, DOMAIN


class HeliaLuxConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for HeliaLux SmartControl."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle manual setup."""
        errors = {}

        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            name = user_input.get(CONF_NAME, DEFAULT_NAME)

            await self.async_set_unique_id(host)
            self._abort_if_unique_id_configured()

            api = HeliaLuxApi(async_get_clientsession(self.hass), host)

            try:
                await api.get_status()
            except HeliaLuxApiError:
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(
                    title=name,
                    data={
                        CONF_HOST: host,
                        CONF_NAME: name,
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST, default="192.168.178.250"): str,
                    vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
                }
            ),
            errors=errors,
        )