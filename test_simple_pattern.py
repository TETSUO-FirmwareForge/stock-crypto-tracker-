#!/usr/bin/env python3
"""
Test with a simple black and white pattern - half black, half white.
This will help us see if ANYTHING is updating on the display.
"""

import time
import RPi.GPIO as GPIO
import spidev

RST_PIN = 17
DC_PIN = 25
BUSY_PIN = 24

def reset():
    GPIO.output(RST_PIN, GPIO.HIGH)
    time.sleep(0.2)
    GPIO.output(RST_PIN, GPIO.LOW)
    time.sleep(0.002)
    GPIO.output(RST_PIN, GPIO.HIGH)
    time.sleep(0.2)

def send_command(spi, command):
    GPIO.output(DC_PIN, GPIO.LOW)
    spi.writebytes([command])

def send_data(spi, data):
    GPIO.output(DC_PIN, GPIO.HIGH)
    spi.writebytes([data])

def wait_until_idle():
    print(".", end='', flush=True)
    while GPIO.input(BUSY_PIN) == 1:
        time.sleep(0.01)
    time.sleep(0.2)

def main():
    print("=== PATTERN TEST: Half WHITE / Half BLACK ===\n")
    print("This will show WHITE on top half, BLACK on bottom half")
    print("If you see this pattern, the display IS working!\n")

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(RST_PIN, GPIO.OUT)
    GPIO.setup(DC_PIN, GPIO.OUT)
    GPIO.setup(BUSY_PIN, GPIO.IN)

    spi = spidev.SpiDev()
    spi.open(0, 0)
    spi.max_speed_hz = 4000000
    spi.mode = 0b00

    try:
        print("1. Reset", end='')
        reset()
        wait_until_idle()
        print(" OK")

        print("2. Init", end='')
        send_command(spi, 0x12)  # SW reset
        wait_until_idle()

        send_command(spi, 0x01)  # Driver output
        send_data(spi, 0x07)
        send_data(spi, 0x01)
        send_data(spi, 0x00)

        send_command(spi, 0x11)  # Data entry mode
        send_data(spi, 0x03)

        send_command(spi, 0x44)  # Set RAM X
        send_data(spi, 0x00)
        send_data(spi, 0x15)

        send_command(spi, 0x45)  # Set RAM Y
        send_data(spi, 0x00)
        send_data(spi, 0x00)
        send_data(spi, 0x07)
        send_data(spi, 0x01)

        send_command(spi, 0x3C)  # Border
        send_data(spi, 0x05)

        send_command(spi, 0x18)  # Temperature sensor
        send_data(spi, 0x80)

        send_command(spi, 0x4E)  # Set RAM X counter
        send_data(spi, 0x00)

        send_command(spi, 0x4F)  # Set RAM Y counter
        send_data(spi, 0x00)
        send_data(spi, 0x00)

        wait_until_idle()
        print(" OK")

        print("3. Writing pattern", end='')
        send_command(spi, 0x24)
        GPIO.output(DC_PIN, GPIO.HIGH)

        # 176 * 264 = 46464 pixels = 5808 bytes
        # First half WHITE (0xFF), second half BLACK (0x00)
        half = 5808 // 2

        # Top half: WHITE
        for i in range(half):
            spi.writebytes([0xFF])

        # Bottom half: BLACK
        for i in range(half):
            spi.writebytes([0x00])

        print(" OK")

        print("4. Update display", end='')
        send_command(spi, 0x22)
        send_data(spi, 0xC7)
        send_command(spi, 0x20)
        wait_until_idle()
        print(" OK")

        print("\n✅ DONE!\n")
        print("You should see:")
        print("  - TOP HALF: WHITE")
        print("  - BOTTOM HALF: BLACK")
        print("\nIf you see this, the display IS working!")
        print("If not, check physical connection.\n")

        time.sleep(2)

        print("5. Sleep mode...")
        send_command(spi, 0x10)
        send_data(spi, 0x01)

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

    finally:
        spi.close()
        GPIO.cleanup()

if __name__ == "__main__":
    main()
