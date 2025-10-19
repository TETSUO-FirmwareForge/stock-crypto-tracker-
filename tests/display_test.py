#!/usr/bin/env python3
"""
Hardware display test for TETSUO e-paper.

Tests the e-paper display hardware directly.
Requires Raspberry Pi with display connected.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import Config
from app.display_driver import EPD2in7, HAS_HARDWARE


def main():
    """Run display hardware test."""
    print("TETSUO Display - Hardware Test\n")

    if not HAS_HARDWARE:
        print("✗ Hardware not available")
        print("  This test requires:")
        print("  - Raspberry Pi")
        print("  - RPi.GPIO library")
        print("  - spidev library")
        print("  - E-paper HAT connected")
        sys.exit(1)

    print("This test will:")
    print("  1. Initialize the display")
    print("  2. Clear it to white")
    print("  3. Draw a test pattern")
    print("  4. Clean up")
    print("\nThe display will flash during the test.\n")

    input("Press Enter to start...")

    try:
        config = Config()
        epd = EPD2in7(
            dc_pin=config.get("display.gpio.dc_pin", 25),
            rst_pin=config.get("display.gpio.rst_pin", 17),
            busy_pin=config.get("display.gpio.busy_pin", 24),
            cs_pin=config.get("display.gpio.cs_pin", 8)
        )

        print("\n1. Initializing display...")
        epd.init('full')
        print("   ✓ Initialized")

        print("\n2. Clearing display...")
        epd.clear()
        print("   ✓ Cleared")

        print("\n3. Drawing test pattern...")

        # Create simple test pattern
        from PIL import Image, ImageDraw, ImageFont

        image = Image.new('1', (epd.width, epd.height), 255)
        draw = ImageDraw.Draw(image)

        # Draw border
        draw.rectangle([0, 0, epd.width - 1, epd.height - 1], outline=0, width=2)

        # Draw cross
        draw.line([(epd.width // 2, 0), (epd.width // 2, epd.height)], fill=0, width=1)
        draw.line([(0, epd.height // 2), (epd.width, epd.height // 2)], fill=0, width=1)

        # Draw corners
        size = 20
        draw.rectangle([0, 0, size, size], fill=0)
        draw.rectangle([epd.width - size, 0, epd.width, size], fill=0)
        draw.rectangle([0, epd.height - size, size, epd.height], fill=0)
        draw.rectangle([epd.width - size, epd.height - size, epd.width, epd.height], fill=0)

        # Draw text
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
        except:
            font = ImageFont.load_default()

        draw.text((10, 10), "TETSUO", font=font, fill=0)
        draw.text((10, 40), "Hardware Test", font=font, fill=0)
        draw.text((10, epd.height - 30), "Display OK", font=font, fill=0)

        # Convert to buffer
        rotated = image.rotate(90, expand=True)
        buffer = []
        for y in range(epd.height):
            for x in range(0, epd.width, 8):
                byte = 0
                for bit in range(8):
                    if x + bit < epd.width:
                        pixel = rotated.getpixel((x + bit, y))
                        if pixel == 0:
                            byte |= (0x80 >> bit)
                buffer.append(byte)

        epd.display_frame(bytes(buffer))
        epd.refresh('full')
        print("   ✓ Pattern displayed")

        print("\nCheck the display. You should see:")
        print("  - Border rectangle")
        print("  - Center cross")
        print("  - Black squares in corners")
        print("  - Text labels")

        input("\nPress Enter to clean up...")

        print("\n4. Cleaning up...")
        epd.cleanup()
        print("   ✓ Done")

        print("\n✓ Display test complete!")

    except KeyboardInterrupt:
        print("\n\nTest interrupted")
        try:
            epd.cleanup()
        except:
            pass
        sys.exit(1)

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()

        try:
            epd.cleanup()
        except:
            pass

        sys.exit(1)


if __name__ == "__main__":
    main()
