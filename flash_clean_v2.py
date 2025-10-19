#!/usr/bin/env python3
"""
Flash display multiple times to remove ghosting - V2 version
"""
import sys
import time
sys.path.insert(0, '/home/sa/tetsuo-display')
from app.display_driver import EPD2in7

def main():
    print("=== CLEANING DISPLAY - REMOVING GHOSTING ===\n")

    epd = EPD2in7()
    epd.init('full')

    # Flash 10 times between white and black
    for i in range(10):
        print(f"Flash {i+1}/10: WHITE", end='', flush=True)
        white_buffer = bytes([0xFF] * 5808)
        epd.display_frame(white_buffer)
        epd.refresh('full')
        print(" -> BLACK", flush=True)
        black_buffer = bytes([0x00] * 5808)
        epd.display_frame(black_buffer)
        epd.refresh('full')
        time.sleep(0.1)

    # Final: leave it white
    print("\nFinal: Setting to WHITE...")
    white_buffer = bytes([0xFF] * 5808)
    epd.display_frame(white_buffer)
    epd.refresh('full')

    print("\n✅ DONE! Display should be clean white now\n")

    epd.sleep()
    epd.cleanup()

if __name__ == "__main__":
    main()
