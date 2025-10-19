#!/usr/bin/env python3
"""
NUCLEAR CLEAR - Maximum effort to clear all ghosting.
Uses multiple refresh cycles with different patterns.
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
    timeout = 0
    while GPIO.input(BUSY_PIN) == 1:
        time.sleep(0.01)
        timeout += 1
        if timeout > 500:  # 5 seconds
            break
    time.sleep(0.2)

def init_display(spi):
    reset()
    wait_until_idle()

    send_command(spi, 0x12)  # Software reset
    wait_until_idle()

    send_command(spi, 0x01)  # Driver output control
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

    send_command(spi, 0x18)  # Temperature
    send_data(spi, 0x80)

    wait_until_idle()

def fill_and_refresh(spi, byte_value, update_mode):
    """Fill display and refresh."""
    # Set counters
    send_command(spi, 0x4E)
    send_data(spi, 0x00)
    send_command(spi, 0x4F)
    send_data(spi, 0x00)
    send_data(spi, 0x00)

    # Write RAM
    send_command(spi, 0x24)
    GPIO.output(DC_PIN, GPIO.HIGH)
    for i in range(5808):
        spi.writebytes([byte_value])

    # Update
    send_command(spi, 0x22)
    send_data(spi, update_mode)
    send_command(spi, 0x20)
    wait_until_idle()

def main():
    print("=== NUCLEAR CLEAR ===\n")
    print("Maximum effort ghosting removal")
    print("This will take ~2 minutes\n")

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
        print("Phase 1: Initialize...")
        init_display(spi)
        print("OK\n")

        print("Phase 2: Full refresh cycles (20x)...")
        for i in range(20):
            if i % 2 == 0:
                print(f"  {i+1}/20: BLACK", end='', flush=True)
                fill_and_refresh(spi, 0xFF, 0xC7)
            else:
                print(f" -> WHITE", end='', flush=True)
                fill_and_refresh(spi, 0x00, 0xC7)
                print(" ✓")
            time.sleep(0.3)

        print("\nPhase 3: Final WHITE clears (5x)...")
        for i in range(5):
            print(f"  {i+1}/5...", end='', flush=True)
            fill_and_refresh(spi, 0x00, 0xC7)
            print(" ✓")
            time.sleep(0.5)

        print("\n✅ COMPLETE!")
        print("\nDisplay should be PURE WHITE now.")
        print("If you still see ghosting, the e-paper may need to rest\n")

        # Sleep mode
        send_command(spi, 0x10)
        send_data(spi, 0x01)
        time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        spi.close()
        GPIO.cleanup()
        print("Cleanup done")

if __name__ == "__main__":
    main()
