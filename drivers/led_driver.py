"""
Addressable RGB LED (WS2812 / NeoPixel) driver for the Smart Greenhouse Monitor.
"""

from machine import Pin
import neopixel


class StatusLed:
    """
    This driver controls a WS2812 RGB LED to indicate plant status ('mood') using color associations.
    """

    DEFAULT_PIN = 22
    DEFAULT_BRIGHTNESS = 1

    # Colors (R, G, B)
    OFF = (0, 0, 0)
    GREEN = (0, 255, 40)     # Optimal conditions
    ORANGE = (255, 90, 0)    # Dry soil 
    BLUE = (0, 40, 255)      # Overwatered soil or high air humidity
    CYAN = (0, 220, 255)     # Low temperature 
    RED = (255, 0, 0)        # High temperature
    PURPLE = (220, 0, 255)   # Sensor error

    def __init__(self, pin_number=DEFAULT_PIN, num_leds=1, brightness=DEFAULT_BRIGHTNESS):
        """
        Initialize the WS2812 NeoPixel LED on a specified GPIO pin.

        :param pin_number: GPIO pin connected to the DIN pin of the LED. 
        :param num_leds: Number of chained NeoPixel LEDs. 
        :param brightness: Global brightness multiplier from 0.0 to 1.0. 
        """
        if not 0.0 <= brightness <= 1.0:
            raise ValueError("Brightness must be between 0.0 and 1.0.")

        self.num_leds = num_leds
        self.brightness = brightness
        self.led = neopixel.NeoPixel(Pin(pin_number), num_leds)
        self.current_color = self.OFF
        self.off()

    def set_brightness(self, brightness):
        """
        Update the global brightness level and refresh the current color.

        :param brightness: New brightness multiplier from 0.0 to 1.0.
        """
        if not 0.0 <= brightness <= 1.0:
            raise ValueError("Brightness must be between 0.0 and 1.0.")

        self.brightness = brightness
        self.set_color(*self.current_color)

    def set_color(self, r, g, b):
        """
        Set the LED to an RGB color scaled by the current brightness.

        :param r: Red intensity (0 to 255).
        :param g: Green intensity (0 to 255).
        :param b: Blue intensity (0 to 255).
        """
        self.current_color = (r, g, b)
        scaled = (
            int(max(0, min(255, r)) * self.brightness),
            int(max(0, min(255, g)) * self.brightness),
            int(max(0, min(255, b)) * self.brightness),
        )
        for i in range(self.num_leds):
            self.led[i] = scaled
        self.led.write()

    def off(self):
        """Turn the RGB LED completely off."""
        self.set_color(*self.OFF)


def demo():
    """Code to test all mood colors of the StatusLed class."""
    import time

    led = StatusLed(pin_number=22)

    try:
        print("1. Optimal climate (Emerald Green)")
        led.set_color(*StatusLed.GREEN)
        time.sleep(2)

        print("2. Dry soil (Orange)")
        led.set_color(*StatusLed.ORANGE)
        time.sleep(2)

        print("3. Overwatered / High air humidity (Deep Blue)")
        led.set_color(*StatusLed.BLUE)
        time.sleep(2)

        print("4. Cold temperature (Ice Cyan)")
        led.set_color(*StatusLed.CYAN)
        time.sleep(2)

        print("5. Overheating (Red)")
        led.set_color(*StatusLed.RED)
        time.sleep(2)

        print("6. Sensor error (Purple)")
        led.set_color(*StatusLed.PURPLE)
        time.sleep(2)

    finally:
        print("Turning LED off.")
        led.off()


if __name__ == "__main__":
    demo()