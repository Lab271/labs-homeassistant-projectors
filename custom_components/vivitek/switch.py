# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2024-2026 Schuberg Philis / Lab271
from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .entity import build_device_info


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities):
    """Set up Vivitek switch from a config entry."""
    data = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([VivitekSwitch(data)])


class VivitekSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of a Vivitek projector power switch."""

    _attr_has_entity_name = True
    _attr_name = "Power"

    def __init__(self, data):
        """Initialize the switch."""
        super().__init__(data["coordinator"])
        self._attr_unique_id = f"{data['host']}_power"
        self._attr_device_info = build_device_info(data)

    @property
    def is_on(self):
        """Return true if the projector is on."""
        return bool(self.coordinator.data.get("power"))

    async def async_turn_on(self, **kwargs):
        """Turn the projector on."""
        await self.hass.async_add_executor_job(self.coordinator.send_command, "op power.on")
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        """Turn the projector off."""
        await self.hass.async_add_executor_job(self.coordinator.send_command, "op power.off")
        await self.coordinator.async_request_refresh()
