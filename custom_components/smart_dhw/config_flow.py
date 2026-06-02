from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries

from .const import DOMAIN, CONF_TEMP_SENSOR, CONF_STATUS_SENSOR, CONF_MIN_TEMP, CONF_MAX_TEMP

CONF_VOLUME_L = "volume_l"


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(
                title="Smart DHW",
                data=user_input,
            )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_TEMP_SENSOR): vol.All(str),
                vol.Required(CONF_STATUS_SENSOR): vol.All(str),
                vol.Optional(CONF_VOLUME_L, default=200.0): vol.Coerce(float),
                vol.Optional(CONF_MIN_TEMP, default=40.0): vol.Coerce(float),
                vol.Optional(CONF_MAX_TEMP, default=60.0): vol.Coerce(float),
            }
        )

        return self.async_show_form(step_id="user", data_schema=data_schema)
