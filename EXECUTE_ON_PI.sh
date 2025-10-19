#!/bin/bash

# ========================================
# EJECUTA ESTE SCRIPT EN TU RASPBERRY PI
# ========================================

cd ~/tetsuo-lcd

# Crear el script de arreglo
cat > fix_driver.py << 'ENDSCRIPT'
#!/usr/bin/env python3
import sys

# Leer el archivo del driver
file_path = 'app/lcd_driver_st7735.py'

with open(file_path, 'r') as f:
    lines = f.readlines()

# Buscar y reemplazar la función fill_rect
new_lines = []
in_fill_rect = False
skip_until_next_def = False

for i, line in enumerate(lines):
    if 'def fill_rect(self' in line:
        in_fill_rect = True
        skip_until_next_def = True
        # Agregar la nueva versión de la función
        new_lines.append('''    def fill_rect(self, x, y, w, h, color):
        """Fill rectangle with color."""
        if not HAS_HARDWARE:
            return

        # Set window
        self.set_window(x, y, x+w-1, y+h-1)

        # Prepare color bytes
        color_high = (color >> 8) & 0xFF
        color_low = color & 0xFF

        # Send data in chunks to avoid SPI buffer overflow
        total_pixels = w * h
        chunk_size = 256  # Send 256 pixels at a time

        for i in range(0, total_pixels, chunk_size):
            pixels_to_send = min(chunk_size, total_pixels - i)
            data = []
            for _ in range(pixels_to_send):
                data.append(color_high)
                data.append(color_low)
            self.write_data_bulk(data)

''')
    elif skip_until_next_def:
        # Skip lines until we find the next function
        if line.strip() and not line.startswith(' ') and not line.startswith('\t'):
            skip_until_next_def = False
            new_lines.append(line)
        elif 'def ' in line and not in_fill_rect:
            skip_until_next_def = False
            in_fill_rect = False
            new_lines.append(line)
    else:
        new_lines.append(line)

# Escribir el archivo corregido
with open(file_path, 'w') as f:
    f.writelines(new_lines)

print("Driver fixed successfully!")
ENDSCRIPT

# Ejecutar el arreglo
echo "Fixing driver..."
python3 fix_driver.py

# Probar el LCD
echo ""
echo "Testing LCD display..."
sudo python3 << 'TESTSCRIPT'
import sys
sys.path.append('.')

try:
    from app.lcd_driver_st7735 import ST7735

    print("Initializing LCD...")
    lcd = ST7735()
    lcd.init()

    print("Testing colors...")

    # Test with smaller rectangles first
    print("Drawing small red square...")
    lcd.fill_rect(50, 50, 28, 28, 0xF800)  # Red

    import time
    time.sleep(1)

    print("Drawing small green square...")
    lcd.fill_rect(60, 60, 28, 28, 0x07E0)  # Green

    time.sleep(1)

    print("Drawing small blue square...")
    lcd.fill_rect(70, 70, 28, 28, 0x001F)  # Blue

    time.sleep(1)

    print("Clearing to black...")
    lcd.clear(0x0000)

    time.sleep(0.5)

    print("Clearing to white...")
    lcd.clear(0xFFFF)

    lcd.cleanup()
    print("\n✓ LCD test successful!")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
TESTSCRIPT

# Si el test funcionó, ejecutar el monitor
echo ""
echo "========================================"
echo "Starting TETSUO Price Monitor"
echo "========================================"
echo ""

sudo python3 main_lcd.py