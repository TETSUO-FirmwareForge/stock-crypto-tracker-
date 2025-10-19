#!/usr/bin/env python3
"""Quick white test - minimal waits"""
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

try:
    print("Quick reset...")
    GPIO.output(RST_PIN, GPIO.HIGH)
    time.sleep(0.1)
    GPIO.output(RST_PIN, GPIO.LOW)
    time.sleep(0.005)
    GPIO.output(RST_PIN, GPIO.HIGH)
    time.sleep(0.1)

    def cmd(c):
        GPIO.output(DC_PIN, GPIO.LOW)
        spi.writebytes([c])

    def dat(d):
        GPIO.output(DC_PIN, GPIO.HIGH)
        spi.writebytes([d])

    print("Init...")
    cmd(0x12)  # SW reset
    time.sleep(0.1)

    print("Sending WHITE (0xFF)...")
    cmd(0x10)
    GPIO.output(DC_PIN, GPIO.HIGH)
    for i in range(5808):
        spi.writebytes([0xFF])

    cmd(0x13)
    GPIO.output(DC_PIN, GPIO.HIGH)
    for i in range(5808):
        spi.writebytes([0xFF])

    print("Refresh...")
    cmd(0x12)
    time.sleep(2)  # Short wait

    print("DONE - check display")

finally:
    spi.close()
    GPIO.cleanup()
