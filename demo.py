#!/usr/bin/env python3
"""
Demo script to showcase the VirtualBox GPS plugin functionality
Runs both host and guest components in demo mode side-by-side
"""

import time
import json
from datetime import datetime
from typing import Optional
from vbox_gps_host import GPSLocationProvider, VBoxGPSService
from vbox_gps_guest import VBoxGPSClient


class DemoGPSBridge:
    """Simulates the VirtualBox guest property communication"""
    
    def __init__(self):
        self.properties = {}
    
    def set_property(self, key: str, value: str):
        """Host sets a property"""
        self.properties[key] = value
    
    def get_property(self, key: str) -> Optional[str]:
        """Guest gets a property"""
        return self.properties.get(key)


def run_demo(duration: int = 30, interval: int = 3):
    """Run a complete demo of the GPS plugin"""
    
    print("=" * 70)
    print(" VirtualBox GPS Plugin - Interactive Demo")
    print("=" * 70)
    print()
    print("This demo simulates the GPS location sharing between:")
    print("  • HOST: Captures GPS data and shares via guest properties")
    print("  • GUEST: Receives GPS data from guest properties")
    print()
    print(f"Demo will run for {duration} seconds with {interval}s update intervals")
    print("=" * 70)
    print()
    
    bridge = DemoGPSBridge()
    gps_provider = GPSLocationProvider(demo_mode=True)
    
    print("\n🚀 Starting demo...\n")
    
    start_time = time.time()
    iteration = 0
    
    try:
        while time.time() - start_time < duration:
            iteration += 1
            
            print(f"\n{'─' * 70}")
            print(f"  Update #{iteration} - {datetime.now().strftime('%H:%M:%S')}")
            print(f"{'─' * 70}")
            
            location = gps_provider.get_location()
            
            print("\n📍 HOST: Generated GPS location")
            print(f"   Latitude:  {location['latitude']}")
            print(f"   Longitude: {location['longitude']}")
            print(f"   Altitude:  {location['altitude']} m")
            print(f"   Accuracy:  {location['accuracy']} m")
            
            location_json = json.dumps(location)
            bridge.set_property("/VirtualBox/GuestInfo/GPS/Location", location_json)
            bridge.set_property("/VirtualBox/GuestInfo/GPS/Latitude", str(location['latitude']))
            bridge.set_property("/VirtualBox/GuestInfo/GPS/Longitude", str(location['longitude']))
            
            print("\n📤 HOST: Shared via guest properties")
            print(f"   Property: /VirtualBox/GuestInfo/GPS/Location")
            print(f"   Size: {len(location_json)} bytes")
            
            received_json = bridge.get_property("/VirtualBox/GuestInfo/GPS/Location")
            
            if received_json:
                received_location = json.loads(received_json)
                
                print("\n📥 GUEST: Received GPS location")
                print(f"   Latitude:  {received_location['latitude']}")
                print(f"   Longitude: {received_location['longitude']}")
                print(f"   Altitude:  {received_location['altitude']} m")
                print(f"   Accuracy:  {received_location['accuracy']} m")
                print(f"   Timestamp: {received_location['timestamp']}")
                
                print("\n✅ Data transfer successful!")
            else:
                print("\n❌ No data received by guest")
            
            if time.time() - start_time < duration:
                print(f"\n⏳ Next update in {interval} seconds...")
                time.sleep(interval)
        
        print("\n" + "=" * 70)
        print(f"✨ Demo completed! Ran {iteration} location updates.")
        print("=" * 70)
        print("\nTo use in production:")
        print("  HOST: python vbox_gps_host.py --vm YourVMName")
        print("  GUEST: python vbox_gps_guest.py")
        print("\nFor testing without VirtualBox:")
        print("  HOST: python vbox_gps_host.py --demo")
        print("  GUEST: python vbox_gps_guest.py --demo")
        print()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
        print(f"Completed {iteration} updates before stopping.")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='VirtualBox GPS Plugin Demo')
    parser.add_argument('--duration', type=int, default=30, 
                       help='Demo duration in seconds (default: 30)')
    parser.add_argument('--interval', type=int, default=3,
                       help='Update interval in seconds (default: 3)')
    
    args = parser.parse_args()
    run_demo(duration=args.duration, interval=args.interval)
