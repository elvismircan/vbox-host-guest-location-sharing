#!/usr/bin/env python3
"""
VirtualBox GPS Guest Client
Receives GPS location data from the host VM
"""

import time
import json
import argparse
import subprocess
from datetime import datetime
from typing import Optional, Dict


class VBoxGPSClient:
    """Client to receive GPS data from VirtualBox host"""
    
    def __init__(self, demo_mode: bool = False):
        self.demo_mode = demo_mode
        self.last_location = None
    
    def get_guest_property(self, key: str) -> Optional[str]:
        """Get a guest property value using VBoxControl"""
        if self.demo_mode:
            return self._get_demo_property(key)
        
        try:
            result = subprocess.run(
                ['VBoxControl', 'guestproperty', 'get', key],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                output = result.stdout.strip()
                if 'Value:' in output:
                    value = output.split('Value:', 1)[1].strip()
                    return value
            return None
        except FileNotFoundError:
            print("VBoxControl not found. Make sure VirtualBox Guest Additions are installed.")
            print("Running in demo mode.")
            self.demo_mode = True
            return self._get_demo_property(key)
        except Exception as e:
            print(f"Error reading guest property: {e}")
            return None
    
    def _get_demo_property(self, key: str) -> Optional[str]:
        """Return demo data for testing"""
        demo_location = {
            'latitude': 37.7749,
            'longitude': -122.4194,
            'altitude': 50.0,
            'accuracy': 10.0,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'source': 'demo'
        }
        
        if '/Location' in key:
            return json.dumps(demo_location)
        elif '/Latitude' in key:
            return str(demo_location['latitude'])
        elif '/Longitude' in key:
            return str(demo_location['longitude'])
        elif '/Timestamp' in key:
            return demo_location['timestamp']
        
        return None
    
    def get_location(self) -> Optional[Dict]:
        """Get current GPS location from host"""
        location_json = self.get_guest_property("/VirtualBox/GuestInfo/GPS/Location")
        
        if location_json:
            try:
                location = json.loads(location_json)
                self.last_location = location
                return location
            except json.JSONDecodeError as e:
                print(f"Error parsing location JSON: {e}")
                return None
        
        return None
    
    def display_location(self, location: Dict):
        """Display location information"""
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] GPS Location Received:")
        print(f"  Latitude:  {location.get('latitude', 'N/A')}")
        print(f"  Longitude: {location.get('longitude', 'N/A')}")
        print(f"  Altitude:  {location.get('altitude', 'N/A')} m")
        print(f"  Accuracy:  {location.get('accuracy', 'N/A')} m")
        print(f"  Timestamp: {location.get('timestamp', 'N/A')}")
        print(f"  Source:    {location.get('source', 'unknown')}")
    
    def run(self, interval: int = 5, continuous: bool = True):
        """Main client loop"""
        print("=" * 60)
        print("VirtualBox GPS Guest Client")
        print("=" * 60)
        print(f"Mode: {'DEMO' if self.demo_mode else 'PRODUCTION'}")
        print(f"Update Interval: {interval} seconds")
        print("=" * 60)
        print("\nListening for GPS location updates...")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                location = self.get_location()
                
                if location:
                    self.display_location(location)
                else:
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] No GPS data available")
                
                if not continuous:
                    break
                
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n\nStopping GPS client...")
            print("Client stopped.")


def main():
    parser = argparse.ArgumentParser(
        description='VirtualBox GPS Guest Client - Receive GPS location from host'
    )
    parser.add_argument(
        '--demo',
        action='store_true',
        help='Run in demo mode'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=5,
        help='Update interval in seconds (default: 5)'
    )
    parser.add_argument(
        '--once',
        action='store_true',
        help='Get location once and exit'
    )
    
    args = parser.parse_args()
    
    client = VBoxGPSClient(demo_mode=args.demo)
    client.run(interval=args.interval, continuous=not args.once)


if __name__ == '__main__':
    main()
