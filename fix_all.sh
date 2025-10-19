#!/bin/bash

# Fix ALL SPI issues in the LCD driver

cat << 'FULLFIX' > /tmp/complete_fix.py
#!/usr/bin/env python3

# Read the current driver
with open('app/lcd_driver_st7735.py', 'r') as f:
    lines = f.readlines()

# Find and fix the write_data_bulk method
fixed_lines = []
for i, line in enumerate(lines):
    fixed_lines.append(line)

    # Add fixed write_data_bulk after the original
    if 'def write_data_bulk(self, data):' in line:
        # Skip original implementation
        j = i + 1
        while j < len(lines) and lines[j].startswith('        '):
            j += 1

        # Insert fixed version
        fixed_lines.extend([
            '        """Write multiple data bytes to display."""\n',
            '        if not HAS_HARDWARE:\n',
            '            return\n',
            '\n',
            '        GPIO.output(self.cs_pin, GPIO.LOW)\n',
            '        GPIO.output(self.dc_pin, GPIO.HIGH)\n',
            '        \n',
            '        # Send data in chunks to avoid SPI buffer overflow\n',
            '        if isinstance(data, bytes):\n',
            '            data = list(data)\n',
            '        \n',
            '        chunk_size = 4096\n',
            '        for i in range(0, len(data), chunk_size):\n',
            '            chunk = data[i:i+chunk_size]\n',
            '            self.spi.writebytes(chunk)\n',
            '        \n',
            '        GPIO.output(self.cs_pin, GPIO.HIGH)\n',
            '\n'
        ])

        # Skip original lines
        while i < j - 1:
            i += 1
            if i < len(lines):
                fixed_lines.pop()  # Remove the original lines we added

# Write the fixed driver
with open('app/lcd_driver_st7735.py', 'w') as f:
    f.writelines(fixed_lines)

print("Driver fixed!")

# Now fix display_image method specifically
with open('app/lcd_driver_st7735.py', 'r') as f:
    content = f.read()

# Fix display_image to send in chunks
import re

display_image_fix = '''    def display_image(self, image):
        """
        Display PIL image on LCD.
        Image should be 128x128 RGB.
        """
        if not HAS_HARDWARE:
            return

        # Convert image to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Resize if needed
        if image.size != (self.width, self.height):
            image = image.resize((self.width, self.height), Image.LANCZOS)

        # Convert to RGB565 format
        pixels = np.array(image)
        rgb565 = self.rgb888_to_rgb565(pixels)

        # Set window to full screen
        self.set_window(0, 0, self.width-1, self.height-1)

        # Write image data in chunks
        rgb565_bytes = rgb565.tobytes()
        chunk_size = 4096
        for i in range(0, len(rgb565_bytes), chunk_size):
            chunk = rgb565_bytes[i:i+chunk_size]
            self.write_data_bulk(chunk)'''

pattern = r'def display_image\(self.*?\n(?:.*?\n)*?.*?self\.write_data_bulk\([^)]+\)'
content = re.sub(pattern, display_image_fix.strip(), content, flags=re.DOTALL)

# Add cleanup method if missing
if 'def cleanup(' not in content:
    # Find the end of the class (before main or at end of file)
    insert_pos = content.rfind('\n\nclass InputHandler')
    if insert_pos == -1:
        insert_pos = content.rfind('\n\ndef main(')
    if insert_pos == -1:
        insert_pos = len(content) - 1

    cleanup_method = '''
    def cleanup(self):
        """Clean up GPIO and SPI resources."""
        if not HAS_HARDWARE:
            return

        self.clear()
        self.set_backlight(False)

        if self.spi:
            self.spi.close()

        GPIO.cleanup()
'''
    content = content[:insert_pos] + cleanup_method + content[insert_pos:]

with open('app/lcd_driver_st7735.py', 'w') as f:
    f.write(content)

print("All fixes applied!")
FULLFIX

cd ~/tetsuo-lcd
python3 /tmp/complete_fix.py

# Test the fixed driver
echo "Testing fixed driver..."
sudo python3 -c "
import sys
sys.path.append('.')
from app.lcd_driver_st7735 import ST7735

lcd = ST7735()
lcd.init()
print('LCD initialized')

# Simple color test
lcd.clear(0xF800)  # Red
print('Red displayed')

import time
time.sleep(1)

lcd.clear(0x07E0)  # Green
print('Green displayed')

time.sleep(1)

lcd.clear(0x001F)  # Blue
print('Blue displayed')

time.sleep(1)

lcd.cleanup()
print('Test complete!')
"

# If test passed, run the main app
if [ $? -eq 0 ]; then
    echo ""
    echo "========================================="
    echo "STARTING TETSUO PRICE MONITOR"
    echo "========================================="
    sudo python3 main_lcd.py
else
    echo "Test failed. Checking error..."
fi