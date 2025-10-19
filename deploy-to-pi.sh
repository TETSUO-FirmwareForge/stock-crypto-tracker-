#!/bin/bash
# TETSUO Display - Deploy to Raspberry Pi (Run from Mac)

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║       TETSUO Display - Deploy to Raspberry Pi             ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo

# Ask for Raspberry Pi IP and username
echo "Enter Raspberry Pi IP address:"
read -p "IP: " PI_IP
read -p "Username [sa]: " PI_USER
PI_USER=${PI_USER:-sa}

if [ -z "$PI_IP" ]; then
    echo "❌ No IP provided. Exiting."
    exit 1
fi

echo
echo "Using IP: $PI_IP"
echo "Username: $PI_USER"
echo

# Test connection
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Testing connection to Raspberry Pi..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if ! ping -c 1 -W 2 $PI_IP > /dev/null 2>&1; then
    echo "⚠️  Warning: Cannot ping $PI_IP"
    echo "Make sure your Raspberry Pi is:"
    echo "  1. Powered on"
    echo "  2. Connected to the same network"
    echo "  3. SSH is enabled"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Transfer project
echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 1: Transferring project to Raspberry Pi..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo
echo "Copying files (you'll be asked for your SSH password)..."
echo

scp -r ~/Desktop/tetsuo-display/ $PI_USER@$PI_IP:~/

echo
echo "✅ Files transferred successfully!"

# Connect and install
echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 2: Installing on Raspberry Pi..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo
read -p "Run automatic installation on Pi? (Y/n): " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    echo
    echo "Connecting to Pi and running installation..."
    echo "(You may be asked for your SSH password again)"
    echo

    ssh $PI_USER@$PI_IP "cd ~/tetsuo-display && bash install.sh"

    echo
    echo "✅ Installation complete!"
else
    echo
    echo "Skipping automatic installation."
    echo "To install manually, connect to your Pi:"
    echo
    echo "  ssh pi@$PI_IP"
    echo "  cd ~/tetsuo-display"
    echo "  ./install.sh"
fi

# Final instructions
echo
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                  Deployment Complete!                      ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo
echo "To connect to your Raspberry Pi:"
echo "  ssh $PI_USER@$PI_IP"
echo
echo "To check the display service:"
echo "  ssh $PI_USER@$PI_IP 'sudo systemctl status tetsuo-display'"
echo
echo "To view live logs:"
echo "  ssh $PI_USER@$PI_IP 'sudo journalctl -u tetsuo-display -f'"
echo
echo "🎉 Your TETSUO display should now be running!"
echo
