from onos_controller import ONOSController

onos = ONOSController()

print("Testing ONOS API...")

# Test 1: Can we connect?
try:
    devices = onos.get_devices()
    print("✓ Connection successful")
    print(f"  Found {len(devices['devices'])} devices")
except Exception as e:
    print(f"✗ Connection failed: {e}")
    exit(1)

# Test 2: Can we see hosts?
hosts = onos.get_hosts()
print(f"✓ Found {len(hosts['hosts'])} hosts")

# Test 3: Can we see links?
links = onos.get_links()
print(f"✓ Found {len(links['links'])} links")

print("\nAll tests passed!")
