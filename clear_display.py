#!/usr/bin/env python3
"""
Clear display completely to WHITE - remove all ghosting.
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
    while GPIO.input(BUSY_PIN) == 1:
        time.sleep(0.01)
    time.sleep(0.2)

def clear_to_white(spi):
    """Clear display to pure white - with inverted bytes for this display."""
    print("Clearing to WHITE...")

    # For this display 0x00 = white (inverted)
    send_command(spi, 0x24)
    GPIO.output(DC_PIN, GPIO.HIGH)

    # Send all 0x00 for white
    for i in range(5808):  # 176 * 264 / 8
        spi.writebytes([0x00])

    # Full refresh
    send_command(spi, 0x22)
    send_data(spi, 0xC7)
    send_command(spi, 0x20)
    wait_until_idle()

    print("First clear done, doing second clear...")

    # Do it again to remove ghosting
    send_command(spi, 0x24)
    GPIO.output(DC_PIN, GPIO.HIGH)

    for i in range(5808):
        spi.writebytes([0x00])

    send_command(spi, 0x22)
    send_data(spi, 0xC7)
    send_command(spi, 0x20)
    wait_until_idle()

    print("Second clear done!")

def main():
    print("=== CLEAR DISPLAY TO WHITE ===\n")

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
        print("Initializing...")
        reset()
        wait_until_idle()

        send_command(spi, 0x12)
        wait_until_idle()

        send_command(spi, 0x01)
        send_data(spi, 0x07)
        send_data(spi, 0x01)
        send_data(spi, 0x00)

        send_command(spi, 0x11)
        send_data(spi, 0x03)

        send_command(spi, 0x44)
        send_data(spi, 0x00)
        send_data(spi, 0x15)

        send_command(spi, 0x45)
        send_data(spi, 0x00)
        send_data(spi, 0x00)
        send_data(spi, 0x07)
        send_data(spi, 0x01)

        send_command(spi, 0x3C)
        send_data(spi, 0x05)

        send_command(spi, 0x18)
        send_data(spi, 0x80)

        send_command(spi, 0x4E)
        send_data(spi, 0x00)

        send_command(spi, 0x4F)
        send_data(spi, 0x00)
        send_data(spi, 0x00)

        wait_until_idle()

        # Clear twice to remove ghosting
        clear_to_white(spi)

        print("\n✅ DONE!")
        print("Display should be COMPLETELY WHITE now\n")

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
