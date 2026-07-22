# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2024-2026 Schuberg Philis / Lab271
from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import INPUT_SOURCES
from .entity import build_device_info

# Reverse map: source name -> numeric code for "op input.sel = <code>".
SOURCE_CODES = {name: code for code, name in INPUT_SOURCES.items()}


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities):
    """Set up the Vivitek input source select from a config entry."""
    data = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([VivitekInputSelect(data)])


class VivitekInputSelect(CoordinatorEntity, SelectEntity):
    """Selects the projector's active input source."""

    _attr_has_entity_name = True
    _attr_name = "Input"
    _attr_icon = "mdi:import"
    _attr_options = list(INPUT_SOURCES.values())

    def __init__(self, data):
        """Initialize the select."""
        super().__init__(data["coordinator"])
        self._attr_unique_id = f"{data['host']}_input"
        self._attr_device_info = build_device_info(data)

    @property
    def current_option(self):
        """Return the currently selected source, or None if unknown."""
        return self.coordinator.data.get("input")

    async def async_select_option(self, option):
        """Switch the projector to the chosen input source."""
        code = SOURCE_CODES[option]
        await self.hass.async_add_executor_job(
            self.coordinator.send_command, f"op input.sel = {code}"
        )
        await self.coordinator.async_request_refresh()
