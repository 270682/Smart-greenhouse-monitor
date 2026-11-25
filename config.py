"""
Configuration constants for the Smart Greenhouse Monitor.
"""

# I2C buses
I2C0_SDA = 4       # OLED display SH1106
I2C0_SCL = 5
I2C1_SDA = 26      # BME280 sensor
I2C1_SCL = 27

# Analog and digital inputs
SOIL_ADC_PIN = 28
ENC_CLK_PIN = 13
ENC_DT_PIN = 14
ENC_SW_PIN = 15
BTN_DISP_PIN = 17

# Outputs
RELAY_PIN = 16
RGB_LED_PIN = 22
RGB_LED_BRIGHTNESS = 0.25

# Soil moisture sensor calibration
SOIL_DRY_VALUE = 52000
SOIL_WET_VALUE = 24000

# Default target setpoints
DEFAULT_TARGETS = {
    "temp": 22.0,   # °C
    "hum": 55.0,    # %
    "soil": 50.0,   # %
}

# Allowed +/- tolerances around target setpoints
TOLERANCES = {
    "temp": 2.0,    # °C
    "hum": 10.0,    # %
    "soil": 10.0,   # %
}