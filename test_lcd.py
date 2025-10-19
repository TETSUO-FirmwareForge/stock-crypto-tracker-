#!/usr/bin/env python3
"""
Test script for 1.44" ST7735S LCD Display on Raspberry Pi Zero 2
Tests display functionality, colors, and input controls
"""

import sys
import time
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.lcd_driver_st7735 import ST7735, InputHandler
from PIL import Image, ImageDraw, ImageFont


def test_display_init():
    """Test basic display initialization."""
    print("=" * 50)
    print("TEST 1: Display Initialization")
    print("=" * 50)

    lcd = ST7735()

    try:
        print("Initializing LCD...")
        lcd.init()
        print("✓ LCD initialized successfully")

        print("Clearing display to black...")
        lcd.clear(lcd.BLACK)
        time.sleep(1)

        print("✓ Display cleared")
        return lcd

    except Exception as e:
        print(f"✗ Initialization failed: {e}")
        return None


def test_colors(lcd):
    """Test color display."""
    print("\n" + "=" * 50)
    print("TEST 2: Color Display")
    print("=" * 50)

    colors = [
        ("Black", lcd.BLACK),
        ("White", lcd.WHITE),
        ("Red", lcd.RED),
        ("Green", lcd.GREEN),
        ("Blue", lcd.BLUE),
        ("Yellow", lcd.YELLOW),
        ("Cyan", lcd.CYAN),
        ("Magenta", lcd.MAGENTA),
        ("Orange", lcd.ORANGE)
    ]

    for name, color in colors:
        print(f"Testing {name}...")
        lcd.clear(color)
        time.sleep(0.5)

    print("✓ Color test complete")


def test_rectangles(lcd):
    """Test drawing rectangles."""
    print("\n" + "=" * 50)
    print("TEST 3: Rectangle Drawing")
    print("=" * 50)

    lcd.clear(lcd.BLACK)

    # Draw nested rectangles
    colors = [lcd.RED, lcd.GREEN, lcd.BLUE, lcd.YELLOW]
    for i, color in enumerate(colors):
        x = 10 + i * 10
        y = 10 + i * 10
        w = 108 - i * 20
        h = 108 - i * 20

        print(f"Drawing rectangle {i+1}...")
        lcd.fill_rect(x, y, w, h, color)
        time.sleep(0.5)

    print("✓ Rectangle test complete")


def test_image_display(lcd):
    """Test PIL image display."""
    print("\n" + "=" * 50)
    print("TEST 4: Image Display")
    print("=" * 50)

    # Create test image
    img = Image.new('RGB', (128, 128), color='black')
    draw = ImageDraw.Draw(img)

    # Draw gradient
    for y in range(128):
        color = (y * 2, 128 - y, y)
        draw.line([(0, y), (127, y)], fill=color)

    # Add text overlay
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
    except:
        font = ImageFont.load_default()

    draw.text((20, 50), "TETSUO", font=font, fill=(255, 255, 255))
    draw.text((35, 75), "LCD", font=font, fill=(0, 255, 0))

    print("Displaying test image...")
    lcd.display_image(img)
    time.sleep(2)

    print("✓ Image display test complete")


def test_input(lcd, input_handler):
    """Test joystick and button inputs."""
    print("\n" + "=" * 50)
    print("TEST 5: Input Controls")
    print("=" * 50)
    print("Test the controls:")
    print("- Move joystick UP/DOWN/LEFT/RIGHT")
    print("- Press joystick CENTER")
    print("- Press buttons K1, K2, K3")
    print("- Press K3 to exit test")
    print("-" * 50)

    # Create base image
    img = Image.new('RGB', (128, 128), color='black')
    draw = ImageDraw.Draw(img)

    # Title
    draw.text((25, 10), "INPUT TEST", fill='white')
    draw.rectangle([10, 30, 118, 100], outline='gray')

    lcd.display_image(img)

    last_input = None
    exit_test = False

    while not exit_test:
        states = input_handler.read_inputs()

        for name, pressed in states.items():
            if pressed and name != last_input:
                print(f"Input detected: {name}")

                # Update display
                img = Image.new('RGB', (128, 128), color='black')
                draw = ImageDraw.Draw(img)

                draw.text((25, 10), "INPUT TEST", fill='white')
                draw.rectangle([10, 30, 118, 100], outline='gray')

                # Show current input
                color = 'green' if 'k' in name else 'yellow'
                draw.text((30, 55), name.upper(), fill=color)

                # Draw direction indicator
                if name == 'up':
                    draw.polygon([(64, 35), (54, 45), (74, 45)], fill='yellow')
                elif name == 'down':
                    draw.polygon([(64, 95), (54, 85), (74, 85)], fill='yellow')
                elif name == 'left':
                    draw.polygon([(15, 65), (25, 55), (25, 75)], fill='yellow')
                elif name == 'right':
                    draw.polygon([(113, 65), (103, 55), (103, 75)], fill='yellow')
                elif name == 'center':
                    draw.ellipse([59, 60, 69, 70], fill='red')

                lcd.display_image(img)
                last_input = name

                if name == 'k3':
                    exit_test = True
                    print("Exiting input test...")

        time.sleep(0.05)

    print("✓ Input test complete")


