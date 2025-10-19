#!/bin/bash
# Complete fix for all indentation errors and display issues

cd ~/tetsuo-lcd

echo "=== Fixing LCD Driver (line 502) ==="
python3 << 'PYFIX1'
with open('app/lcd_driver_st7735.py', 'r') as f:
    lines = f.readlines()

# Fix line 502 - ensure proper indentation (8 spaces for method body)
if len(lines) >= 502:
    line = lines[501]
    lines[501] = '        ' + line.lstrip()
    print(f"Fixed line 502: {repr(line.strip())} -> properly indented")

with open('app/lcd_driver_st7735.py', 'w') as f:
    f.writelines(lines)

print("✓ Driver fixed!")
PYFIX1

echo ""
echo "=== Testing imports ==="
python3 << 'PYTEST'
try:
    from app.lcd_driver_st7735 import ST7735
    print("✓ Driver imports successfully")
except Exception as e:
    print(f"✗ Driver error: {e}")
    exit(1)

try:
    from app.lcd_renderer import LCDRenderer
    print("✓ Renderer imports successfully")
except Exception as e:
    print(f"✗ Renderer error: {e}")
    exit(1)

print("\n✓ All imports working!")
PYTEST

if [ $? -eq 0 ]; then
    echo ""
    echo "=== Starting LCD Monitor ==="
    echo "Display should show:"
    echo "  - Horizontal layout (128x128)"
    echo "  - Colored graphics (not text)"
    echo "  - TETSUO header in top bar"
    echo "  - Price in yellow"
    echo "  - 24h change with colored background"
    echo ""
    sudo python3 main_lcd.py
else
    echo "✗ Import tests failed. Fix errors above before running monitor."
    exit 1
fi
