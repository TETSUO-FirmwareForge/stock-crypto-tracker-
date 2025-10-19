#!/usr/bin/env python3
"""
Show time in bottom-right corner with smaller numbers
"""
import sys
import time
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

    # Load smaller font
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
    except:
        font = ImageFont.load_default()

    # Get current time
    now = datetime.now()
    time_text = now.strftime("%H:%M")

    # Position in bottom-right corner
    bbox = draw.textbbox((0, 0), time_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x_pos = 264 - text_width - 10  # 10 pixels from right edge
    y_pos = 176 - text_height - 10  # 10 pixels from bottom edge

    # Draw text multiple times to make it thicker/darker
    draw.text((x_pos, y_pos), time_text, font=font, fill=0)
    draw.text((x_pos+1, y_pos), time_text, font=font, fill=0)
    draw.text((x_pos, y_pos+1), time_text, font=font, fill=0)
    draw.text((x_pos+1, y_pos+1), time_text, font=font, fill=0)

    print(f"Displaying: {time_text} at position ({x_pos}, {y_pos})")

    # Convert to buffer
    buffer = []
    for y in range(176):
        for x in range(0, 264, 8):
            byte = 0
            for bit in range(8):
                if x + bit < 264:
                    pixel = image.getpixel((x + bit, y))
                    # V2: white pixel (255) -> bit 1
                    if pixel == 255:
                        byte |= (0x80 >> bit)
            buffer.append(byte)

    # Display
    epd.display_frame(bytes(buffer))
    epd.refresh('full')

    print("Done!")

    epd.sleep()
    epd.cleanup()

if __name__ == "__main__":
    main()
