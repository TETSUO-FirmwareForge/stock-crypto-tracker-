#!/usr/bin/env python3
"""
Ultra smooth clock - minimal flashing using FAST mode
NO reinitialization between updates
"""
import sys
import time
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, '/home/sa/tetsuo-display')
from app.display_driver import EPD2in7

def create_time_image(time_text, font):
    """Create image with time text"""
    image = Image.new('1', (176, 264), 255)
    draw = ImageDraw.Draw(image)

    bbox = draw.textbbox((0, 0), time_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x_pos = (176 - text_width) // 2
    y_pos = 264 - text_height - 10

    draw.text((x_pos, y_pos), time_text, font=font, fill=0)

    return image

def image_to_buffer(image):
    """Convert image to buffer"""
    buf = [0xFF] * (int(176 / 8) * 264)
    image_mono = image.convert('1')
    pixels = image_mono.load()

    for y in range(264):
        for x in range(176):
            if pixels[x, y] == 0:
                buf[int((x + y * 176) / 8)] &= ~(0x80 >> (x % 8))

    return bytes(buf)

def main():
    print("Starting ultra smooth clock (FAST mode)...")

    # Initialize display ONCE
    epd = EPD2in7()
    epd.init('full')

    # Load font
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
    except:
        font = ImageFont.load_default()

    # Initial display
    now = datetime.now()
    time_text = now.strftime("%H:%M")
    print(f"Initial time: {time_text}")

    image = create_time_image(time_text, font)
    buffer = image_to_buffer(image)
    epd.display_frame(buffer)
    epd.refresh('full')

    last_minute = now.minute
    update_count = 0

    try:
        while True:
            now = datetime.now()
            current_minute = now.minute

            if current_minute != last_minute:
                time_text = now.strftime("%H:%M")

                image = create_time_image(time_text, font)
                buffer = image_to_buffer(image)

                # Use FAST mode for updates (0xC7)
                update_count += 1

                if update_count >= 30:  # Full refresh every 30 minutes
                    print(f"{time_text} (full)")
                    epd.refresh('full')
                    update_count = 0
                else:
                    print(f"{time_text} (fast)")

                # Send buffer
                epd.display_frame(buffer)

                # Use FAST refresh (0xC7) - faster than partial
                epd.send_command(0x22)
                epd.send_data(0xC7)  # FAST mode
                epd.send_command(0x20)
                epd.wait_until_idle()

                last_minute = current_minute

            time.sleep(10)

    except KeyboardInterrupt:
        print("\nStopping...")
        epd.sleep()
        epd.cleanup()

if __name__ == "__main__":
    main()
