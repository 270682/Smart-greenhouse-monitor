from machine import ADC
import time


def read_adc(adc, samples=8):
    raw = 0
    for _ in range(samples):
        raw = raw + adc.read_u16()

    raw = round(raw / samples)
    voltage = raw * 3.3 / 65_535
    return raw, voltage


def main():
    adc = ADC(26)

    print("Turn the potentiometer; press Ctrl+C to stop.")

    try:
        while True:
            raw, voltage = read_adc(adc, samples=10)
            print(
                f"raw: {raw:5d}   "
                f"voltage: {voltage:.3f} V"
            )
            time.sleep_ms(100)

    except KeyboardInterrupt:
        print("\nProgram stopped. Exiting...")


if __name__ == "__main__":
    main()
