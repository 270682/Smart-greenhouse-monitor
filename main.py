"""
Main application for the Smart Greenhouse Monitor.
"""

import uasyncio as asyncio
from machine import I2C, Pin
import config

from bme280 import BME280
from gpio_devices import Button
from drivers.oled_driver import oled_driver
from drivers.soil_moisture_driver import MoistureSensor
from drivers.relay_driver import Relay
from drivers.led_driver import StatusLed
from drivers.rotary_encoder import RotaryEncoder


def create_initial_state():
    """Create the shared application state dictionary."""
    t = config.DEFAULT_TARGETS
    tol = config.TOLERANCES
    return {
        "temp": None,
        "humidity": None,
        "soil": None,
        "targets": t.copy(),
        "limits": {
            "temp": (t["temp"] - tol["temp"], t["temp"] + tol["temp"]),
            "hum": (t["hum"] - tol["hum"], t["hum"] + tol["hum"]),
            "soil": (t["soil"] - tol["soil"], t["soil"] + tol["soil"]),
        },
        "alerts": {"temp": False, "hum": False, "soil": False},
        "fan_on": False,
        "led_color": StatusLed.PURPLE,
        "ui_step": 0,  # 0 = Dashboard, 1 = Temp, 2 = Humidity, 3 = Soil
    }


def evaluate_greenhouse(state, tolerances):
    """
    Calculate tolerance limits, alert flags, fan state with hysteresis,
    and RGB LED priority color from current sensor readings.
    """
    temp = state["temp"]
    hum = state["humidity"]
    soil = state["soil"]
    targets = state["targets"]

    t_min = targets["temp"] - tolerances["temp"]
    t_max = targets["temp"] + tolerances["temp"]
    h_min = targets["hum"] - tolerances["hum"]
    h_max = targets["hum"] + tolerances["hum"]
    s_min = targets["soil"] - tolerances["soil"]
    s_max = targets["soil"] + tolerances["soil"]

    state["limits"]["temp"] = (t_min, t_max)
    state["limits"]["hum"] = (h_min, h_max)
    state["limits"]["soil"] = (s_min, s_max)

    state["alerts"] = {
        "temp": temp is None or temp < t_min or temp > t_max,
        "hum": hum is None or hum < h_min or hum > h_max,
        "soil": soil is None or soil < s_min or soil > s_max,
    }

    # Fan control with hysteresis (turns ON above upper limit, OFF at target)
    if temp is None or hum is None:
        state["fan_on"] = False
    elif temp > t_max or hum > h_max:
        state["fan_on"] = True
    elif temp <= targets["temp"] and hum <= targets["hum"]:
        state["fan_on"] = False

    # RGB LED status color ordered by priority
    if temp is None or hum is None or soil is None:
        state["led_color"] = StatusLed.PURPLE
    elif temp > t_max:
        state["led_color"] = StatusLed.RED
    elif temp < t_min:
        state["led_color"] = StatusLed.CYAN
    elif soil < s_min or hum < h_min:
        state["led_color"] = StatusLed.ORANGE
    elif soil > s_max or hum > h_max:
        state["led_color"] = StatusLed.BLUE
    else:
        state["led_color"] = StatusLed.GREEN


async def sensor_task(bme, soil_sensor, state):
    """Periodically read air temperature, air humidity, and soil moisture."""
    while True:
        try:
            temp, hum, _, _ = bme.read_values()
            state["temp"] = round(temp, 1)
            state["humidity"] = round(hum, 1)
        except OSError:
            state["temp"] = None
            state["humidity"] = None

        try:
            state["soil"] = soil_sensor.read_soil(samples=10)
        except Exception:
            state["soil"] = None

        await asyncio.sleep_ms(2000)


async def control_task(fan_relay, status_led, state):
    """Evaluate greenhouse conditions and update fan relay and RGB LED."""
    while True:
        evaluate_greenhouse(state, config.TOLERANCES)
        fan_relay.set_state(state["fan_on"])
        status_led.set_color(*state["led_color"])
        await asyncio.sleep_ms(500)


async def ui_input_task(encoder, disp_btn, display, state):
    """Handle rotary encoder rotation/press and display power button."""
    keys = ["temp", "hum", "soil"]
    bounds = [
        (5.0, 45.0, 0.5),   # Temp: min, max, step
        (10.0, 95.0, 1.0),  # Humidity: min, max, step
        (5.0, 95.0, 1.0),   # Soil: min, max, step
    ]

    while True:
        if disp_btn.was_pressed():
            display.toggle_power()

        if encoder.was_pressed():
            state["ui_step"] = (state["ui_step"] + 1) % 4

        steps = encoder.get_delta()
        if steps != 0 and state["ui_step"] > 0:
            idx = state["ui_step"] - 1
            key = keys[idx]
            min_v, max_v, step_size = bounds[idx]
            new_val = state["targets"][key] + steps * step_size
            state["targets"][key] = round(max(min_v, min(max_v, new_val)), 1)

        await asyncio.sleep_ms(50)


async def display_task(display, state):
    """Periodically refresh the OLED display screen."""
    while True:
        if state["ui_step"] == 0:
            display.show_dashboard(
                temp=state["temp"],
                humidity=state["humidity"],
                soil_moisture=state["soil"],
                fan_on=state["fan_on"],
                limits=state["limits"],
                alerts=state["alerts"],
            )
        else:
            display.show_settings(
                target_temp=state["targets"]["temp"],
                target_hum=state["targets"]["hum"],
                target_soil=state["targets"]["soil"],
                selected_idx=state["ui_step"] - 1,
            )

        await asyncio.sleep_ms(200)


async def main():
    i2c0 = I2C(0, sda=Pin(config.I2C0_SDA), scl=Pin(config.I2C0_SCL), freq=400_000)
    i2c1 = I2C(1, sda=Pin(config.I2C1_SDA), scl=Pin(config.I2C1_SCL), freq=100_000)

    display = oled_driver(i2c0)
    bme = BME280(i2c1)
    soil_sensor = MoistureSensor(
        adc_pin=config.SOIL_ADC_PIN,
        dry_value=config.SOIL_DRY_VALUE,
        wet_value=config.SOIL_WET_VALUE,
    )
    fan_relay = Relay(pin_number=config.RELAY_PIN)
    status_led = StatusLed(
        pin_number=config.RGB_LED_PIN,
        brightness=config.RGB_LED_BRIGHTNESS,
    )
    encoder = RotaryEncoder(
        clk_pin=config.ENC_CLK_PIN,
        dt_pin=config.ENC_DT_PIN,
        sw_pin=config.ENC_SW_PIN,
    )
    disp_btn = Button(config.BTN_DISP_PIN)

    state = create_initial_state()

    display.show_boot_screen()
    await asyncio.sleep(2)

    asyncio.create_task(sensor_task(bme, soil_sensor, state))
    asyncio.create_task(control_task(fan_relay, status_led, state))
    asyncio.create_task(ui_input_task(encoder, disp_btn, display, state))
    asyncio.create_task(display_task(display, state))

    while True:
        await asyncio.sleep(1)


try:
    asyncio.run(main())
except KeyboardInterrupt:
    Relay(config.RELAY_PIN).off()
    StatusLed(config.RGB_LED_PIN).off()