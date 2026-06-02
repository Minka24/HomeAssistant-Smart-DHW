import importlib

from homeassistant.core import HomeAssistant
from .const import DOMAIN

async def async_setup(hass: HomeAssistant, config: dict):
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass, entry):
    hass.data[DOMAIN][entry.entry_id] = entry.data
    await hass.async_add_executor_job(
        importlib.import_module,
        "custom_components.smart_dhw.sensor",
    )
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True