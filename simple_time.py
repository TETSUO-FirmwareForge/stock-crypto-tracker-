#!/usr/bin/env python3
"""
Simple time display - ONE time only, thicker text
"""
import sys
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, '/home/sa/tetsuo-display')
from app.display_driver import EPD2in7

def main():
    print("Initializing display...")
    epd = EPD2in7()
    epd.init('full')

    # Create white image
    image = Image.new('1', (264, 176), 255)  # White background
    draw = ImageDraw.Draw(image)

    # Load font - size 28 for good visibility
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
    except:
        font = ImageFont.load_default()

    # Get current time
    now = datetime.now()
    time_text = now.strftime("%H:%M")

    print(f"Time to display: {time_text}")

    # Position in bottom-right corner
    bbox = draw.textbbox((0, 0), time_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x_pos = 264 - text_width - 10
    y_pos = 176 - text_height - 10

    print(f"Position: x={x_pos}, y={y_pos}")

    # Draw text ONLY ONCE but with stroke to make it thicker
    draw.text((x_pos, y_pos), time_text, font=font, fill=0, stroke_width=2, stroke_fill=0)

    print("Converting to buffer...")

    # Convert to buffer - use different variable names to avoid confusion
    buffer = []
    for row in range(176):
        for col in range(0, 264, 8):
            byte = 0
            for bit_pos in range(8):
                if col + bit_pos < 264:
                    pixel_value = image.getpixel((col + bit_pos, row))
                    # V2: BLACK pixel (0) -> bit 0, WHITE pixel (255) -> bit 1
                    # So we need to set bit for WHITE, leave 0 for BLACK
                    if pixel_value != 0:  # If NOT black (i.e., white)
                        byte |= (0x80 >> bit_pos)
            buffer.append(byte)

    print(f"Buffer size: {len(buffer)} bytes (expected: 5808)")

    # Display
    print("Sending to display...")
    epd.display_frame(bytes(buffer))
    epd.refresh('full')

    print("Done!")

    epd.sleep()
    epd.cleanup()

if __name__ == "__main__":
    main()
