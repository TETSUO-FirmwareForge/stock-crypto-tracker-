# TETSUO LCD Display - Raspberry Pi Zero 2

Sistema de monitoreo de precio de TETSUO para display LCD de 1.44" (128x128 píxeles) con controlador ST7735S.

## 📟 Hardware Requerido

- **Raspberry Pi Zero 2 W**
- **Display LCD 1.44" ST7735S** (128x128 píxeles, 65K colores)
- **Conexiones SPI** y GPIO
- **Joystick y botones** integrados en el módulo LCD

## 🔌 Conexiones GPIO

### Pines del Display LCD
| Función | Pin GPIO (BCM) | Pin Físico |
|---------|---------------|------------|
| VCC     | 3.3V          | Pin 1      |
| GND     | GND           | Pin 6      |
| DIN/MOSI| GPIO 10       | Pin 19     |
| CLK     | GPIO 11       | Pin 23     |
| CS      | GPIO 8        | Pin 24     |
| DC      | GPIO 25       | Pin 22     |
| RST     | GPIO 17       | Pin 11     |
| BL      | GPIO 24       | Pin 18     |

### Pines del Joystick y Botones
| Control   | Pin GPIO (BCM) | Pin Físico |
|-----------|---------------|------------|
| Joy UP    | GPIO 6        | Pin 31     |
| Joy DOWN  | GPIO 19       | Pin 35     |
| Joy LEFT  | GPIO 5        | Pin 29     |
| Joy RIGHT | GPIO 26       | Pin 37     |
| Joy CENTER| GPIO 13       | Pin 33     |
| Button K1 | GPIO 21       | Pin 40     |
| Button K2 | GPIO 20       | Pin 38     |
| Button K3 | GPIO 16       | Pin 36     |

## 🛠️ Instalación

### 1. Preparar Raspberry Pi Zero 2

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependencias
sudo apt install -y python3-pip python3-dev python3-pil python3-numpy
sudo apt install -y python3-spidev python3-rpi.gpio
sudo apt install -y fonts-dejavu-core

# Habilitar SPI
sudo raspi-config
# Ir a: Interface Options -> SPI -> Enable
```

### 2. Instalar librerías Python

```bash
cd /home/pi
git clone https://github.com/yourusername/tetsuo-display.git
cd tetsuo-display

# Instalar dependencias Python
pip3 install -r requirements.txt
```

### 3. Configurar el display

```bash
# Editar configuración
nano config_lcd.yaml
```

Ajusta los pines GPIO si es necesario según tu conexión.

## 🚀 Uso

### Test Rápido del Display

```bash
# Test completo
sudo python3 test_lcd.py

# Test rápido
sudo python3 test_lcd.py --quick

# Test de colores
sudo python3 test_lcd.py --color

# Test de controles
sudo python3 test_lcd.py --input
```

### Ejecutar el Monitor de Precios

```bash
# Ejecutar normalmente
sudo python3 main_lcd.py

# Ejecutar con debug
sudo python3 main_lcd.py --debug

# Ejecutar con configuración personalizada
sudo python3 main_lcd.py --config mi_config.yaml
```

## 🎮 Controles

### Navegación con Joystick
- **Izquierda/Derecha**: Cambiar entre vistas (Precio → Estadísticas → Gráfico)
- **Arriba/Abajo**: Ajustar brillo del display
- **Centro**: (Reservado para futuras funciones)

### Botones
- **K1**: (Reservado)
- **K2**: (Reservado)
- **K3**: Salir/Menú

## 📊 Vistas del Display

### Vista 1: Precio Principal
- Símbolo del token (TETSUO)
- Precio actual en USD
- Cambio 24h con indicador de color (verde/rojo)
- Volumen y liquidez resumidos
- Hora de actualización

### Vista 2: Estadísticas Detalladas
- Precio completo con más decimales
- Cambio porcentual 24h
- Volumen 24h
- Liquidez total
- FDV (Fully Diluted Valuation)
- Fuente de datos

### Vista 3: Gráfico de Precios
- Gráfico de línea con últimos 30 puntos
- Precio máximo y mínimo del período
- Indicadores de tendencia con colores

## 🎨 Características del LCD

- **Resolución**: 128x128 píxeles
- **Colores**: 65,536 colores (RGB565)
- **Refresco**: Hasta 60 FPS
- **Backlight**: Ajustable
- **Ángulo de visión**: 160°

## 🔧 Configuración Avanzada

### Personalizar Colores

Edita `config_lcd.yaml`:

```yaml
lcd:
  colors:
    price_up: green     # Color cuando sube
    price_down: red     # Color cuando baja
    background: black   # Fondo
    text_primary: white # Texto principal
    accent: blue       # Acentos
```

### Ajustar Frecuencia de Actualización

```yaml
poll:
  interval_seconds: 5  # Actualizar cada 5 segundos

refresh:
  fps: 10  # Frames por segundo para animaciones
```

### Auto-rotación de Vistas

```yaml
display:
  auto_rotate: true           # Activar rotación automática
  rotation_interval: 10       # Segundos entre cambios
```

## 🐛 Solución de Problemas

### Display no se enciende
1. Verificar conexiones de alimentación (3.3V y GND)
2. Comprobar pin de backlight (GPIO 24)
3. Verificar que SPI esté habilitado

### Display muestra basura
1. Verificar conexiones SPI (MOSI, CLK, CS)
2. Comprobar velocidad SPI en config
3. Verificar pin DC (Data/Command)

### Joystick/Botones no responden
1. Verificar conexiones de pines de entrada
2. Comprobar configuración de pull-up en código
3. Test individual con `test_lcd.py --input`

### Errores de permisos
```bash
# Agregar usuario al grupo gpio y spi
sudo usermod -a -G gpio,spi $USER
# Reiniciar o reloguear
```

## 📝 Logs

Los logs se guardan en:
- `tetsuo_lcd.log` - Log principal
- `data/last_snapshot.json` - Último dato cacheado

Ver logs en tiempo real:
```bash
tail -f tetsuo_lcd.log
```

## 🚀 Ejecutar al Inicio (systemd)

```bash
# Copiar servicio
sudo cp tetsuo-lcd.service /etc/systemd/system/

# Habilitar servicio
sudo systemctl enable tetsuo-lcd.service

# Iniciar servicio
sudo systemctl start tetsuo-lcd.service

# Ver estado
sudo systemctl status tetsuo-lcd.service
```

## 📋 Archivo de Servicio

Crear `/etc/systemd/system/tetsuo-lcd.service`:

```ini
[Unit]
Description=TETSUO LCD Price Display
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/tetsuo-display
ExecStart=/usr/bin/python3 /home/pi/tetsuo-display/main_lcd.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## 🎯 Características Principales

- ✅ Display a color de alta resolución
- ✅ Actualización en tiempo real
- ✅ Múltiples vistas de información
- ✅ Control interactivo con joystick
- ✅ Gráfico de precios históricos
- ✅ Indicadores visuales de cambios
- ✅ Modo de ahorro de energía
- ✅ Cache de datos offline

## 📄 Licencia

MIT License - Ver archivo LICENSE para más detalles.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request