"""
Rotary encoder driver (KY-040) for the Smart Greenhouse Monitor.
"""

from machine import Pin
from gpio_devices import Button
import time


class RotaryEncoder:
    """
    This driver handles rotation steps and debounced push-button presses of a KY-040 rotary encoder.
    """

    DEFAULT_CLK_PIN = 13
    DEFAULT_DT_PIN = 14
    DEFAULT_SW_PIN = 15

    def __init__(
        self,
        clk_pin=DEFAULT_CLK_PIN,
        dt_pin=DEFAULT_DT_PIN,
        sw_pin=DEFAULT_SW_PIN,
        rot_debounce_ms=5,
    ):
        """
        Initialize the rotary encoder GPIO pins, push button, and rotation interrupt.

        :param clk_pin: GPIO pin number connected to encoder CLK. Defaults to 13.
        :param dt_pin: GPIO pin number connected to encoder DT. Defaults to 14.
        :param sw_pin: GPIO pin number connected to encoder SW. Defaults to 15.
        :param rot_debounce_ms: Minimum interval in ms between valid rotation steps. Defaults to 5.
        """
        self.clk = Pin(clk_pin, Pin.IN, Pin.PULL_UP)
        self.dt = Pin(dt_pin, Pin.IN, Pin.PULL_UP)
        self.sw = Button(sw_pin)

        self.rot_debounce_ms = rot_debounce_ms
        self._delta = 0
        self._last_rot_ms = 0

        self.clk.irq(trigger=Pin.IRQ_FALLING, handler=self._on_rotate)

    def _on_rotate(self, pin):
        """Hardware interrupt handler recording rotation direction and step count."""
        now = time.ticks_ms()
        if time.ticks_diff(now, self._last_rot_ms) < self.rot_debounce_ms:
            return
        self._last_rot_ms = now

        if self.dt.value() != self.clk.value():
            self._delta += 1
        else:
            self._delta -= 1

    def get_delta(self):
        """
        Return accumulated rotation steps since the last call and reset the counter.

        :return: Signed integer step count (+ clockwise, - counter-clockwise).
        """
        steps = self._delta
        self._delta = 0
        return steps

    def was_pressed(self, debounce_ms=20):
        """
        Detect a single debounced press of the encoder push button.

        :param debounce_ms: Debounce interval in milliseconds. Defaults to 20.
        :return: True once when a stable button press occurs, False otherwise.
        """
        return self.sw.was_pressed(debounce_ms=debounce_ms)


def demo():
    """Code designed to test rotation and button press of the RotaryEncoder class."""
    encoder = RotaryEncoder()
    step_total = 0

    print("Rotate encoder or press button; press Ctrl+C to stop.")

    try:
        while True:
            if encoder.was_pressed():
                print("Button pressed!")

            delta = encoder.get_delta()
            if delta != 0:
                step_total += delta
                print(f"Delta: {delta:+d}   Total: {step_total}")

            time.sleep_ms(20)

    except KeyboardInterrupt:
        print("\nProgram stopped. Exiting...")


if __name__ == "__main__":
    demo()