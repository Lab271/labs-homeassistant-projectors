"""Shared polling coordinator for a Vivitek projector.

The projector speaks a simple ASCII "op" protocol over TCP and only accepts
one connection at a time, so all entities share a single coordinator that
queries every value once per update cycle. Each query uses its own short-lived
connection because the projector closes the socket after replying.

Command set verified against a DU4371Z-ST (laser) on firmware V02:
    op status ?       -> "OP STATUS = 0"      (0 = off, non-zero = on/warming/cooling)
    op source.info ?  -> "OP SOURCE.INFO = 1920  x  1200  @  59.94 Hz"
    op light.mode ?   -> "OP LIGHT.MODE = 0"
    op model ?        -> "OP MODEL = DU4371Z-ST"
    op sw.ver ?       -> "OP SW.VER = DU4371Z-ST V02"
In standby only power/model-type queries answer; signal queries time out, so a
timed-out individual query is recorded as None rather than failing the poll.
"""
import logging
import socket
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

_LOGGER = logging.getLogger(__name__)

DEFAULT_PORT = 7000
SOCKET_TIMEOUT = 6
UPDATE_INTERVAL = timedelta(seconds=30)

ILLEGAL = "*Illegal format#"
# Values the projector reports when a reading is not yet available.
UNAVAILABLE_VALUES = {"", "NA"}

# Query commands -> key used in the coordinator's data dict.
# "op proj.runtime ?" is the only usage-hours counter this firmware exposes
# (lamp1.hours / light.hour etc. all return *Illegal format# on the DU4371Z-ST).
QUERIES = {
    "power": "op status ?",
    "source_info": "op source.info ?",
    "light_mode": "op light.mode ?",
    "runtime_hours": "op proj.runtime ?",
    "input": "op input.sel ?",
}

# Input source codes reported/accepted by "op input.sel" (verified against the
# DU4371Z-ST; matches the DU7195Z laser communication manual).
INPUT_SOURCES = {
    1: "VGA1",
    6: "HDMI 1",
    9: "HDMI 2",
    15: "HDBaseT",
}


class VivitekCoordinator(DataUpdateCoordinator):
    """Polls a single Vivitek projector and shares the result with all entities."""

    def __init__(self, hass: HomeAssistant, host: str):
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"vivitek {host}",
            update_interval=UPDATE_INTERVAL,
        )
        self._host = host

    async def _async_update_data(self):
        """Fetch all projector values."""
        return await self.hass.async_add_executor_job(self._poll)

    def _poll(self):
        """Run every query. Runs in the executor.

        The 'power' query is the reachability probe: if it fails, the whole
        poll fails and every entity goes unavailable. Other queries are allowed
        to fail individually (they time out when the projector is in standby)
        and are recorded as None.
        """
        power_raw = self._send_command(QUERIES["power"])
        if power_raw is None:
            raise UpdateFailed(f"No response from projector at {self._host}")

        data = {"power": self._parse("power", power_raw)}
        for key, command in QUERIES.items():
            if key == "power":
                continue
            data[key] = self._parse(key, self._send_command(command))
        return data

    @staticmethod
    def _parse(key, raw):
        """Turn a raw ASCII reply into a usable value.

        Replies look like "OP STATUS = 2" or "OP SOURCE.INFO = 1920 x 1200 ...".
        During power transitions the projector may return "NA" (not yet
        available), the padded "*Illegal format#", or a stray framing byte with
        no "=" — all of which become None here.
        """
        if not raw or raw == ILLEGAL or "=" not in raw:
            return None
        value = raw.split("=", 1)[-1].strip()
        if value in UNAVAILABLE_VALUES:
            return None
        if key == "power":
            # Observed states: 0 = off/standby; 2 = on; 4/5 = warming.
            # Any non-zero numeric state means the projector is powered on.
            return value.isdigit() and value != "0"
        if key in ("light_mode", "runtime_hours"):
            try:
                return int(value)
            except ValueError:
                return None
        if key == "input":
            # Map the numeric code to a source name; unknown codes -> None.
            try:
                return INPUT_SOURCES.get(int(value))
            except ValueError:
                return None
        if key == "source_info":
            # Collapse the projector's padded spacing: "1920  x  1200  @  59.94 Hz".
            return " ".join(value.split())
        return value

    def async_read_device_info(self):
        """Read model and firmware once. Best-effort; runs in the executor."""
        model = self._parse("model", self._send_command("op model ?"))
        sw_version = self._parse("sw_version", self._send_command("op sw.ver ?"))
        return {"model": model, "sw_version": sw_version}

    def send_command(self, command):
        """Send a one-off command (e.g. power on/off). Runs in the executor."""
        return self._send_command(command)

    def _send_command(self, command):
        """Send one command over its own connection and return the reply text."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(SOCKET_TIMEOUT)
                s.connect((self._host, DEFAULT_PORT))
                s.sendall((command + "\r").encode())
                return s.recv(1024).decode(errors="ignore").strip()
        except Exception as err:  # noqa: BLE001 - caller decides whether this is fatal
            _LOGGER.debug("Error sending '%s' to projector at %s: %s", command, self._host, err)
            return None
