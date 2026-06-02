from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector

from .const import DOMAIN, CONF_MIN_TEMP, CONF_MAX_TEMP

CONF_VOLUME_L = "volume_l"


class SmartDHWConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(
                title="Smart DHW",
                data=user_input,
            )

        data_schema = vol.Schema(
            {
                vol.Required("temp_sensor"): selector.EntitySelector(
                    selector={"domain": "sensor"}
                ),
                vol.Required("status_sensor"): selector.EntitySelector(
                    selector={"domain": "sensor"}
                ),
                vol.Optional(CONF_VOLUME_L, default=200.0): vol.Coerce(float),
                vol.Optional(CONF_MIN_TEMP, default=40.0): vol.Coerce(float),
                vol.Optional(CONF_MAX_TEMP, default=60.0): vol.Coerce(float),
            }
        )

        return self.async_show_form(step_id="user", data_schema=data_schema)
