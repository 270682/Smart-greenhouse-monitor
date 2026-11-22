"""
OLED display driver for the Smart Greenhouse Monitor. Inherits from SH1106_I2C.
"""

from sh1106 import SH1106_I2C


class oled_driver(SH1106_I2C):
    """
    This driver provides functions for displaying live measured data and for displaying the settings of desired setpoints.
    """

    def __init__(self, i2c, width=128, height=64, addr=0x3C):
        """
        Initialize the SH1106 OLED display over I2C.

        :param i2c: Initialized machine.I2C object (e.g. I2C(0) on GP4/GP5).
        :param width: Display width in pixels. Defaults to 128.
        :param height: Display height in pixels. Defaults to 64.
        :param addr: I2C address of the OLED controller. Defaults to 0x3C.
        """
        super().__init__(i2c, width=width, height=height, addr=addr)
        self.width = width
        self.height = height
        self.is_on = True
        self.power_on()
        self.fill(0)
        self.show()

    def power_on(self):
        """Turn on the OLED display and update internal state."""
        self.is_on = True
        super().poweron()

    def power_off(self):
        """Turn off the OLED display and update internal state."""
        self.is_on = False
        super().poweroff()

    def toggle_power(self):
        """
        Toggle display power state on/off.

        :return: New power state of the display (bool).
        """
        if self.is_on:
            self.power_off()
        else:
            self.power_on()
        return self.is_on

    def show_boot_screen(self):
        """Display the startup screen using the inherited show_logo() method."""
        if not self.is_on:
            return
        self.fill(0)
        self.show_logo(
            logo_x=0,
            logo_y=16,
            text_x=36,
            text_y=17,
            line1="Smart",
            line2="Greenhouse",
            line3="VUT Brno",
        )

    def draw_bar(self, x, y, width, value, minimum=0, maximum=100, height=6):
        """
        Draw a horizontal progress bar scaled between minimum and maximum.

        Taken from laboratory exercises:
        https://gitlab.fekt.vut.cz/fryza/micropython-course-labs

        :param x: Left X coordinate in pixels.
        :param y: Top Y coordinate in pixels.
        :param width: Total bar width in pixels.
        :param value: Current measured value.
        :param minimum: Lower scale bound (0% bar fill). Defaults to 0.
        :param maximum: Upper scale bound (100% bar fill). Defaults to 100.
        :param height: Total bar height in pixels. Defaults to 6.
        """
        if width < 3 or height < 3:
            raise ValueError("Bar width and height must be at least 3 pixels")
        if maximum <= minimum:
            raise ValueError("Maximum must be greater than minimum")

        clamped = max(minimum, min(value, maximum))
        inner_width = width - 2
        inner_height = height - 2
        filled_width = int(inner_width * (clamped - minimum) / (maximum - minimum))

        self.rect(x, y, width, height, 1)
        self.fill_rect(x + 1, y + 1, inner_width, inner_height, 0)
        if filled_width > 0:
            self.fill_rect(x + 1, y + 1, filled_width, inner_height, 1)

    def draw_measurement(self, label, value, unit, y, minimum, maximum, is_alert=False):
        """
        Draw a measured quantity name, numeric value, optional alert mark, and bar graph.

        Taken from laboratory exercises:
        https://gitlab.fekt.vut.cz/fryza/micropython-course-labs

        :param label: Name of the measured quantity ('Temp', 'Humidity', 'Soil').
        :param value: Numeric reading, or None if sensor read failed.
        :param unit: Unit string ('C' or '%').
        :param y: Top Y coordinate of the row.
        :param minimum: Lower tolerance limit (empty bar).
        :param maximum: Upper tolerance limit (full bar).
        :param is_alert: True to display an exclamation mark on the right.
        """
        self.text(label, 0, y)

        if value is None:
            self.text("ERR", 92, y)
            bar_value = minimum
        else:
            self.text(f"{value:5.1f}{unit}", 68, y)
            bar_value = value

        if is_alert:
            self.text("!", 120, y)

        self.draw_bar(0, y + 9, self.width, bar_value, minimum, maximum, height=6)

    def show_dashboard(
        self,
        temp,
        humidity,
        soil_moisture,
        fan_on,
        targets=None,
        tolerances=None,
        alerts=None,
    ):
        """
        Display the main greenhouse monitor screen with measured values, tolerance-scaled bars and fan operation indication.

        :param temp: Air temperature in degrees Celsius (or None on error).
        :param humidity: Relative air humidity in % (or None on error).
        :param soil_moisture: Soil moisture in % (or None on error).
        :param fan_on: Boolean indicating whether the fan relay is active.
        :param targets: Dictionary of target setpoints, e.g. {'temp': 21.0, 'hum': 50.0, 'soil': 50.0}.
        :param tolerances: Dictionary of allowed +/- tolerances, e.g. {'temp': 2.0, 'hum': 10.0, 'soil': 10.0}.
        :param alerts: Optional dictionary of alert flags; if None, computed from limits.
        """
        if not self.is_on:
            return

        if targets is None:
            targets = {"temp": 21.0, "hum": 50.0, "soil": 50.0}
        if tolerances is None:
            tolerances = {"temp": 2.0, "hum": 10.0, "soil": 10.0}

        temp_min, temp_max = targets["temp"] - tolerances["temp"], targets["temp"] + tolerances["temp"]
        hum_min, hum_max = targets["hum"] - tolerances["hum"], targets["hum"] + tolerances["hum"]
        soil_min, soil_max = targets["soil"] - tolerances["soil"], targets["soil"] + tolerances["soil"]

        if alerts is None:
            alerts = {
                "temp": temp is None or temp < temp_min or temp > temp_max,
                "hum": humidity is None or humidity < hum_min or humidity > hum_max,
                "soil": soil_moisture is None or soil_moisture < soil_min or soil_moisture > soil_max,
            }

        self.fill(0)

        self.text("FAN:ON" if fan_on else "FAN:OFF", 0, 0)
        if any(alerts.values()):
            self.fill_rect(72, 0, 56, 9, 1)
            self.text("ALERT!", 76, 1, 0)

        self.hline(0, 10, self.width, 1)

        self.draw_measurement("Temp", temp, "C", 13, temp_min, temp_max, alerts.get("temp", False))
        self.draw_measurement("Humidity", humidity, "%", 30, hum_min, hum_max, alerts.get("hum", False))
        self.draw_measurement("Soil", soil_moisture, "%", 47, soil_min, soil_max, alerts.get("soil", False))

        self.show()

    def show_settings(self, target_temp, target_hum, target_soil, selected_idx=0):
        """
        Display the threshold setup screen controlled by the rotary encoder.

        :param target_temp: Target air temperature in degrees Celsius.
        :param target_hum: Target air humidity in %.
        :param target_soil: Target soil moisture in %.
        :param selected_idx: Active row index (0=Temp, 1=Humidity, 2=Soil).
        """
        if not self.is_on:
            return

        self.fill(0)
        self.text("SET TARGETS", 18, 0)
        self.hline(0, 10, self.width, 1)

        items = [
            ("Temp    :", f"{target_temp:5.1f}C", 16),
            ("Humidity:", f"{target_hum:5.1f}%", 32),
            ("Soil    :", f"{target_soil:5.1f}%", 48),
        ]

        for idx, (label, val_str, y) in enumerate(items):
            prefix = ">" if idx == selected_idx else " "
            self.text(f"{prefix}{label}", 0, y)
            self.text(val_str, 80, y)

        self.show()


def demo():
    """Code designed to test all functions."""
    from machine import I2C, Pin
    import time

    i2c0 = I2C(0, sda=Pin(4), scl=Pin(5), freq=400_000)
    display = oled_driver(i2c0)

    targets = {"temp": 21.0, "hum": 50.0, "soil": 50.0}
    tolerances = {"temp": 2.0, "hum": 10.0, "soil": 10.0}

    display.contrast(255)
    display.show_boot_screen()
    time.sleep(3)

    display.show_dashboard(
        temp=21.0,
        humidity=50.0,
        soil_moisture=50.0,
        fan_on=False,
        targets=targets,
        tolerances=tolerances,
    )
    time.sleep(3)

    display.show_dashboard(
        temp=26.2,
        humidity=65.0,
        soil_moisture=38.0,
        fan_on=True,
        targets=targets,
        tolerances=tolerances,
    )
    time.sleep(3)

    display.show_settings(target_temp=21.0, target_hum=50.0, target_soil=50.0, selected_idx=1)


if __name__ == "__main__":
    demo()
