#!/bin/bash

# Installation script for TETSUO LCD Display on Raspberry Pi Zero 2
# Run this script ON the Raspberry Pi

set -e  # Exit on error

echo "========================================="
echo "TETSUO LCD Display Installation"
echo "For Raspberry Pi Zero 2 + 1.44\" LCD"
echo "========================================="
echo ""

# Check if running as root for GPIO access
if [[ $EUID -eq 0 ]]; then
   echo "Running as root - good for testing"
else
   echo "Note: You may need to use 'sudo' for GPIO access"
fi

# Update system
echo "Step 1: Updating system packages..."
sudo apt update

# Install system dependencies
echo "Step 2: Installing system dependencies..."
sudo apt install -y \
    python3-pip \
    python3-dev \
    python3-pil \
    python3-numpy \
    python3-spidev \
    python3-rpi.gpio \
    fonts-dejavu-core \
    git

# Enable SPI interface
echo "Step 3: Enabling SPI interface..."
if ! grep -q "^dtparam=spi=on" /boot/config.txt; then
    echo "dtparam=spi=on" | sudo tee -a /boot/config.txt
    echo "SPI enabled in /boot/config.txt"
    SPI_ENABLED=true
else
    echo "SPI already enabled"
    SPI_ENABLED=false
fi

# Install Python packages
echo "Step 4: Installing Python packages..."
pip3 install --user \
    requests \
    pyyaml \
    pillow \
    numpy

# Set up directory structure
echo "Step 5: Setting up directory structure..."
INSTALL_DIR="/home/pi/tetsuo-lcd"
cd $INSTALL_DIR

# Create necessary directories
mkdir -p data
mkdir -p logs
mkdir -p app

# Create __init__.py if not exists
touch app/__init__.py

# Set permissions
echo "Step 6: Setting permissions..."
chmod +x main_lcd.py
chmod +x test_lcd.py
chmod +x deploy_to_pi_lcd.sh 2>/dev/null || true

# Add user to necessary groups
echo "Step 7: Adding user to GPIO and SPI groups..."
sudo usermod -a -G gpio,spi $USER

# Test SPI availability
echo "Step 8: Checking SPI devices..."
if ls /dev/spidev* 1> /dev/null 2>&1; then
    echo "✓ SPI devices found:"
    ls /dev/spidev*
else
    echo "⚠ No SPI devices found. You may need to reboot."
fi

# Create systemd service
echo "Step 9: Installing systemd service..."
if [ -f "tetsuo-lcd.service" ]; then
    sudo cp tetsuo-lcd.service /etc/systemd/system/
    sudo systemctl daemon-reload
    echo "✓ Systemd service installed"
    echo "  To enable auto-start: sudo systemctl enable tetsuo-lcd"
    echo "  To start service: sudo systemctl start tetsuo-lcd"
else
    echo "⚠ Service file not found"
fi

# Create log file
echo "Step 10: Creating log file..."
touch tetsuo_lcd.log
chmod 666 tetsuo_lcd.log

echo ""
echo "========================================="
echo "Installation Complete!"
echo "========================================="
echo ""

# Test basic functionality
echo "Testing basic imports..."
python3 -c "
try:
    import RPi.GPIO as GPIO
    print('✓ RPi.GPIO imported successfully')
except ImportError as e:
    print('✗ RPi.GPIO import failed:', e)

try:
    import spidev
    print('✓ spidev imported successfully')
except ImportError as e:
    print('✗ spidev import failed:', e)

try:
    from PIL import Image
    print('✓ PIL imported successfully')
except ImportError as e:
    print('✗ PIL import failed:', e)

try:
    import yaml
    print('✓ yaml imported successfully')
except ImportError as e:
    print('✗ yaml import failed:', e)

try:
    import requests
    print('✓ requests imported successfully')
except ImportError as e:
    print('✗ requests import failed:', e)
"

echo ""
echo "========================================="
echo "Next Steps:"
echo "========================================="
echo ""

if [ "$SPI_ENABLED" = true ]; then
    echo "⚠ IMPORTANT: SPI was just enabled. You need to REBOOT!"
    echo "  Run: sudo reboot"
    echo ""
fi

echo "1. Test the LCD display:"
echo "   sudo python3 test_lcd.py --quick"
echo ""
echo "2. Run full test suite:"
echo "   sudo python3 test_lcd.py"
echo ""
echo "3. Start the price monitor:"
echo "   sudo python3 main_lcd.py"
echo ""
echo "4. Enable auto-start on boot (optional):"
echo "   sudo systemctl enable tetsuo-lcd"
echo "   sudo systemctl start tetsuo-lcd"
echo ""
echo "5. View logs:"
echo "   tail -f tetsuo_lcd.log"
echo ""

if ! groups | grep -q "\bgpio\b"; then
    echo "⚠ NOTE: You may need to logout and login again for GPIO group access"
fi

echo "========================================="
echo "Happy monitoring! 🚀"
echo "========================================="