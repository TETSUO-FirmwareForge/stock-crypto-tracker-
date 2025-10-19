#!/usr/bin/env python3
"""
CORRECT commands for Waveshare 2.7" V2 display
Based on official epd2in7_V2.py
"""
import time
import RPi.GPIO as GPIO
import spidev

RST_PIN = 17
DC_PIN = 25
BUSY_PIN = 24

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(RST_PIN, GPIO.OUT)
GPIO.setup(DC_PIN, GPIO.OUT)
GPIO.setup(BUSY_PIN, GPIO.IN)

spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 4000000
spi.mode = 0b00

def wait_busy():
    print("Waiting for display...")
    timeout = 0
    while GPIO.input(BUSY_PIN) == 1 and timeout < 50:
        time.sleep(0.1)
        timeout += 1
    if timeout >= 50:
        print("WARNING: Timeout waiting for BUSY")
    else:
        print("Display ready")

def cmd(c):
    GPIO.output(DC_PIN, GPIO.LOW)
    spi.writebytes([c])

def dat(d):
    GPIO.output(DC_PIN, GPIO.HIGH)
    spi.writebytes([d])

def reset():
    print("Hardware reset...")
    GPIO.output(RST_PIN, GPIO.HIGH)
    time.sleep(0.2)
    GPIO.output(RST_PIN, GPIO.LOW)
    time.sleep(0.002)
    GPIO.output(RST_PIN, GPIO.HIGH)
    time.sleep(0.2)

try:
    reset()
    wait_busy()

    print("\n=== V2 INIT SEQUENCE ===")

    # Software reset
    print("Software reset...")
    cmd(0x12)  # SWRESET
    wait_busy()

    # Set Ram-Y address start/end position
    print("Set RAM Y address...")
    cmd(0x45)
    dat(0x00)
    dat(0x00)
    dat(0x07)  # 0x0107 = 263+1 = 264
    dat(0x01)

    # Set RAM y address count to 0
    print("Set RAM Y counter...")
    cmd(0x4F)
    dat(0x00)
    dat(0x00)

    # Data entry mode
    print("Set data entry mode...")
    cmd(0x11)
    dat(0x03)

    print("Init complete!\n")

    # Clear to WHITE (0xFF)
    print("=== CLEARING TO WHITE ===")
    print("Sending data to 0x24...")
    cmd(0x24)
    Width = 176 // 8  # 22 bytes per row
    Height = 264

    for j in range(Height):
        for i in range(Width):
            dat(0xFF)

    print("Data sent. Turning on display...")

    # TurnOnDisplay (V2 style)
    cmd(0x22)  # Display Update Control
    dat(0xF7)
    cmd(0x20)  # Activate Display Update Sequence
    wait_busy()

    print("\n✅ DONE! Display should be WHITE now!\n")

    # Sleep
    cmd(0x10)
    dat(0x01)

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

finally:
    spi.close()
    GPIO.cleanup()
