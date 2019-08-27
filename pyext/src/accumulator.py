import numpy as np


class SampleAccumulator(object):
    def __init__(self, keys):
        self.keys = keys
        self.values = []

    def add_sample(self, values):
        self.values.append(values)

    def get_samples(self, key=None):
        if key is None:
            return dict(zip(self.keys, map(np.array, zip(*self.values))))
        i = self.keys.index(key)
        return np.array([vals[i] for vals in self.values])

    def clear(self):
        self.values.clear()


class StatisticsAccumulator(SampleAccumulator):
    def __init__(self, keys):
        super().__init__(keys)
        self.means = np.zeros(len(keys), dtype=np.double)
        self.current = {}

    def add_sample(self, stats):
        values = list(stats.values())
        super().add_sample(values)
        self.means += (np.asarray(values, dtype=np.double) - self.means) / len(
            self.values
        )
        self.current = dict(zip(self.keys, values))

    def get_mean_stats(self):
        return dict(zip(self.keys, self.means))

    def clear(self):
        super().clear()
        self.means = np.zeros_like(self.means)
        self.current = {}

    def log_current(self, prefix="     "):
        print(
            "\n".join(
                [
                    "{0}{1}: {2}".format(prefix, k, v)
                    for k, v in self.current.items()
                ]
            )
        )

    def log_mean(self, prefix="     "):
        print(
            "\n".join(
                [
                    "{0}{1}: {2}".format(prefix, k, v)
                    for k, v in zip(self.keys, self.means)
                ]
            )
        )
