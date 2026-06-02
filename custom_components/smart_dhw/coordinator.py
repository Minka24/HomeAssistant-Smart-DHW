from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

from .const import CONF_STATUS_SENSOR, CONF_TEMP_SENSOR
from .dhw import WATER_HEAT_CAPACITY, energy_from_delta


class DHWCoordinator(DataUpdateCoordinator):

    def __init__(self, hass, config):
        self.hass = hass
        self.config = config

        super().__init__(
            hass,
            logger=None,
            name="smart_dhw",
            update_interval=None,
        )

    async def _async_update_data(self):
        temp_entity = self.config[CONF_TEMP_SENSOR]
        status_entity = self.config[CONF_STATUS_SENSOR]

        history = await self.hass.services.async_call(
            "recorder",
            "get_history",
            {
                "entity_id": [temp_entity, status_entity],
                "minimal_response": True,
                "end_time": dt_util.now(),
                "limit": 1000,
            },
            blocking=True,
            return_response=True,
        )

        temp_states = self._states_for_entity(history, temp_entity)
        status_states = self._states_for_entity(history, status_entity)

        current_temp = self._last_temp(temp_states)
        if current_temp is None or len(status_states) < 2:
            return self._empty()

        hc_times = self._hc_event_times(status_states)
        if len(hc_times) < 2:
            return {"required_temp": round(current_temp)}

        energy_since_last = self._energy_since(temp_states, hc_times[-1])
        predicted_interval = self._predict_interval_kwh(temp_states, hc_times)

        required_temp = self._required_charge_temp(
            current_temp,
            predicted_interval,
            energy_since_last,
            self.config["volume_l"],
            self.config["min_temp"],
            self.config["max_temp"],
        )

        return {"required_temp": required_temp}

    # -----------------------------
    # Helpers
    # -----------------------------

    def _states_for_entity(self, history, entity_id):
        if isinstance(history, dict):
            return list(history.get(entity_id, []))
        try:
            return list(history.values())[0]
        except Exception:
            return []

    def _parse_timestamp(self, state):
        timestamp = state.get("last_updated") or state.get("last_changed")
        if not timestamp:
            return None
        return dt_util.parse_datetime(timestamp)

    def _last_temp(self, states):
        for state in reversed(states):
            try:
                return float(state["state"])
            except Exception:
                continue
        return None

    def _hc_event_times(self, states):
        times = []
        previous = None
        for state in states:
            current = state.get("state")
            timestamp = self._parse_timestamp(state)
            if timestamp is None:
                continue
            if current == "HC" and previous != "HC":
                times.append(timestamp)
            previous = current
        return times

    def _energy_since(self, temp_states, start_time):
        temp_points = self._temperature_points(temp_states)
        filtered = [point for point in temp_points if point[0] >= start_time]
        return self._energy_of_draws(filtered)

    def _predict_interval_kwh(self, temp_states, hc_times):
        intervals = []
        for start, end in zip(hc_times, hc_times[1:]):
            intervals.append(self._energy_between(temp_states, start, end))
        if not intervals:
            return 0.0
        intervals.sort()
        return intervals[len(intervals) // 2]

    def _energy_between(self, temp_states, start, end):
        temp_points = self._temperature_points(temp_states)
        filtered = [point for point in temp_points if start <= point[0] < end]
        return self._energy_of_draws(filtered)

    def _temperature_points(self, states):
        points = []
        for state in states:
            timestamp = self._parse_timestamp(state)
            if timestamp is None:
                continue
            try:
                temp = float(state["state"])
            except Exception:
                continue
            points.append((timestamp, temp))
        return points

    def _energy_of_draws(self, temp_points):
        energy = 0.0
        for previous, current in zip(temp_points, temp_points[1:]):
            delta = current[1] - previous[1]
            if delta < -0.1:
                energy += energy_from_delta(self.config["volume_l"], abs(delta))
        return energy

    def _required_charge_temp(self, current_temp, predicted_kwh, energy_since_last, volume_l, min_temp, max_temp):
        remaining_kwh = predicted_kwh - energy_since_last
        if remaining_kwh <= 0:
            return max(round(current_temp), min_temp)

        delta_t = remaining_kwh * 1000 / (volume_l * WATER_HEAT_CAPACITY)
        target_temp = current_temp + delta_t
        if target_temp > max_temp:
            target_temp = max_temp
        return min(max(round(target_temp), min_temp), max_temp)

    def _empty(self):
        return {"required_temp": None}