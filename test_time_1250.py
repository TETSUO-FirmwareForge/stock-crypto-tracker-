#!/usr/bin/env python3
"""
Test: Show 12:50 in corner - horizontal orientation (264x176)
"""
import sys
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, '/home/sa/tetsuo-display')
from app.display_driver import EPD2in7

def main():
    print("Creating image...")

    # Horizontal orientation: 264 width x 176 height
    image = Image.new('1', (264, 176), 255)  # White background
    draw = ImageDraw.Draw(image)

    # Load font
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
    except:
        print("Using default font")
        font = ImageFont.load_default()

    # Fixed time: 12:50
    time_text = "12:50"

    # Get text size
    bbox = draw.textbbox((0, 0), time_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Position in bottom-right corner
    x_pos = 264 - text_width - 15
    y_pos = 176 - text_height - 15

    print(f"Drawing '{time_text}' at position ({x_pos}, {y_pos})")
    print(f"Text size: {text_width}x{text_height}")

    # Draw text in BLACK (fill=0)
    draw.text((x_pos, y_pos), time_text, font=font, fill=0)

    # Convert to buffer
    print("Converting to buffer...")
    buffer = []

    for row in range(176):
        for col in range(0, 264, 8):
            byte = 0
            for bit in range(8):
                pixel_col = col + bit
                if pixel_col < 264:
                    pixel = image.getpixel((pixel_col, row))
                    # If pixel is WHITE (255), set bit to 1
                    # If pixel is BLACK (0), leave bit as 0
                    if pixel == 255:
                        byte |= (0x80 >> bit)
            buffer.append(byte)

    print(f"Buffer created: {len(buffer)} bytes")

    # Send to display
    print("Initializing display...")
    epd = EPD2in7()
    epd.init('full')

    print("Sending buffer...")
    epd.display_frame(bytes(buffer))

    print("Refreshing...")
    epd.refresh('full')

    print("✅ DONE!")

    epd.sleep()
    epd.cleanup()

if __name__ == "__main__":
    main()
