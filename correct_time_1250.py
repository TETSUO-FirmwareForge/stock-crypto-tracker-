#!/usr/bin/env python3
"""
CORRECT version using official Waveshare V2 buffer logic
Show 12:50 in corner
"""
import sys
from PIL import Image

sys.path.insert(0, '/home/sa/tetsuo-display')
from app.display_driver import EPD2in7

def main():
    print("Creating display driver...")
    epd = EPD2in7()

    print("Creating image 264x176 (horizontal)...")
    # Create image in PIL
    from PIL import ImageDraw, ImageFont
    image = Image.new('1', (264, 176), 255)  # White background
    draw = ImageDraw.Draw(image)

    # Load font
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
    except:
        font = ImageFont.load_default()

    # Draw 12:50 in bottom-right corner
    time_text = "12:50"
    bbox = draw.textbbox((0, 0), time_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x_pos = 264 - text_width - 15
    y_pos = 176 - text_height - 15

    print(f"Drawing '{time_text}' at ({x_pos}, {y_pos})")
    draw.text((x_pos, y_pos), time_text, font=font, fill=0)  # Black text

    # Convert using OFFICIAL Waveshare V2 method
    print("Converting to buffer (Waveshare V2 method)...")

    # Start with all white (0xFF)
    buf = [0xFF] * (int(176 / 8) * 264)

    # Convert image to mono
    image_mono = image.convert('1')
    pixels = image_mono.load()

    # Horizontal orientation (image is 264x176, display is 176x264)
    # We need to rotate: image's 264 width becomes display's 264 height
    imwidth = 264
    imheight = 176
    display_width = 176

    print("Processing pixels...")
    for y in range(imheight):
        for x in range(imwidth):
            # Horizontal transformation
            newx = y
            newy = display_width - x - 1

            # If pixel is BLACK (0), clear the bit
            if pixels[x, y] == 0:
                buf[int((newx + newy * display_width) / 8)] &= ~(0x80 >> (y % 8))

    print(f"Buffer created: {len(buf)} bytes")

    # Send to display
    print("Initializing display...")
    epd.init('full')

    print("Sending buffer...")
    epd.display_frame(bytes(buf))

    print("Refreshing...")
    epd.refresh('full')

    print("✅ DONE!")

    epd.sleep()
    epd.cleanup()

if __name__ == "__main__":
    main()
