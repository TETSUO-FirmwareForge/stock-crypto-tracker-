#!/usr/bin/env python3
"""
MEGA FLASH - Flash between BLACK and WHITE 50 times rapidly.
This forces the e-paper particles to move and should clear ghosting.
Then leaves it in your chosen color.
"""

import time
import sys
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
    time.sleep(0.1)

def quick_fill(spi, byte_value):
    """Quick fill and refresh."""
    send_command(spi, 0x4E)
    send_data(spi, 0x00)
    send_command(spi, 0x4F)
    send_data(spi, 0x00)
    send_data(spi, 0x00)

    send_command(spi, 0x24)
    GPIO.output(DC_PIN, GPIO.HIGH)
    for i in range(5808):
        spi.writebytes([byte_value])

    send_command(spi, 0x22)
    send_data(spi, 0xC7)
    send_command(spi, 0x20)
    wait_until_idle()

def main():
    if len(sys.argv) < 2:
        print("Usage: sudo python3 mega_flash.py [black|white]")
        print("  black - ends with pure black screen")
        print("  white - ends with pure white screen")
        sys.exit(1)

    final_color = sys.argv[1].lower()
    if final_color not in ['black', 'white']:
        print("Error: Choose 'black' or 'white'")
        sys.exit(1)

    print("=== MEGA FLASH - GHOSTING REMOVAL ===\n")
    print(f"Will flash 50 times, then end with {final_color.upper()}")
    print("This will take ~3 minutes\n")

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

        wait_until_idle()
        print("OK\n")

        print("Flashing BLACK/WHITE...")
        for i in range(50):
            print(f"\rCycle {i+1}/50", end='', flush=True)
            quick_fill(spi, 0xFF)  # BLACK
            quick_fill(spi, 0x00)  # WHITE
            time.sleep(0.1)

        print("\n\nApplying final color...")
        final_byte = 0xFF if final_color == 'black' else 0x00
        for i in range(5):
            print(f"  Pass {i+1}/5...", end='', flush=True)
            quick_fill(spi, final_byte)
            print(" DONE")

        print(f"\n✅ COMPLETE! Display is now {final_color.upper()}\n")

        send_command(spi, 0x10)
        send_data(spi, 0x01)

    except KeyboardInterrupt:
        print("\n\nInterrupted")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        spi.close()
        GPIO.cleanup()

if __name__ == "__main__":
    main()
