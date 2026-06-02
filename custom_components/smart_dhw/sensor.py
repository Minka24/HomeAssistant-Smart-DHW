from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.const import UnitOfTemperature

from .const import DOMAIN
from .coordinator import DHWCoordinator


async def async_setup_entry(hass, entry, async_add_entities):
    import logging
    _LOGGER = logging.getLogger(__name__)
    
    try:
        _LOGGER.debug(f"Setting up sensor platform with config: {entry.data}")
        coordinator = DHWCoordinator(hass, entry.data)
        _LOGGER.debug("Coordinator created, refreshing...")
        await coordinator.async_config_entry_first_refresh()
        _LOGGER.debug(f"Coordinator refreshed, data: {coordinator.data}")
        hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

        async_add_entities([
            DHWRequiredTempSensor(coordinator),
        ], True)
        _LOGGER.debug("Sensor entity added")
    except Exception as err:
        _LOGGER.error(f"Error setting up sensor: {err}", exc_info=True)
        raise


class DHWRequiredTempSensor(SensorEntity):

    def __init__(self, coordinator):
        self.coordinator = coordinator
        self._attr_name = "DHW Required Charge Temperature"
        self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        self._attr_device_class = SensorDeviceClass.TEMPERATURE

    @property
    def native_value(self):
        value = self.coordinator.data.get("required_temp")
        return round(value, 1) if value is not None else None

    @property
    def available(self):
        return self.coordinator.last_update_success

    async def async_update(self):
        await self.coordinator.async_request_refresh()
