"""
Soil moisture sensor driver for the Smart Greenhouse Monitor.
"""

from machine import ADC, Pin
from adc_read import read_adc


class MoistureSensor:
    """
    This driver provides calibrated soil moisture readings from an analog sensor.
    """

    DEFAULT_PIN = 28
    DRY_VALUE = 52000   # Raw 16-bit ADC value in dry air (0%)
    WET_VALUE = 24000   # Raw 16-bit ADC value in water (100%)

    def __init__(self, adc_pin=DEFAULT_PIN, dry_value=DRY_VALUE, wet_value=WET_VALUE):
        """
        Initialize the soil moisture sensor on an ADC-capable GPIO pin.

        :param adc_pin: GPIO pin number with ADC capability.
        :param dry_value: Raw 16-bit ADC value measured in dry air (0% moisture).
        :param wet_value: Raw 16-bit ADC value measured in water (100% moisture).
        """
        if adc_pin not in (26, 27, 28):
            raise ValueError("Invalid ADC pin. Use GP26, GP27, or GP28.")
        if dry_value == wet_value:
            raise ValueError("dry_value and wet_value must not be equal.")

        self.adc = ADC(Pin(adc_pin))
        self.dry_value = dry_value
        self.wet_value = wet_value

    def read_soil(self, samples=10):
        """
        Calculate calibrated soil moisture as a percentage (0% = dry, 100% = wet).

        :param samples: Number of consecutive ADC samples to average.
        :return: Soil moisture percentage rounded to one decimal place.
        """
        raw, _ = read_adc(self.adc, samples=samples)
        percent = (self.dry_value - raw) * 100.0 / (self.dry_value - self.wet_value)
        percent = max(0.0, min(100.0, percent))
        return round(percent, 1)


def demo():
    """Code to test and calibrate the MoistureSensor class."""
    import time

    sensor = MoistureSensor()
    print("Reading soil moisture sensor; press Ctrl+C to stop.")

    try:
        while True:
            raw, voltage = read_adc(sensor.adc, samples=10)
            moisture = sensor.read_soil(samples=10)
            print(
                f"raw: {raw:5d}   "
                f"voltage: {voltage:.3f} V   "
                f"moisture: {moisture:5.1f} %"
            )
            time.sleep_ms(200)

    except KeyboardInterrupt:
        print("\nProgram stopped. Exiting...")


if __name__ == "__main__":
    demo()