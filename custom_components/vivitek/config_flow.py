# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2024-2026 Schuberg Philis / Lab271
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME
from .const import DOMAIN

class VivitekConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Vivitek Projector."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_HOST, default="192.0.2.10"): str,
                vol.Required(CONF_NAME, default="Projector 1"): str,
            })
        )


