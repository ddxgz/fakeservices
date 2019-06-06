# This module is to emulate the environment data from a sense hat during
# development
# %%
import numpy as np


class SenseHat:
    def get_humidity(self) -> float:
        """The percentage of relative humidity. Humidity: %%rH """
        return np.random.normal(40, 5)

    def get_temperature(self) -> float:
        """The current temperature in degrees Celsius. Gets the current 
        temperature in degrees Celsius from the humidity sensor."""
        return np.random.normal(20, 2)

    def get_pressure(self) -> float:
        """The current pressure in Millibars."""
        return np.random.normal(1015, 2)


if __name__ == '__main__':
    sh = SenseHat()
    print(sh.get_humidity())
    print(sh.get_temperature())
    print(sh.get_pressure())
