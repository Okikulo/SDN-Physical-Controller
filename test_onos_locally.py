#!/usr/bin/env python3
"""
Test script for Mininet + ONOS integration on localhost
"""

import requests
import subprocess
import time
import json

class ONOSTest:
    def __init__(self):
        self.base_url = "http://127.0.0.1:8181/onos/v1"
        self.auth = ('onos', 'rocks')
    
    def test_connection(self):
        """Test 1: Can we connect to ONOS?"""
        print("\n=== Test 1: ONOS Connection ===")
        try:
            response = requests.get(f"{self.base_url}/devices", auth=self.auth, timeout=5)
            if response.status_code == 200:
                print("✓ ONOS is reachable")
                return True
            else:
                print(f"✗ ONOS returned status {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Cannot connect to ONOS: {e}")
            print("  Make sure ONOS Docker container is running:")
            print("  docker ps | grep onos")
            return False
    
    def test_apps(self):
        """Test 2: Are required apps active?"""
        print("\n=== Test 2: ONOS Applications ===")
        try:
            response = requests.get(f"{self.base_url}/applications", auth=self.auth)
            apps = response.json()['applications']
            
            required_apps = ['org.onosproject.openflow', 'org.onosproject.fwd']
            active_apps = [app['name'] for app in apps if app['state'] == 'ACTIVE']
            
            for app_name in required_apps:
                if app_name in active_apps:
                    print(f"✓ {app_name} is ACTIVE")
                else:
                    print(f"✗ {app_name} is NOT active")
                    print(f"  Activate it: docker exec -it onos /opt/onos/bin/onos")
                    print(f"  Then run: app activate {app_name}")
            
            return all(app in active_apps for app in required_apps)
        except Exception as e:
            print(f"✗ Error checking apps: {e}")
            return False
    
    def get_topology(self):
        """Test 3: Get current topology"""
        print("\n=== Test 3: Network Topology ===")
        try:
            # Get devices
            devices = requests.get(f"{self.base_url}/devices", auth=self.auth).json()
            print(f"Devices: {len(devices['devices'])}")
            for device in devices['devices']:
                print(f"  - {device['id']} ({device['type']}) - Available: {device['available']}")
            
            # Get hosts
            hosts = requests.get(f"{self.base_url}/hosts", auth=self.auth).json()
            print(f"\nHosts: {len(hosts['hosts'])}")
            for host in hosts['hosts']:
                print(f"  - {host['id']} at {host['ipAddresses']}")
                for loc in host['locations']:
                    print(f"    Connected to: {loc['elementId']} port {loc['port']}")
            
            # Get links
            links = requests.get(f"{self.base_url}/links", auth=self.auth).json()
            print(f"\nLinks: {len(links['links'])}")
            for link in links['links']:
                print(f"  - {link['src']['device']}:{link['src']['port']} → {link['dst']['device']}:{link['dst']['port']}")
            
            return len(devices['devices']) > 0
        except Exception as e:
            print(f"✗ Error getting topology: {e}")
            return False
    
    def test_flows(self):
        """Test 4: Check flow rules"""
        print("\n=== Test 4: Flow Rules ===")
        try:
            response = requests.get(f"{self.base_url}/flows", auth=self.auth)
            flows = response.json()['flows']
            print(f"Total flows: {len(flows)}")
            
            for flow in flows[:5]:  # Show first 5
                print(f"\n  Flow ID: {flow['id'][:8]}...")
                print(f"  Device: {flow['deviceId']}")
                print(f"  State: {flow['state']}")
                print(f"  Priority: {flow['priority']}")
            
            return True
        except Exception as e:
            print(f"✗ Error checking flows: {e}")
            return False

def start_mininet_test():
    """Start a simple Mininet topology"""
    print("\n=== Starting Mininet ===")
    print("Running: sudo mn --controller=remote,ip=127.0.0.1,port=6653 --switch ovsk,protocols=OpenFlow13 --topo=single,2")
    print("\nMininet will start in a new terminal.")
    print("In Mininet, run these commands:")
    print("  mininet> pingall")
    print("  mininet> h1 ping -c3 h2")
    print("  mininet> exit")
    print("\nPress Enter when Mininet is running...")
    input()

def connectivity_test():
    """Test 5: Network connectivity"""
    print("\n=== Test 5: Network Connectivity ===")
    print("Make sure Mininet is running, then run 'pingall' in Mininet")
    print("You should see:")
    print("  h1 -> h2")
    print("  h2 -> h1")
    print("  *** Results: 0% dropped (2/2 received)")

def main():
    print("=" * 60)
    print("ONOS + Mininet Integration Test (Localhost)")
    print("=" * 60)
    
    onos = ONOSTest()
    
    # Run tests
    results = []
    
    results.append(("ONOS Connection", onos.test_connection()))
    
    if results[-1][1]:  # If ONOS is reachable
        results.append(("ONOS Apps", onos.test_apps()))
        
        print("\n" + "=" * 60)
        print("Now start Mininet in another terminal:")
        print("sudo mn --controller=remote,ip=127.0.0.1,port=6653 --switch ovsk,protocols=OpenFlow13 --topo=single,2")
        print("=" * 60)
        print("\nPress Enter after Mininet is running...")
        input()
        
        # Wait a bit for Mininet to connect
        print("\nWaiting 3 seconds for topology to stabilize...")
        time.sleep(3)
        
        results.append(("Topology Discovery", onos.get_topology()))
        results.append(("Flow Rules", onos.test_flows()))
        
        connectivity_test()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {test_name}")
    
    print("\n" + "=" * 60)
    if all(r[1] for r in results):
        print("🎉 All tests passed! Your setup is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above.")
    print("=" * 60)

if __name__ == "__main__":
    main()
