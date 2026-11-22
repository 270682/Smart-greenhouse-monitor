"""
Relay module driver for the Smart Greenhouse Monitor.
"""

from machine import Pin


class Relay:
    """
    This driver controls a relay module (for switching a 5V DC fan).
    """

    DEFAULT_PIN = 16

    def __init__(self, pin_number=DEFAULT_PIN):
        """
        Initialize the relay on a specific GPIO pin in the OFF state.

        :param pin_number: GPIO pin number connected to the relay IN pin.
        """
        self.pin = Pin(pin_number, Pin.OUT)
        self._state = False
        self.off()

    def set_state(self, state):
        """
        Set the relay state.

        :param state: True to turn on the relay, False to turn it off.
        """
        self._state = bool(state)
        self.pin.value(int(self._state))

    def on(self):
        """Turn the relay on (pin value 1)."""
        self.set_state(True)

    def off(self):
        """Turn the relay off (pin value 0)."""
        self.set_state(False)

    def toggle(self):
        """Toggle the current relay state between on and off."""
        self.set_state(not self._state)

    def is_on(self):
        """
        Check whether the relay is currently energized.

        :return: True if the relay is ON, False if the relay is OFF.
        """
        return self._state


def demo():
    """Code designed to test all functions of the Relay class."""
    import time

    relay = Relay(pin_number=16)

    try:
        while True:
            relay.on()
            print("Relay ON")
            time.sleep(0.2)

            relay.off()
            print("Relay OFF")
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nProgram stopped. Exiting...")
        relay.off()


if __name__ == "__main__":
    demo()