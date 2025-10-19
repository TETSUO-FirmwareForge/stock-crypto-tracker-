#!/bin/bash

# Deploy script for TETSUO LCD Display to Raspberry Pi Zero 2
# This script copies files and sets up the LCD display system

set -e  # Exit on error

# Configuration
PI_USER="pi"
PI_HOST="192.168.2.209"  # Update with your Pi's IP
PI_PASSWORD="5157"
REMOTE_DIR="/home/pi/tetsuo-lcd"

echo "========================================="
echo "TETSUO LCD Display Deployment Script"
echo "========================================="

# Check if sshpass is installed
if ! command -v sshpass &> /dev/null; then
    echo "Installing sshpass..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install hudochenkov/sshpass/sshpass
    else
        sudo apt-get install -y sshpass
    fi
fi

echo "Target: $PI_USER@$PI_HOST:$REMOTE_DIR"
echo ""

# Create remote directory
echo "Creating remote directory..."
sshpass -p "$PI_PASSWORD" ssh -o StrictHostKeyChecking=no $PI_USER@$PI_HOST "mkdir -p $REMOTE_DIR"

# Copy files to Raspberry Pi
echo "Copying files to Raspberry Pi..."
sshpass -p "$PI_PASSWORD" scp -o StrictHostKeyChecking=no -r \
    app/lcd_driver_st7735.py \
    app/lcd_renderer.py \
    app/config.py \
    app/data_fetcher.py \
    app/cache.py \
    main_lcd.py \
    config_lcd.yaml \
    test_lcd.py \
    requirements.txt \
    tetsuo-lcd.service \
    README_LCD.md \
    $PI_USER@$PI_HOST:$REMOTE_DIR/

# Create app directory on Pi
echo "Setting up directory structure..."
sshpass -p "$PI_PASSWORD" ssh -o StrictHostKeyChecking=no $PI_USER@$PI_HOST << 'EOF'
    cd /home/pi/tetsuo-lcd
    mkdir -p app
    mkdir -p data

    # Move app files
    mv lcd_driver_st7735.py app/ 2>/dev/null || true
    mv lcd_renderer.py app/ 2>/dev/null || true
    mv config.py app/ 2>/dev/null || true
    mv data_fetcher.py app/ 2>/dev/null || true
    mv cache.py app/ 2>/dev/null || true

    # Create __init__.py
    touch app/__init__.py

    echo "Directory structure created"
EOF

echo "Files deployed successfully!"
echo ""

# Optional: Run installation on Pi
read -p "Do you want to run the installation script on the Pi? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Running installation on Raspberry Pi..."
    sshpass -p "$PI_PASSWORD" ssh -o StrictHostKeyChecking=no $PI_USER@$PI_HOST "cd $REMOTE_DIR && bash install_lcd.sh"
fi

echo ""
echo "========================================="
echo "Deployment complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. SSH into your Pi: ssh $PI_USER@$PI_HOST"
echo "2. Navigate to: cd $REMOTE_DIR"
echo "3. Run installation: sudo bash install_lcd.sh"
echo "4. Test display: sudo python3 test_lcd.py"
echo "5. Run application: sudo python3 main_lcd.py"