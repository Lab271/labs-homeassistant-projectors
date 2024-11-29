import logging
from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from .const import DOMAIN
import socket

_LOGGER = logging.getLogger(__name__)
DEFAULT_PORT = 7000

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities):
    """Set up Vivitek switch from a config entry."""
    host = config_entry.data["host"]
    name = config_entry.data["name"]
    async_add_entities([VivitekSwitch(name, host)])


class VivitekSwitch(SwitchEntity):
    """Representation of a Vivitek projector switch."""

    def __init__(self, name, host):
        """Initialize the switch."""
        self._device_name = name
        self._host = host
        self._name = f'{name}_power'
        self._is_on = False
        self._attr_unique_id = f"{host}_light"


    @property
    def name(self):
        """Return the name of the switch."""
        return self._name


    @property
    def is_on(self):
        """Return true if the switch is on."""
        return self._is_on

    @property
    def device_info(self):
        """Return device information for this projector."""
        return {
            "identifiers": {(DOMAIN, self._host)},
            "name": self._device_name,
            "manufacturer": "Vivitek",
            "model": "D4000Z",
            "sw_version": '1'

        }



    async def async_turn_on(self, **kwargs):
        """Turn the projector on."""
        response = await self.hass.async_add_executor_job(self._send_command, 'op power.on')
        if response:
            self._is_on = True
            self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        """Turn the projector off."""
        response = await self.hass.async_add_executor_job(self._send_command, 'op power.off')
        if response:
            self._is_on = False
            self.async_write_ha_state()

    async def async_update(self):
        """Fetch the projector's status."""
        response = await self.hass.async_add_executor_job(self._send_command, 'op status ?')
        if response and response.strip()[-1] == '2':  # Adjust based on actual response format
            self._is_on = True
        else:
            self._is_on = False
        self.async_write_ha_state()

    def _send_command(self, command):
        """Send a command to the projector."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5)  # Timeout for socket
                s.connect((self._host, DEFAULT_PORT))
                s.sendall((command + '\r').encode())
                _LOGGER.info("Sent command '%s' to projector '%s'", command, self._name)
                response = s.recv(1024)
                return response.decode().strip()
        except Exception as e:
            _LOGGER.error("Error communicating with projector '%s': %s", self._name, e)
        return None
