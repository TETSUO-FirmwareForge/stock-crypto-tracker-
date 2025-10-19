#!/usr/bin/env python3
"""
Most basic test - Clear display to white using Waveshare method.
"""

import time
import RPi.GPIO as GPIO
import spidev

# GPIO pins
RST_PIN = 17
DC_PIN = 25
CS_PIN = 8
BUSY_PIN = 24

# Display dimensions
EPD_WIDTH = 176
EPD_HEIGHT = 264

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
    print("Waiting for display to be idle...", end='', flush=True)
    while GPIO.input(BUSY_PIN) == 1:
        time.sleep(0.01)
    time.sleep(0.2)
    print(" done")

def main():
    print("=== BASIC WAVESHARE 2.7\" CLEAR TEST ===\n")

    # Setup GPIO (CS_PIN is handled by SPI, don't configure it)
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(RST_PIN, GPIO.OUT)
    GPIO.setup(DC_PIN, GPIO.OUT)
    GPIO.setup(BUSY_PIN, GPIO.IN)

    # Setup SPI
    spi = spidev.SpiDev()
    spi.open(0, 0)
    spi.max_speed_hz = 4000000
    spi.mode = 0b00

    try:
        print("1. Hardware reset...")
        reset()

        print("2. Initialize display...")
        wait_until_idle()

        # Software reset
        send_command(spi, 0x12)
        wait_until_idle()

        # Driver output control
        send_command(spi, 0x01)
        send_data(spi, 0x07)
        send_data(spi, 0x01)
        send_data(spi, 0x00)

        # Data entry mode
        send_command(spi, 0x11)
        send_data(spi, 0x03)

        # Set RAM X address
        send_command(spi, 0x44)
        send_data(spi, 0x00)
        send_data(spi, 0x15)  # 176/8-1 = 21 = 0x15

        # Set RAM Y address
        send_command(spi, 0x45)
        send_data(spi, 0x00)
        send_data(spi, 0x00)
        send_data(spi, 0x07)  # 264-1 low byte
        send_data(spi, 0x01)  # 264-1 high byte

        # Border waveform
        send_command(spi, 0x3C)
        send_data(spi, 0x05)

        # Temperature sensor
        send_command(spi, 0x1A)
        send_data(spi, 0x80)

        # Set RAM X address counter
        send_command(spi, 0x4E)
        send_data(spi, 0x00)

        # Set RAM Y address counter
        send_command(spi, 0x4F)
        send_data(spi, 0x00)
        send_data(spi, 0x00)

        wait_until_idle()

        print("3. Clearing display to WHITE...")

        # Write RAM - all 0xFF for white
        send_command(spi, 0x24)
        GPIO.output(DC_PIN, GPIO.HIGH)

        # Send all white bytes (0xFF)
        white_data = [0xFF] * 5808  # 176 * 264 / 8
        for byte in white_data:
            spi.writebytes([byte])

        print("4. Activating display update...")

        # Display update control
        send_command(spi, 0x22)
        send_data(spi, 0xC7)  # Full update

        # Master activation
        send_command(spi, 0x20)

        wait_until_idle()

        print("\n✅ DONE! Display should be WHITE now.\n")

        # Sleep mode
        print("5. Entering sleep mode...")
        send_command(spi, 0x10)
        send_data(spi, 0x01)
        time.sleep(0.1)

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

    finally:
        spi.close()
        GPIO.cleanup()
        print("GPIO cleaned up")

if __name__ == "__main__":
    main()
