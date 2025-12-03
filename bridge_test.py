#!/usr/bin/env python3
"""
SDN Bridge Script - Production Mode (With Arduino)
Group 5 - Advanced Computer Networks

Connects Arduino <-> Mininet <-> ONOS
"""

import serial
import subprocess
import time
import sys

# ============ CONFIGURATION ============
ARDUINO_PORT = '/dev/ttyACM0'  # Change if needed (ls /dev/ttyACM* to verify)
ARDUINO_BAUD = 9600
ONOS_IP = '192.168.16.111'  # Laptop IP

# ============ STATE VARIABLES ============
h1_connected = True
h2_connected = True
switch_congested = False
selected_device = None  # 'h1', 'h2', 's1', 'both'
last_temperature = 0.0  

# ============ NETWORK COMMANDS ============

def link_h1_down():
    """Disconnect h1 from switch"""
    print("  → Executing: h1 link DOWN")
    result = subprocess.run(
        ["sudo", "ovs-ofctl", "-O", "OpenFlow13", "mod-port", "s1", "s1-eth1", "down"],
        capture_output=True
    )
    success = result.returncode == 0
    if success:
        print("  ✓ h1 disconnected")
    else:
        print(f"  ✗ Error: {result.stderr.decode()}")
    return success

def link_h1_up():
    """Reconnect h1 to switch"""
    print("  → Executing: h1 link UP")
    result = subprocess.run(
        ["sudo", "ovs-ofctl", "-O", "OpenFlow13", "mod-port", "s1", "s1-eth1", "up"],
        capture_output=True
    )
    success = result.returncode == 0
    if success:
        print("  ✓ h1 connected")
    else:
        print(f"  ✗ Error: {result.stderr.decode()}")
    return success

def link_h2_down():
    """Disconnect h2 from switch"""
    print("  → Executing: h2 link DOWN")
    result = subprocess.run(
        ["sudo", "ovs-ofctl", "-O", "OpenFlow13", "mod-port", "s1", "s1-eth2", "down"],
        capture_output=True
    )
    success = result.returncode == 0
    if success:
        print("  ✓ h2 disconnected")
    else:
        print(f"  ✗ Error: {result.stderr.decode()}")
    return success

def link_h2_up():
    """Reconnect h2 to switch"""
    print("  → Executing: h2 link UP")
    result = subprocess.run(
        ["sudo", "ovs-ofctl", "-O", "OpenFlow13", "mod-port", "s1", "s1-eth2", "up"],
        capture_output=True
    )
    success = result.returncode == 0
    if success:
        print("  ✓ h2 connected")
    else:
        print(f"  ✗ Error: {result.stderr.decode()}")
    return success

