#!/usr/bin/env python3
"""
Test script to display a completely WHITE screen on the e-paper display.
This verifies the hardware is working correctly.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from app.display_driver import EPD2in7
    print("Display driver imported successfully")
except Exception as e:
    print(f"Error importing display driver: {e}")
    sys.exit(1)

def main():
    print("=== E-Paper White Screen Test ===")
    print("This will display a completely white screen")

    epd = EPD2in7(dc_pin=25, rst_pin=17, busy_pin=24, cs_pin=8)

    try:
        print("\n1. Initializing display...")
        epd.init('full')
        print("   ✓ Display initialized")

        print("\n2. Creating white buffer...")
        # 0xFF = white pixels for e-paper
        # Display is 176 width x 264 height = 46464 pixels = 5808 bytes
        buffer_size = (176 * 264) // 8
        white_buffer = bytes([0xFF] * buffer_size)
        print(f"   ✓ Buffer created: {buffer_size} bytes")

        print("\n3. Sending buffer to display...")
        epd.display_frame(white_buffer)
        print("   ✓ Buffer sent")

        print("\n4. Refreshing display (this takes a few seconds)...")
        epd.refresh('full')
        print("   ✓ Display refreshed")

        print("\n✅ SUCCESS! The screen should now be completely WHITE.")
        print("   If you see white, the hardware is working correctly.")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

    finally:
        print("\n5. Cleaning up...")
        try:
            epd.sleep()
            print("   ✓ Display in sleep mode")
        except:
            pass

if __name__ == "__main__":
    main()
