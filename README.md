# SDN Physical Controller

A hands-on SDN demonstration system that connects physical hardware (Arduino) to a virtual network (Mininet) managed by an ONOS controller. Use a joystick to select network devices and a button to toggle their state—see the results instantly on LEDs and the ONOS web UI.

## Hardware Requirements

| Component | Quantity | Notes |
|-----------|----------|-------|
| Laptop | 1 | Runs ONOS controller (x86_64) |
| Raspberry Pi 4 | 1 | Runs Mininet + bridge script |
| Arduino Uno | 1 | Physical I/O controller |
| Joystick Module (HW-504) | 1 | Device selection |
| Push Button (HW-483) | 1 | Toggle device state |
| LED (single color) | 2 | Host status (h1, h2) |
| RGB LED | 1 | Switch status |
| 220Ω Resistors | 5 | For LEDs |
| Jumper Wires | ~20 | Connections |
| USB Cable (A to B) | 1 | Arduino to Raspberry Pi |

## Architecture

```
┌─────────────────┐
│  Laptop         │
│  - ONOS         │ ← SDN Controller
│  - Web UI       │
└────────┬────────┘
         │ OpenFlow (port 6653, WiFi)
         │
┌────────┴────────┐
│  Raspberry Pi   │
│  - Mininet      │ ← Virtual network
│  - bridge.py    │ ← Coordinator script
└────────┬────────┘
         │ Serial USB (9600 baud)
         │
┌────────┴────────┐
│    Arduino      │
│  - Joystick     │ ← Input
│  - Button       │ ← Input
│  - LEDs         │ ← Output
└─────────────────┘
```

## Pin Wiring (Arduino)

| Pin | Component | Type |
|-----|-----------|------|
| 2 | Button | INPUT |
| 4 | Joystick Switch | INPUT |
| 5 | LED h1 | OUTPUT |
| 6 | LED h2 | OUTPUT |
| 9 | RGB LED (Green) | OUTPUT |
| 10 | RGB LED (Blue) | OUTPUT |
| 11 | RGB LED (Red) | OUTPUT |
| A0 | Joystick X-axis | INPUT |
| A1 | Joystick Y-axis | INPUT |

---

## Setup Instructions

### 1. Laptop Setup (Arch Linux)

#### Install Docker

```bash
sudo pacman -S docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
# Logout and login again, or run: newgrp docker
```

#### Run ONOS

```bash
docker pull onosproject/onos:2.7.0

docker run -t -d \
  -p 8181:8181 \
  -p 8101:8101 \
  -p 6653:6653 \
  -p 5005:5005 \
  -p 830:830 \
  --name onos \
  onosproject/onos:2.7.0
```

#### Activate Required ONOS Apps

```bash
# Wait ~30 seconds for ONOS to start, then:
docker exec -it onos /opt/onos/bin/onos

# Inside ONOS CLI:
app activate org.onosproject.openflow
app activate org.onosproject.fwd
exit
```

#### Verify ONOS

Open browser: `http://localhost:8181/onos/ui`  
Login: `onos` / `rocks`

#### Get Your Laptop IP

```bash
ip -4 addr | grep inet
# Note the IP (e.g., 192.168.1.100) - needed for Raspberry Pi
```

---

### 1b. Laptop Setup (Ubuntu)

```bash
# Install Docker
sudo apt update
sudo apt install docker.io
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
# Logout and login again

# Then follow the same ONOS steps as Arch
```

---

### 2. Raspberry Pi Setup (Raspberry Pi OS)

#### Update System

```bash
sudo apt update && sudo apt upgrade -y
```

#### Install Mininet

```bash
sudo apt install mininet
```

#### Verify Mininet

```bash
sudo mn --test pingall
```

#### Install Python Dependencies

```bash
pip3 install pyserial
```

#### Add User to dialout Group (for Arduino Serial)

```bash
sudo usermod -a -G dialout $USER
# Logout and login again
```

#### Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/sdn-physical-controller.git
cd sdn-physical-controller
```

---

### 3. Arduino Setup

#### Option A: Using Arduino IDE

1. Install Arduino IDE on your laptop
2. Open `arduino/arduino.ino`
3. Connect Arduino via USB
4. Select Board: Arduino Uno
5. Select Port: `/dev/ttyACM0` (or similar)
6. Upload

#### Option B: Using PlatformIO (Recommended)

```bash
# Install PlatformIO CLI
pip install platformio

# Navigate to arduino folder
cd arduino

# Build and upload
pio run -t upload

# Monitor serial output
pio device monitor
```

---

## Running the System

### Step 1: Start ONOS (Laptop)

```bash
docker start onos
# Verify: http://localhost:8181/onos/ui
```

### Step 2: Start Mininet (Raspberry Pi - Terminal 1)

```bash
sudo mn --controller=remote,ip=LAPTOP_IP,port=6653 --topo=single,2
```

Replace `LAPTOP_IP` with your laptop's actual IP address.

### Step 3: Run Bridge Script (Raspberry Pi - Terminal 2)

```bash
cd sdn-physical-controller
python3 bridge.py
```

### Step 4: Test

| Action | Expected Result |
|--------|-----------------|
| Joystick Left | Select h1 |
| Joystick Right | Select h2 |
| Joystick Up | Select Switch |
| Joystick Down | Select Both Hosts |
| Press Button | Toggle selected device |

In Mininet terminal, run `pingall` to verify connectivity changes.

---

## Testing

### Test ONOS Connection (on Laptop)

```bash
python3 test_onos_locally.py
```

This will:
1. Check ONOS is reachable
2. Verify required apps are active
3. Display topology after Mininet connects
4. Show flow rules

### Test from Raspberry Pi

```bash
# Edit onos_controller.py with your laptop IP first
python3 test_onos.py
```

---

## Troubleshooting

### Arduino not detected

```bash
# Check if Arduino is connected
ls /dev/ttyACM* /dev/ttyUSB*

# Check permissions
sudo chmod 666 /dev/ttyACM0
```

### Mininet can't connect to ONOS

```bash
# Verify ONOS is running
docker ps | grep onos

# Check ONOS logs
docker logs onos

# Verify port 6653 is open on laptop
sudo ss -tlnp | grep 6653

# Test connection from Pi
telnet LAPTOP_IP 6653
```

### ONOS not showing topology

```bash
# Verify apps are activated
docker exec -it onos /opt/onos/bin/onos
apps -a -s
# Should show: openflow and fwd as ACTIVE
```

### Bridge script serial error

```bash
# Verify Arduino port
ls /dev/ttyACM*

# Edit bridge.py if port is different
ARDUINO_PORT = '/dev/ttyACM0'  # Change if needed
```

---

## Project Structure

```
sdn-physical-controller/
├── README.md
├── arduino/
│   ├── arduino.ino
│   └── platformio.ini
├── raspberry/
│   ├── bridge.py
│   ├── onos_controller.py
│   ├── test_onos.py
│   └── test_onos_locally.py
└── docs/
    └── report.pdf
```

---

## License

MIT License - Feel free to use for educational purposes.
