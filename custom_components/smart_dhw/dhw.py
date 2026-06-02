import numpy as np

WATER_HEAT_CAPACITY = 1.163  # Wh per liter per °C


def energy_from_delta(volume_l, delta_t):
    return volume_l * abs(delta_t) * WATER_HEAT_CAPACITY / 1000


def soc(temp, t_min, t_max):
    return max(0.0, min(1.0, (temp - t_min) / (t_max - t_min)))


def estimate_draw_events(temp_series):
    """
    Sehr einfache Ereigniserkennung:
    große negative Sprünge = Entnahme
    """
    events = []
    for i in range(1, len(temp_series)):
        delta = temp_series[i] - temp_series[i - 1]
        if delta < -0.8:
            events.append(abs(delta))
    return events


def rolling_consumption(events):
    if not events:
        return 0
    return sum(events)