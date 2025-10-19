#!/usr/bin/env python3
"""
ALL BLACK - Make the display completely black.
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

def fill_black(spi):
    """Fill display with pure BLACK."""
    send_command(spi, 0x24)
    GPIO.output(DC_PIN, GPIO.HIGH)

    # 0xFF = BLACK (for this inverted display)
    for i in range(5808):
        spi.writebytes([0xFF])

    # Full refresh
    send_command(spi, 0x22)
    send_data(spi, 0xC7)
    send_command(spi, 0x20)
    wait_until_idle()

def main():
    print("=== SET DISPLAY TO PURE BLACK ===\n")

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
        print("OK\n")

        # Fill with BLACK multiple times to ensure it's pure black
        print("Filling with BLACK...")
        for i in range(3):
            print(f"  Pass {i+1}/3...", end='', flush=True)
            fill_black(spi)
            print(" DONE")
            time.sleep(0.5)

        print("\n✅ COMPLETE!")
        print("Display should be PURE BLACK now\n")

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
