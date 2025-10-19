#!/bin/bash

# ============================================
# SCRIPT PARA EJECUTAR EN TU RASPBERRY PI
# ============================================
#
# INSTRUCCIONES:
# 1. Enciende tu Raspberry Pi Zero 2
# 2. Conéctate por SSH o directamente
# 3. Copia y ejecuta estos comandos
# ============================================

echo "========================================="
echo "TETSUO LCD - Instalación Completa"
echo "========================================="

# Establecer variables
INSTALL_DIR="$HOME/tetsuo-lcd"
MAC_IP="127.160.126.170"  # Cambia esto por la IP de tu Mac si es diferente

# Crear directorio
echo "Creando directorio de instalación..."
mkdir -p $INSTALL_DIR
cd $INSTALL_DIR

# Descargar el paquete
echo "Descargando archivos..."
if command -v wget &> /dev/null; then
    wget http://$MAC_IP:8888/tetsuo-lcd.tar.gz
elif command -v curl &> /dev/null; then
    curl -O http://$MAC_IP:8888/tetsuo-lcd.tar.gz
else
    echo "ERROR: Necesitas wget o curl"
    echo "Instala con: sudo apt install wget"
    exit 1
fi

# Verificar descarga
if [ ! -f "tetsuo-lcd.tar.gz" ]; then
    echo "ERROR: No se pudo descargar el archivo"
    echo "Verifica que el servidor HTTP esté activo en tu Mac"
    echo "En tu Mac ejecuta: python3 -m http.server 8888"
    exit 1
fi

# Extraer archivos
echo "Extrayendo archivos..."
tar xzf tetsuo-lcd.tar.gz

# Crear directorios necesarios
mkdir -p data logs

# Dar permisos
chmod +x *.py *.sh 2>/dev/null || true

# Instalar dependencias del sistema
echo ""
echo "Instalando dependencias del sistema..."
sudo apt update
sudo apt install -y \
    python3-pip \
    python3-pil \
    python3-spidev \
    python3-rpi.gpio \
    python3-numpy \
    fonts-dejavu-core

# Instalar librerías Python
echo ""
echo "Instalando librerías Python..."
pip3 install --user requests pyyaml pillow numpy

# Habilitar SPI
echo ""
echo "Habilitando interfaz SPI..."
sudo raspi-config nonint do_spi 0

# Verificar SPI
if ls /dev/spidev* 1> /dev/null 2>&1; then
    echo "✓ Dispositivos SPI encontrados:"
    ls /dev/spidev*
else
    echo "⚠ No se encontraron dispositivos SPI"
    echo "  Puede que necesites reiniciar"
fi

# Test rápido del display
echo ""
echo "========================================="
echo "PROBANDO EL DISPLAY LCD"
echo "========================================="

sudo python3 << 'EOF'
import sys
sys.path.append('.')

try:
    from app.lcd_driver_st7735 import ST7735

    print("Inicializando LCD...")
    lcd = ST7735()
    lcd.init()

    print("Mostrando colores de prueba...")
    print("ROJO...")
    lcd.clear(lcd.RED)
    import time
    time.sleep(1)

    print("VERDE...")
    lcd.clear(lcd.GREEN)
    time.sleep(1)

    print("AZUL...")
    lcd.clear(lcd.BLUE)
    time.sleep(1)

    print("BLANCO...")
    lcd.clear(lcd.WHITE)
    time.sleep(1)

    lcd.cleanup()
    print("✓✓✓ TEST EXITOSO ✓✓✓")

except Exception as e:
    print(f"Error en test: {e}")
    print("Ejecuta: sudo python3 test_lcd.py --quick")
EOF

echo ""
echo "========================================="
echo "INICIANDO MONITOR DE PRECIOS TETSUO"
echo "========================================="
echo ""
echo "El display LCD mostrará:"
echo "  • Precio de TETSUO en USD"
echo "  • Cambio 24h (verde=sube, rojo=baja)"
echo "  • Volumen y liquidez"
echo "  • Gráfico de precios"
echo ""
echo "Usa el joystick para navegar entre vistas"
echo "========================================="
echo ""

# Ejecutar la aplicación
sudo python3 main_lcd.py

echo ""
echo "========================================="
echo "Para ejecutar en segundo plano:"
echo "  nohup sudo python3 main_lcd.py &"
echo ""
echo "Para instalación permanente:"
echo "  sudo cp tetsuo-lcd.service /etc/systemd/system/"
echo "  sudo systemctl enable tetsuo-lcd"
echo "  sudo systemctl start tetsuo-lcd"
echo "========================================="