def test_price_display(lcd):
    """Test price display layout."""
    print("\n" + "=" * 50)
    print("TEST 6: Price Display Layout")
    print("=" * 50)

    img = Image.new('RGB', (128, 128), color='black')
    draw = ImageDraw.Draw(img)

    # Header
    draw.rectangle([0, 0, 128, 20], fill=(20, 20, 20))
    draw.text((5, 3), "TETSUO/SOL", fill=(0, 150, 255))
    draw.text((90, 3), "LIVE", fill=(0, 255, 0))

    # Price
    draw.text((15, 30), "$0.003456", fill='white')

    # Change
    draw.text((25, 55), "▲ +5.23%", fill=(0, 255, 0))

    # Stats
    draw.text((5, 80), "Vol: $1.23M", fill=(180, 180, 180))
    draw.text((5, 95), "Liq: $456.7K", fill=(180, 180, 180))

    # Footer
    draw.line([(0, 113), (128, 113)], fill=(60, 60, 60))
    draw.text((45, 115), "14:23:45", fill=(180, 180, 180))

    print("Displaying price layout...")
    lcd.display_image(img)
    time.sleep(3)

    print("✓ Price display test complete")


def run_all_tests():
    """Run all LCD tests."""
    print("\n" + "=" * 50)
    print("ST7735S LCD DISPLAY TEST SUITE")
    print("For Raspberry Pi Zero 2")
    print("=" * 50)

    # Initialize
    lcd = test_display_init()
    if not lcd:
        print("\n✗ Cannot proceed without display initialization")
        return False

    input_handler = InputHandler()

    try:
        # Run tests
        test_colors(lcd)
        test_rectangles(lcd)
        test_image_display(lcd)
        test_price_display(lcd)
        test_input(lcd, input_handler)

        print("\n" + "=" * 50)
        print("ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 50)

        # Final message
        img = Image.new('RGB', (128, 128), color='black')
        draw = ImageDraw.Draw(img)
        draw.text((20, 50), "TEST", fill='green')
        draw.text((15, 70), "COMPLETE!", fill='green')
        lcd.display_image(img)
        time.sleep(2)

        return True

    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        return False

    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        print("\nCleaning up...")
        lcd.cleanup()


def quick_test():
    """Quick test to verify basic functionality."""
    print("Running quick LCD test...")

    try:
        lcd = ST7735()
        lcd.init()

        # Show test pattern
        lcd.clear(lcd.BLACK)
        time.sleep(0.5)
        lcd.fill_rect(10, 10, 108, 108, lcd.GREEN)
        time.sleep(0.5)
        lcd.fill_rect(30, 30, 68, 68, lcd.BLUE)
        time.sleep(0.5)
        lcd.fill_rect(50, 50, 28, 28, lcd.RED)
        time.sleep(1)

        print("✓ Quick test successful!")
        lcd.cleanup()
        return True

    except Exception as e:
        print(f"✗ Quick test failed: {e}")
        return False


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Test ST7735S LCD Display')
    parser.add_argument('--quick', action='store_true',
                      help='Run quick test only')
    parser.add_argument('--color', action='store_true',
                      help='Run color test only')
    parser.add_argument('--input', action='store_true',
                      help='Run input test only')

    args = parser.parse_args()

    try:
        if args.quick:
            success = quick_test()
        elif args.color:
            lcd = test_display_init()
            if lcd:
                test_colors(lcd)
                lcd.cleanup()
            success = lcd is not None
        elif args.input:
            lcd = test_display_init()
            if lcd:
                input_handler = InputHandler()
                test_input(lcd, input_handler)
                lcd.cleanup()
            success = lcd is not None
        else:
            success = run_all_tests()

        sys.exit(0 if success else 1)

    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)