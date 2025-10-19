#!/usr/bin/env python3
"""Clear to BLACK (0x00) without BUSY wait"""
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

try:
    print("Reset...")
    GPIO.output(RST_PIN, GPIO.HIGH)
    time.sleep(0.2)
    GPIO.output(RST_PIN, GPIO.LOW)
    time.sleep(0.01)
    GPIO.output(RST_PIN, GPIO.HIGH)
    time.sleep(0.2)

    print("Init...")
    cmd(0x01); dat(0x03); dat(0x00); dat(0x2b); dat(0x2b); dat(0x09)
    cmd(0x06); dat(0x07); dat(0x07); dat(0x17)
    cmd(0x04); time.sleep(0.3)
    cmd(0x00); dat(0xAF)
    cmd(0x30); dat(0x3A)
    cmd(0x61); dat(0xB0); dat(0x01); dat(0x08)
    cmd(0x82); dat(0x12)
    cmd(0x50); dat(0x97)

    print("Clearing to BLACK (0x00)...")
    cmd(0x10)
    for i in range(5808):
        dat(0x00)
    cmd(0x13)
    for i in range(5808):
        dat(0x00)

    print("Refreshing...")
    cmd(0x12)
    time.sleep(3)

    print("\n✅ DONE - should be BLACK\n")

except Exception as e:
    print(f"ERROR: {e}")

finally:
    spi.close()
    GPIO.cleanup()
