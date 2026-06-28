"""API client for Juwel HeliaLux SmartControl."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import aiohttp


class HeliaLuxApiError(Exception):
    """HeliaLux communication error."""


@dataclass
class HeliaLuxStatus:
    white: int | None
    blue: int | None
    green: int | None
    red: int | None
    controller_time: str | None
    simulation_time: int | None
    cloud_active: bool | None
    time_simulation_active: bool | None
    target_time: str | None
    cloud_time: str | None


@dataclass
class HeliaLuxProgram:
    name: str
    times: list[int]
    white: list[int]
    blue: list[int]
    green: list[int]
    red: list[int]
    cloud_intensity: list[int]
    cloud_motion: list[int]


class HeliaLuxApi:
    """Small async API client for HeliaLux SmartControl."""

    def __init__(self, session: aiohttp.ClientSession, host: str) -> None:
        self._session = session
        self._host = host.replace("http://", "").replace("https://", "").rstrip("/")
        self._base_url = f"http://{self._host}"

    async def _post(self, endpoint: str, data: dict[str, Any]) -> dict[str, Any]:
        url = f"{self._base_url}/{endpoint}"

        try:
            async with self._session.post(url, data=data, timeout=5) as response:
                response.raise_for_status()
                return await response.json(content_type=None)
        except Exception as err:
            raise HeliaLuxApiError(f"Error communicating with HeliaLux: {err}") from err

    async def _post_no_json(self, endpoint: str, data: dict[str, Any]) -> str:
        url = f"{self._base_url}/{endpoint}"

        try:
            async with self._session.post(url, data=data, timeout=5) as response:
                response.raise_for_status()
                return await response.text()
        except Exception as err:
            raise HeliaLuxApiError(f"Error communicating with HeliaLux: {err}") from err

    async def get_status(self) -> HeliaLuxStatus:
        """Get live HeliaLux status."""
        data = await self._post("stat", {"action": "10"})

        status = data.get("S", {})
        channels = data.get("C", {}).get("ch", [])

        return HeliaLuxStatus(
            white=_channel(channels, 0),
            blue=_channel(channels, 1),
            green=_channel(channels, 2),
            red=_channel(channels, 3),
            controller_time=status.get("dtime"),
            simulation_time=status.get("stime"),
            cloud_active=_to_bool(status.get("cswi")),
            time_simulation_active=_to_bool(status.get("tswi")),
            target_time=status.get("ttime"),
            cloud_time=status.get("ctime"),
        )

    async def set_colors(self, white: int, blue: int, green: int, red: int) -> None:
        """Set live color channels."""
        await self._post(
            "color",
            {
                "action": "1",
                "ch1": _clamp(white),
                "ch2": _clamp(blue),
                "ch3": _clamp(green),
                "ch4": _clamp(red),
            },
        )

    async def set_simulation(
        self,
        simulation_time: int,
        cloud_active: bool,
        time_simulation_active: bool,
        target_time: str,
        cloud_time: str,
        action: int,
    ) -> None:
        """Set simulation options."""
        await self._post(
            "stat",
            {
                "action": str(action),
                "ch5": str(simulation_time),
                "tswi": "true" if time_simulation_active else "false",
                "ttime": target_time,
                "cswi": "true" if cloud_active else "false",
                "ctime": cloud_time,
            },
        )

    async def save_program(self, program: HeliaLuxProgram) -> None:
        """Upload a full HeliaLux lighting program."""
        await self._post_no_json(
            "pedit",
            {
                "action": "30",
                "PNAME": program.name,
                "TIMES": _array(program.times),
                "CH1": _array(program.white),
                "CH2": _array(program.blue),
                "CH3": _array(program.green),
                "CH4": _array(program.red),
                "CINT": _array(program.cloud_intensity),
                "CMOT": _array(program.cloud_motion),
            },
        )


def _channel(channels: list[Any], index: int) -> int | None:
    try:
        return int(channels[index])
    except (IndexError, TypeError, ValueError):
        return None


def _clamp(value: int) -> int:
    return max(0, min(100, int(value)))


def _array(values: list[int]) -> str:
    return "[" + ",".join(str(int(value)) for value in values) + "]"


def _to_bool(value: Any) -> bool | None:
    if value in (True, "true", "1", 1, "checked", "on"):
        return True
    if value in (False, "false", "0", 0, "", None):
        return False
    return None