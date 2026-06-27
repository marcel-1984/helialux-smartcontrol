"""Data coordinator for HeliaLux SmartControl."""

from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .api import HeliaLuxApi
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class HeliaLuxCoordinator(DataUpdateCoordinator):
    """HeliaLux coordinator."""

    def __init__(self, hass: HomeAssistant, host: str) -> None:
        """Initialize coordinator."""
        self.api = HeliaLuxApi(async_get_clientsession(hass), host)

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=10),
        )

    async def _async_update_data(self):
        """Fetch data from HeliaLux."""
        return await self.api.get_status()