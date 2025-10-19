# ✅ TETSUO Display - Checklist de Instalación

Marca cada paso cuando lo completes.

---

## 🔍 PASO 1: Encontrar IP del Raspberry Pi

**Ejecuta en Terminal del Mac:**
```bash
arp -a | grep -i "b8:27:eb\|dc:a6:32\|e4:5f:01"
```

**O alternativamente:**
```bash
ping raspberrypi.local
```

- [ ] IP encontrada: __________________ (anótala aquí)

---

## 📤 PASO 2: Transferir Proyecto

**Opción A - Script Automático (RECOMENDADO):**

Abre Terminal y ejecuta:
```bash
cd ~/Desktop/tetsuo-display
./deploy-to-pi.sh
```

- [ ] Script ejecutado
- [ ] IP ingresada: __________________
- [ ] Contraseña ingresada: 5157
- [ ] Archivos transferidos con éxito

**Opción B - Manual:**
```bash
scp -r ~/Desktop/tetsuo-display/ pi@<TU_IP>:~/
```
(Reemplaza `<TU_IP>` con la IP real)

- [ ] Archivos copiados

---

## 🔌 PASO 3: Conectar al Raspberry Pi

```bash
ssh pi@<TU_IP>
```
Contraseña: `5157`

- [ ] Conectado al Pi vía SSH
- [ ] Ves el prompt del Pi (algo como `pi@raspberrypi:~ $`)

---

## 🛠️ PASO 4: Instalar en el Pi

**Dentro del SSH del Pi, ejecuta:**
```bash
cd ~/tetsuo-display
./install.sh
```

**El script preguntará cosas, responde:**
- [ ] `Run wizard now? (Y/n):` → Presiona `Y` y Enter

---

## 🎯 PASO 5: Responder al Wizard

El wizard hará preguntas, responde:

1. [ ] `Continue with setup?` → `y`
2. [ ] `SPI enabled?` → Debería decir "✓ SPI is enabled"
3. [ ] `Is this pinout correct?` → `y`
4. [ ] El wizard buscará el par de trading... espera...
5. [ ] `Use this pair?` → `y`
6. [ ] `Do you have a Birdeye API key?` → `n`
7. [ ] `Run display test?` → `y`
8. [ ] **MIRA LA PANTALLA** - ¿Ves un patrón de prueba? → `y`
9. [ ] `Install service now?` → `y`
10. [ ] `Start service now?` → `y`

---

## ✅ PASO 6: Verificar que Funciona

**Ejecuta en el Pi:**
```bash
sudo systemctl status tetsuo-display
```

**Deberías ver:**
- [ ] `Active: active (running)` en color verde
- [ ] NO hay errores en rojo

**Ver logs en vivo:**
```bash
sudo journalctl -u tetsuo-display -f
```

**Deberías ver cada ~45 segundos:**
- [ ] `[HH:MM:SS] Fetching data...`
- [ ] `Price: $0.00XXXXXX`
- [ ] `Display updated`

**Presiona Ctrl+C para salir de los logs**

---

## 👀 PASO 7: Verificar la Pantalla E-Paper

**Mira tu pantalla e-paper física. Debería mostrar:**

- [ ] "TETSUO (SOL)" en la parte superior
- [ ] Precio actual (ejemplo: $0.001568)
- [ ] Cambio 24h con flecha ▲ o ▼
- [ ] Volumen 24h
- [ ] Liquidez
- [ ] Hora actual abajo a la izquierda
- [ ] "LIVE" abajo a la derecha

---

## 🎉 PASO 8: Prueba de Reinicio

**Para asegurarte que sobrevive reinicios:**

```bash
sudo reboot
```

- [ ] Pi reiniciado

**Espera 1 minuto, luego conéctate de nuevo:**
```bash
ssh pi@<TU_IP>
```

**Verifica el servicio:**
```bash
sudo systemctl status tetsuo-display
```

- [ ] Servicio corriendo automáticamente después de reiniciar
- [ ] Pantalla muestra datos

---

## 🔧 Comandos Útiles para Después

```bash
# Ver estado
sudo systemctl status tetsuo-display

# Ver logs
sudo journalctl -u tetsuo-display -f

# Reiniciar servicio
sudo systemctl restart tetsuo-display

# Detener servicio
sudo systemctl stop tetsuo-display

# Ver últimas 50 líneas
sudo journalctl -u tetsuo-display -n 50

# Editar configuración
nano ~/tetsuo-display/config.yaml
# Después de editar: sudo systemctl restart tetsuo-display
```

---

## ❌ Si Algo Sale Mal

### SPI no está habilitado

```bash
sudo raspi-config
```
→ Interface Options → SPI → Enable → Reboot

### No se ve nada en la pantalla

```bash
cd ~/tetsuo-display
source venv/bin/activate
python3 tests/display_test.py
```

### El servicio no arranca

```bash
# Ver errores
sudo journalctl -u tetsuo-display -n 100

# Probar manualmente
cd ~/tetsuo-display
source venv/bin/activate
python3 app/main.py
```

### APIs no funcionan

```bash
cd ~/tetsuo-display
source venv/bin/activate
python3 tests/smoke_test.py
```

---

## 🏆 Lista de Éxito Final

Si puedes marcar estos, ¡TODO FUNCIONA!

- [ ] Servicio corriendo (`systemctl status`)
- [ ] Logs muestran "Display updated" cada 45s
- [ ] Pantalla e-paper muestra precio de TETSUO
- [ ] Precio se actualiza automáticamente
- [ ] Sobrevive reinicio del Pi
- [ ] Muestra "LIVE" cuando hay internet
- [ ] Muestra "STALE" si desconectas internet

---

## 📞 Siguiente Paso

**Una vez que completes todos los checkboxes, habrás terminado!**

Tu pantalla e-paper ahora mostrará el precio de TETSUO 24/7,
actualizándose cada 45 segundos automáticamente.

¡Disfruta tu display! 🚀