def congestion_on():
    """Create congestion on switch"""
    print("  → Executing: Congestion ON")
    # First remove any existing rules
    subprocess.run(
        ["sudo", "tc", "qdisc", "del", "dev", "s1-eth1", "root"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    # Add bandwidth limit
    result = subprocess.run([
        "sudo", "tc", "qdisc", "add", "dev", "s1-eth1", "root",
        "tbf", "rate", "1mbit", "burst", "32kbit", "latency", "400ms"
    ], capture_output=True)
    success = result.returncode == 0
    if success:
        print("  ✓ Congestion active (1 Mbps)")
    else:
        print(f"  ✗ Error: {result.stderr.decode()}")
    return success

def congestion_off():
    """Remove congestion"""
    print("  → Executing: Congestion OFF")
    result = subprocess.run(
        ["sudo", "tc", "qdisc", "del", "dev", "s1-eth1", "root"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    print("  ✓ Congestion removed")
    return True

# ============ MESSAGE HANDLERS ============

def handle_joystick_up(arduino):
    """Joystick UP: Select Switch"""
    global selected_device
    selected_device = 's1'
    print(f"[JOY_UP] 🎯 Selected: SWITCH (s1)")
    print(f"  Current state: {'CONGESTED' if switch_congested else 'NORMAL'}")
    print(f"  🌡️ Temperature: {last_temperature:.1f}°C")  # NEW
    send_led_feedback(arduino)

def handle_joystick_left(arduino):
    """Joystick LEFT: Select h1"""
    global selected_device
    selected_device = 'h1'
    print(f"[JOY_LEFT] 🎯 Selected: HOST h1")
    print(f"  Current state: {'CONNECTED' if h1_connected else 'DISCONNECTED'}")
    print(f"  🌡️ Temperature: {last_temperature:.1f}°C")  # NEW
    send_led_feedback(arduino)

def handle_joystick_right(arduino):
    """Joystick RIGHT: Select h2"""
    global selected_device
    selected_device = 'h2'
    print(f"[JOY_RIGHT] 🎯 Selected: HOST h2")
    print(f"  Current state: {'CONNECTED' if h2_connected else 'DISCONNECTED'}")
    print(f"  🌡️ Temperature: {last_temperature:.1f}°C")  # NEW
    send_led_feedback(arduino)

def handle_joystick_down(arduino):
    """Joystick DOWN: Select both hosts"""
    global selected_device
    selected_device = 'both'
    print(f"[JOY_DOWN] 🎯 Selected: BOTH HOSTS (h1 + h2)")
    print(f"  h1: {'CONNECTED' if h1_connected else 'DISCONNECTED'}")
    print(f"  h2: {'CONNECTED' if h2_connected else 'DISCONNECTED'}")
    print(f"  🌡️ Temperature: {last_temperature:.1f}°C")  # NEW
    send_led_feedback(arduino)

def handle_button(arduino):
    """Button pressed: Toggle state of selected device"""
    global h1_connected, h2_connected, switch_congested, selected_device
    
    if selected_device is None:
        print("[BUTTON] ⚠ No device selected! Use joystick first")
        return
    
    print(f"[BUTTON] 🔘 Action on: {selected_device.upper()}")
    
    if selected_device == 'h1':
        if h1_connected:
            if link_h1_down():
                h1_connected = False
                print("  ✓ h1 → DISCONNECTED")
        else:
            if link_h1_up():
                h1_connected = True
                print("  ✓ h1 → CONNECTED")
    
    elif selected_device == 'h2':
        if h2_connected:
            if link_h2_down():
                h2_connected = False
                print("  ✓ h2 → DISCONNECTED")
        else:
            if link_h2_up():
                h2_connected = True
                print("  ✓ h2 → CONNECTED")
    
    elif selected_device == 's1':
        if switch_congested:
            if congestion_off():
                switch_congested = False
                print("  ✓ Switch → NORMAL")
        else:
            if congestion_on():
                switch_congested = True
                print("  ✓ Switch → CONGESTED")
    
    elif selected_device == 'both':
        if h1_connected or h2_connected:
            print("  → Disconnecting both hosts...")
            link_h1_down()
            link_h2_down()
            h1_connected = False
            h2_connected = False
            print("  ✓ h1 and h2 → DISCONNECTED")
        else:
            print("  → Connecting both hosts...")
            link_h1_up()
            link_h2_up()
            h1_connected = True
            h2_connected = True
            print("  ✓ h1 and h2 → CONNECTED")
    
    send_led_feedback(arduino)

def send_led_feedback(arduino):
    """Send LED commands to Arduino
    
    Simple LEDs (pins 5 and 6):
    - LED1:GREEN → LED h1 ON (connected)
    - LED1:RED → LED h1 OFF (disconnected)
    - LED2:GREEN → LED h2 ON (connected)
    - LED2:RED → LED h2 OFF (disconnected)
    
    RGB LED (switch):
    - LED3:GREEN → Normal
    - LED3:BLUE → Congested
    - LED3:RED → Both hosts down
    """
    print("\n  [LED Feedback]")
    
    # LED h1 (pin 5) - Simple ON/OFF
    if h1_connected:
        arduino.write(b"LED1:GREEN\n")  # LED ON
        if selected_device == 'h1':
            print(f"    LED h1: 💡 ON (SELECTED)")
        else:
            print(f"    LED h1: 💡 ON")
    else:
        arduino.write(b"LED1:RED\n")  # LED OFF
        if selected_device == 'h1':
            print(f"    LED h1: ⚫ OFF (SELECTED)")
        else:
            print(f"    LED h1: ⚫ OFF")
    
    # LED h2 (pin 6) - Simple ON/OFF
    if h2_connected:
        arduino.write(b"LED2:GREEN\n")  # LED ON
        if selected_device == 'h2':
            print(f"    LED h2: 💡 ON (SELECTED)")
        else:
            print(f"    LED h2: 💡 ON")
    else:
        arduino.write(b"LED2:RED\n")  # LED OFF
        if selected_device == 'h2':
            print(f"    LED h2: ⚫ OFF (SELECTED)")
        else:
            print(f"    LED h2: ⚫ OFF")
    
    # LED3 RGB (switch) - Multiple states
    if selected_device == 's1':
        if switch_congested:
            arduino.write(b"LED3:BLUE\n")
            print(f"    LED3 Switch: 🔵 BLUE - Congested (SELECTED)")
        else:
            arduino.write(b"LED3:GREEN\n")
            print(f"    LED3 Switch: 🟢 GREEN - Normal (SELECTED)")
    elif selected_device == 'both':
        if not h1_connected and not h2_connected:
            arduino.write(b"LED3:RED\n")
            print(f"    LED3 Switch: 🔴 RED - Both Down (SELECTED)")
        elif switch_congested:
            arduino.write(b"LED3:BLUE\n")
            print(f"    LED3 Switch: 🔵 BLUE- Congested (SELECTED)")
        else:
            arduino.write(b"LED3:GREEN\n")
            print(f"    LED3 Switch: 🟢 GREEN (SELECTED)")
    else:
        if not h1_connected and not h2_connected:
            arduino.write(b"LED3:RED\n")
            print(f"    LED3 Switch: 🔴 RED - Both Down")
        elif switch_congested:
            arduino.write(b"LED3:BLUE \n")
            print(f"    LED3 Switch: 🔵 BLUE - Congested")
        else:
            arduino.write(b"LED3:GREEN\n")
            print(f"    LED3 Switch: 🟢 GREEN - Normal")
    
    print()

def handle_temp(arduino, temp):
    """Temperature: Monitoring"""
    global last_temperature
    last_temperature = temp  # Store the temperature
    
    print(f"[TEMP] {temp}°C")
    if temp > 30:
        print("  ⚠ High temperature!")       

# ============ ARDUINO INPUT ============

def setup_arduino():
    """Connect to Arduino and wait until ready"""
    print("=== SDN Bridge Starting ===")
    print(f"Connecting to Arduino on {ARDUINO_PORT}...")
    
    try:
        arduino = serial.Serial(ARDUINO_PORT, ARDUINO_BAUD, timeout=1)
        time.sleep(2)  # Wait for Arduino reset
        print("✓ Arduino connected!")
        
        # Wait for "READY" message from Arduino (optional)
        timeout = time.time() + 5
        while time.time() < timeout:
            if arduino.in_waiting > 0:
                msg = arduino.readline().decode('utf-8').strip()
                if msg == "READY":
                    print("✓ Arduino ready!")
                    break
        
        # Initialize LEDs
        # h1 and h2 ON (connected), switch green (normal)
        arduino.write(b"LED1:GREEN\n")
        arduino.write(b"LED2:GREEN\n")
        arduino.write(b"LED3:GREEN\n")
        print("✓ LEDs initialized")
        
        return arduino
        
    except serial.SerialException as e:
        print(f"✗ Error connecting to Arduino: {e}")
        print(f"  Verify:")
        print(f"  1. Arduino connected via USB")
        print(f"  2. Correct port: ls /dev/ttyACM* /dev/ttyUSB*")
        print(f"  3. Permissions: sudo usermod -a -G dialout $USER")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        sys.exit(1)

def arduino_loop(arduino):
    """Main loop: read commands from Arduino"""
    print("\n=== Bridge Running ===")
    print("Waiting for Arduino commands...\n")
    
    try:
        while True:
            if arduino.in_waiting > 0:
                mensaje = arduino.readline().decode('utf-8').strip()
                
                if not mensaje or mensaje == "READY":
                    continue
                
                print(f"[Arduino] {mensaje}")
                
                # Process message
                if mensaje == "JOY_UP":
                    handle_joystick_up(arduino)
                    
                elif mensaje == "JOY_LEFT":
                    handle_joystick_left(arduino)
                    
                elif mensaje == "JOY_RIGHT":
                    handle_joystick_right(arduino)
                    
                elif mensaje == "JOY_DOWN":
                    handle_joystick_down(arduino)
                    
                elif mensaje == "BUTTON":
                    handle_button(arduino)
                    
                elif mensaje.startswith("TEMP:"):
                    try:
                        temp = float(mensaje.split(":")[1])
                        handle_temp(arduino, temp)
                    except ValueError:
                        print(f"  ✗ Error parsing temperature: {mensaje}")
                
                else:
                    print(f"  ? Unknown command: {mensaje}")
            
            time.sleep(0.01)
            
    except KeyboardInterrupt:
        print("\n\n=== Bridge Stopped ===")
        # Cleanup: reset LEDs to initial state
        arduino.write(b"LED1:GREEN\n")
        arduino.write(b"LED2:GREEN\n")
        arduino.write(b"LED3:GREEN\n")
        arduino.close()
        print("Arduino disconnected. Goodbye!")

# ============ MAIN ============

def main():
    print("="*60)
    print("SDN Bridge - PRODUCTION MODE (With Arduino)")
    print("="*60)
    print()
    
    # Connect Arduino
    arduino = setup_arduino()
    
    # Initial state
    print("\nInitial state:")
    print("  h1: CONNECTED (LED ON)")
    print("  h2: CONNECTED (LED ON)")
    print("  Switch: NORMAL (RGB LED Green)")
    
    # Start loop
    arduino_loop(arduino)

if __name__ == "__main__":
    main()
