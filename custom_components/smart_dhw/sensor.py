from homeassistant.components.sensor import SensorEntity
from homeassistant.const import TEMP_CELSIUS

from .const import DOMAIN
from .coordinator import DHWCoordinator


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = DHWCoordinator(hass, entry.data)
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    async_add_entities([
        DHWRequiredTempSensor(coordinator),
    ], True)


class DHWRequiredTempSensor(SensorEntity):

    def __init__(self, coordinator):
        self.coordinator = coordinator
        self._attr_name = "DHW Required Charge Temperature"
        self._attr_native_unit_of_measurement = TEMP_CELSIUS
        self._attr_device_class = "temperature"

    @property
    def native_value(self):
        value = self.coordinator.data.get("required_temp")
        return round(value, 1) if value is not None else None

    @property
    def available(self):
        return self.coordinator.last_update_success

    async def async_update(self):
        await self.coordinator.async_request_refresh()
