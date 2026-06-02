import statistics
from collections import defaultdict


class DHWForecast:

    def __init__(self):
        # weekday -> list of kWh consumption
        self.weekday_profile = defaultdict(list)

    def add_sample(self, weekday, kwh):
        self.weekday_profile[weekday].append(kwh)

    def weekday_factor(self, weekday):
        values = self.weekday_profile.get(weekday, [])
        if not values:
            return 1.0

        return statistics.median(values) / self.global_median()

    def global_median(self):
        all_values = [
            v for vals in self.weekday_profile.values()
            for v in vals
        ]
        if not all_values:
            return 1.0
        return statistics.median(all_values)

    def predict(self, base_kwh, weekday):
        factor = self.weekday_factor(weekday)
        return base_kwh * factor