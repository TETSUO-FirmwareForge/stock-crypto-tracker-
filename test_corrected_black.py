#!/usr/bin/env python3
"""
Test the CORRECTED Waveshare commands to show pure BLACK screen.
Uses official command sequence: 0x10 (old frame), 0x13 (new frame), 0x12 (refresh)
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
    time.sleep(0.005)
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

def main():
    print("=== CORRECTED BLACK SCREEN TEST ===")
    print("Using official Waveshare commands\n")

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
        send_data(spi, 0x15)

        # Set RAM Y address
        send_command(spi, 0x45)
        send_data(spi, 0x00)
        send_data(spi, 0x00)
        send_data(spi, 0x07)
        send_data(spi, 0x01)

        # Border waveform
        send_command(spi, 0x3C)
        send_data(spi, 0x05)

        # Temperature sensor
        send_command(spi, 0x18)
        send_data(spi, 0x80)

        # Set RAM X counter
        send_command(spi, 0x4E)
        send_data(spi, 0x00)

        # Set RAM Y counter
        send_command(spi, 0x4F)
        send_data(spi, 0x00)
        send_data(spi, 0x00)

        wait_until_idle()
        print("OK\n")

        print("Clearing to BLACK using OFFICIAL commands...")

        # OFFICIAL WAVESHARE CLEAR SEQUENCE
        # Command 0x10: Write old frame (all black = 0x00)
        print("  Sending old frame (0x10)...")
        send_command(spi, 0x10)
        GPIO.output(DC_PIN, GPIO.HIGH)
        for i in range(5808):
            spi.writebytes([0x00])

        # Command 0x13: Write new frame (all black = 0x00)
        print("  Sending new frame (0x13)...")
        send_command(spi, 0x13)
        GPIO.output(DC_PIN, GPIO.HIGH)
        for i in range(5808):
            spi.writebytes([0x00])

        # Command 0x12: Refresh display
        print("  Refreshing display (0x12)...")
        send_command(spi, 0x12)
        wait_until_idle()

        print("\n✅ COMPLETE!")
        print("Display should be PURE BLACK now\n")
        print("If it's BLACK: Commands are CORRECT!")
        print("If it's WHITE: We need to use 0xFF instead of 0x00\n")

        # Deep sleep
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
