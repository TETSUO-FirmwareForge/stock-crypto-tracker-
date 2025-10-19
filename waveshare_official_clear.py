#!/usr/bin/env python3
"""
OFFICIAL Waveshare 2.7" initialization and clear
Based on official waveshare_epd/epd2in7.py
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
    print("Wait busy...")
    while GPIO.input(BUSY_PIN) == 1:
        time.sleep(0.01)
    time.sleep(0.2)

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
    time.sleep(0.002)
    GPIO.output(RST_PIN, GPIO.HIGH)
    time.sleep(0.2)

try:
    reset()

    print("OFFICIAL Waveshare init sequence...")

    # POWER_SETTING
    cmd(0x01)
    dat(0x03)  # VDS_EN, VDG_EN
    dat(0x00)  # VCOM_HV, VGHL_LV
    dat(0x2b)  # VDH
    dat(0x2b)  # VDL
    dat(0x09)  # VDHR

    # BOOSTER_SOFT_START
    cmd(0x06)
    dat(0x07)
    dat(0x07)
    dat(0x17)

    # POWER_ON
    cmd(0x04)
    wait_busy()

    # PANEL_SETTING
    cmd(0x00)
    dat(0xAF)  # KW-BF   KWR-AF  BWROTP 0f

    # PLL_CONTROL
    cmd(0x30)
    dat(0x3A)  # 100Hz

    # VCOM AND DATA INTERVAL SETTING
    cmd(0x50)
    dat(0x57)

    # VCM_DC_SETTING
    cmd(0x82)
    dat(0x12)

    # TCON SETTING
    cmd(0x60)
    dat(0x22)

    # RESOLUTION SETTING (176x264)
    cmd(0x61)
    dat(0xB0)  # 176
    dat(0x01)  # 264 high byte
    dat(0x08)  # 264 low byte

    # VCM_DC_SETTING_REGISTER
    cmd(0x82)
    dat(0x12)

    # VCOM AND DATA INTERVAL SETTING
    cmd(0x50)
    dat(0x97)

    print("Init complete!\n")

    print("Clearing to WHITE (0xFF)...")

    # Clear sequence from official code
    cmd(0x10)  # DATA_START_TRANSMISSION_1
    for i in range(5808):  # 176*264/8 = 5808
        dat(0xFF)

    cmd(0x13)  # DATA_START_TRANSMISSION_2
    for i in range(5808):
        dat(0xFF)

    print("Sending DISPLAY_REFRESH...")
    cmd(0x12)  # DISPLAY_REFRESH
    wait_busy()

    print("\n✅ DONE - Display should be WHITE now!")

    # Deep sleep
    cmd(0x02)  # POWER_OFF
    wait_busy()
    cmd(0x07)  # DEEP_SLEEP
    dat(0xA5)

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()

finally:
    spi.close()
    GPIO.cleanup()
