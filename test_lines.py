#!/usr/bin/env python3
"""
Test drawing BLACK lines on WHITE background.
This confirms we can draw patterns correctly.
"""

import time
import RPi.GPIO as GPIO
import spidev

RST_PIN = 17
DC_PIN = 25
BUSY_PIN = 24
WIDTH = 176
HEIGHT = 264

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

def main():
    print("=== DRAWING TEST: BLACK lines on WHITE ===\n")

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
        print("1. Initializing...")
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

        print("2. Creating pattern...")
        # Create buffer: WHITE background with BLACK border and cross
        buffer_size = (WIDTH * HEIGHT) // 8
        buffer = bytearray([0xFF] * buffer_size)  # Start with all white

        # Draw BLACK border (first and last rows, first and last columns)
        bytes_per_row = WIDTH // 8

        # Top border (first row)
        for i in range(bytes_per_row):
            buffer[i] = 0x00

        # Bottom border (last row)
        last_row_start = buffer_size - bytes_per_row
        for i in range(bytes_per_row):
            buffer[last_row_start + i] = 0x00

        # Left and right borders
        for y in range(HEIGHT):
            row_start = y * bytes_per_row
            buffer[row_start] = 0x00  # Left border
            buffer[row_start + bytes_per_row - 1] = 0x00  # Right border

        # Draw cross in the middle
        middle_y = HEIGHT // 2
        middle_x_byte = (WIDTH // 2) // 8

        # Horizontal line
        for i in range(bytes_per_row):
            buffer[middle_y * bytes_per_row + i] = 0x00

        # Vertical line
        for y in range(HEIGHT):
            buffer[y * bytes_per_row + middle_x_byte] = 0x00

        print("3. Sending to display...")
        send_command(spi, 0x24)
        GPIO.output(DC_PIN, GPIO.HIGH)

        for byte in buffer:
            spi.writebytes([byte])

        print("4. Refreshing...")
        send_command(spi, 0x22)
        send_data(spi, 0xC7)
        send_command(spi, 0x20)
        wait_until_idle()

        print("\n✅ DONE!\n")
        print("You should see:")
        print("  - WHITE background")
        print("  - BLACK border around edges")
        print("  - BLACK cross in the middle")
        print("\nIf you see this, we can draw correctly!\n")

        time.sleep(2)

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
