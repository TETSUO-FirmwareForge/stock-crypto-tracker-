#!/usr/bin/env python3
"""
Clear display WITHOUT waiting for BUSY pin
Uses fixed time delays instead
"""
import time
import RPi.GPIO as GPIO
import spidev

RST_PIN = 17
DC_PIN = 25

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(RST_PIN, GPIO.OUT)
GPIO.setup(DC_PIN, GPIO.OUT)

spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 4000000
spi.mode = 0b00

def cmd(c):
    GPIO.output(DC_PIN, GPIO.LOW)
    spi.writebytes([c])

def dat(d):
    GPIO.output(DC_PIN, GPIO.HIGH)
    spi.writebytes([d])

def reset():
    print("Reset...")
    GPIO.output(RST_PIN, GPIO.HIGH)
    time.sleep(0.2)
    GPIO.output(RST_PIN, GPIO.LOW)
    time.sleep(0.01)
    GPIO.output(RST_PIN, GPIO.HIGH)
    time.sleep(0.2)

try:
    reset()

    print("Init with FIXED delays (no BUSY wait)...")

    # POWER_SETTING
    cmd(0x01)
    dat(0x03)
    dat(0x00)
    dat(0x2b)
    dat(0x2b)
    dat(0x09)

    # BOOSTER_SOFT_START
    cmd(0x06)
    dat(0x07)
    dat(0x07)
    dat(0x17)

    # POWER_ON
    cmd(0x04)
    time.sleep(0.3)  # Fixed delay instead of wait_busy

    # PANEL_SETTING
    cmd(0x00)
    dat(0xAF)

    # PLL_CONTROL
    cmd(0x30)
    dat(0x3A)

    # RESOLUTION
    cmd(0x61)
    dat(0xB0)  # 176
    dat(0x01)  # 264 >> 8
    dat(0x08)  # 264 & 0xFF

    # VCM_DC_SETTING
    cmd(0x82)
    dat(0x12)

    # VCOM AND DATA INTERVAL
    cmd(0x50)
    dat(0x97)

    time.sleep(0.1)
    print("Init OK\n")

    print("Clearing to WHITE...")
    cmd(0x10)
    for i in range(5808):
        dat(0xFF)

    cmd(0x13)
    for i in range(5808):
        dat(0xFF)

    print("Refreshing...")
    cmd(0x12)
    time.sleep(3)  # Fixed 3 second delay for refresh

    print("\n✅ DONE! Check display\n")

    # Power off
    cmd(0x02)
    time.sleep(0.3)
    cmd(0x07)
    dat(0xA5)

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()

finally:
    spi.close()
    GPIO.cleanup()
