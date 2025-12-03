import requests
import json

class ONOSController:
    def __init__(self, ip="", port=8181):
        self.base_url = f"http://{ip}:{port}/onos/v1"
        self.auth = ('onos', 'rocks')
    
    def get_devices(self):
        """Get all switches"""
        response = requests.get(f"{self.base_url}/devices", auth=self.auth)
        return response.json()
    
    def get_hosts(self):
        """Get all hosts"""
        response = requests.get(f"{self.base_url}/hosts", auth=self.auth)
        return response.json()
    
    def get_links(self):
        """Get all links"""
        response = requests.get(f"{self.base_url}/links", auth=self.auth)
        return response.json()
    
    def block_host(self, device_id, port):
        """Block traffic from a specific port (host)"""
        flow_rule = {
            "priority": 40000,
            "timeout": 0,
            "isPermanent": True,
            "deviceId": device_id,
            "treatment": {
                "instructions": [{"type": "DROP"}]
            },
            "selector": {
                "criteria": [
                    {
                        "type": "IN_PORT",
                        "port": str(port)
                    }
                ]
            }
        }
        
        response = requests.post(
            f"{self.base_url}/flows/{device_id}",
            json=flow_rule,
            auth=self.auth
        )
        return response.status_code == 201
    
    def remove_all_flows(self, device_id):
        """Remove all flows from a device (restore normal operation)"""
        # Get all flows
        response = requests.get(f"{self.base_url}/flows", auth=self.auth)
        flows = response.json()['flows']
        
        # Delete flows for this device
        for flow in flows:
            if flow['deviceId'] == device_id:
                requests.delete(
                    f"{self.base_url}/flows/{device_id}/{flow['id']}",
                    auth=self.auth
                )
        return True
    
    def limit_bandwidth(self, device_id, port, rate_mbps):
        """Limit bandwidth on a port (create congestion)"""
        # This requires meter bands - more complex
        # For now, can simulate by adding delay or priority
        flow_rule = {
            "priority": 30000,  # Lower priority = slower
            "timeout": 0,
            "isPermanent": True,
            "deviceId": device_id,
            "treatment": {
                "instructions": [
                    {
                        "type": "OUTPUT",
                        "port": "CONTROLLER"  # Send to controller (slower)
                    }
                ]
            },
            "selector": {
                "criteria": [
                    {
                        "type": "IN_PORT",
                        "port": str(port)
                    }
                ]
            }
        }
        
        response = requests.post(
            f"{self.base_url}/flows/{device_id}",
            json=flow_rule,
            auth=self.auth
        )
        return response.status_code == 201

# Usage example
if __name__ == "__main__":
    onos = ONOSController()
    
    # Get topology info
    devices = onos.get_devices()
    print(f"Devices: {devices}")
    
    hosts = onos.get_hosts()
    print(f"Hosts: {hosts}")
    
    # Block h1 (assuming it's on port 1 of switch of:0000000000000001)
    # onos.block_host("of:0000000000000001", 1)
    
    # Restore normal operation
    # onos.remove_all_flows("of:0000000000000001")
