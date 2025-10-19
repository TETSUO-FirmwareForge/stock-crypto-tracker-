#!/bin/bash
# TETSUO Display - Quick Install Script for Raspberry Pi
# Run this script ON the Raspberry Pi after transferring the project

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════╗"
echo "║         TETSUO Display - Raspberry Pi Installation        ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo "⚠️  Warning: This doesn't appear to be a Raspberry Pi"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Step 1: Update system
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 1: Updating system packages..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git

# Step 2: Check SPI
echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 2: Checking SPI interface..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -e /dev/spidev0.0 ]; then
    echo "✓ SPI is enabled"
else
    echo "✗ SPI is NOT enabled"
    echo
    echo "To enable SPI:"
    echo "  1. Run: sudo raspi-config"
    echo "  2. Navigate to: Interface Options → SPI → Enable"
    echo "  3. Reboot: sudo reboot"
    echo
    read -p "Press Enter to continue (will skip SPI-dependent steps)..."
fi

# Step 3: Create virtual environment
echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 3: Setting up Python environment..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Step 4: Install dependencies
echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 4: Installing Python dependencies..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Dependencies installed"

# Step 5: Copy environment file
echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 5: Setting up environment..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✓ Created .env file (edit if you have API keys)"
else
    echo "✓ .env file already exists"
fi

# Step 6: Run wizard
echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 6: Running setup wizard..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo
read -p "Run interactive setup wizard now? (Y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    python3 scripts/wizard.py
else
    echo "⏭️  Skipping wizard (you can run it later with: python3 scripts/wizard.py)"
fi

# Done
echo
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                   Installation Complete!                   ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo
echo "Next steps:"
echo
echo "  Run setup wizard (if you skipped it):"
echo "    source venv/bin/activate"
echo "    python3 scripts/wizard.py"
echo
echo "  Start service:"
echo "    sudo systemctl start tetsuo-display"
echo
echo "  Check status:"
echo "    sudo systemctl status tetsuo-display"
echo
echo "  View logs:"
echo "    sudo journalctl -u tetsuo-display -f"
echo
echo "Enjoy your TETSUO display! 🚀"
echo
