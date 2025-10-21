#!/usr/bin/env python3
"""
VirtualBox GPS Host Service
Captures GPS location data from the host and shares it with guest VMs
"""

import time
import json
import argparse
import random
import subprocess
import threading
from datetime import datetime
from typing import Dict, Optional
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

try:
    import vboxapi  # type: ignore
    VBOX_AVAILABLE = True
except ImportError:
    VBOX_AVAILABLE = False
    vboxapi = None  # type: ignore
    print("Warning: VirtualBox SDK not available. Running in demo mode.")


class GPSLocationProvider:
    """Provides GPS location data (real or simulated)"""
    
    def __init__(self, demo_mode: bool = False):
        self.demo_mode = demo_mode
        self.base_lat = 37.7749
        self.base_lon = -122.4194
        
    def get_location(self) -> Dict:
        """Get current GPS location"""
        if self.demo_mode:
            return self._get_simulated_location()
        else:
            return self._get_real_location()
    
    def _get_simulated_location(self) -> Dict:
        """Generate simulated GPS data for testing"""
        lat = self.base_lat + random.uniform(-0.01, 0.01)
        lon = self.base_lon + random.uniform(-0.01, 0.01)
        
        return {
            'latitude': round(lat, 6),
            'longitude': round(lon, 6),
            'altitude': round(random.uniform(0, 100), 2),
            'accuracy': round(random.uniform(5, 20), 2),
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'source': 'simulated'
        }
    
    def _get_real_location(self) -> Dict:
        """Get real GPS location from system (platform-specific)"""
        try:
            import platform
            if platform.system() == 'Windows':
                return self._get_windows_location()
            elif platform.system() == 'Linux':
                return self._get_linux_location()
            elif platform.system() == 'Darwin':
                return self._get_macos_location()
            else:
                return self._get_simulated_location()
        except Exception as e:
            print(f"Error getting real location: {e}")
            print("Falling back to simulated location")
            return self._get_simulated_location()
    
    def _get_windows_location(self) -> Dict:
        """Get location on Windows using Windows Location API"""
        return {
            'latitude': 0.0,
            'longitude': 0.0,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'source': 'windows_location_api',
            'error': 'Not implemented - use demo mode'
        }
    
    def _get_linux_location(self) -> Dict:
        """Get location on Linux using GeoClue or similar"""
        return {
            'latitude': 0.0,
            'longitude': 0.0,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'source': 'geoclue',
            'error': 'Not implemented - use demo mode'
        }
    
    def _get_macos_location(self) -> Dict:
        """Get location on macOS using CoreLocation"""
        return {
            'latitude': 0.0,
            'longitude': 0.0,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'source': 'corelocation',
            'error': 'Not implemented - use demo mode'
        }


class GPSHTTPHandler(BaseHTTPRequestHandler):
    """HTTP handler for serving GPS data"""
    
    gps_service = None  # Will be set by VBoxGPSService
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/gps' or parsed_path.path == '/gps/location':
            if self.server.gps_service:  # type: ignore
                location = self.server.gps_service.gps.get_location()  # type: ignore
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                self.wfile.write(json.dumps(location).encode('utf-8'))
            else:
                self.send_error(503, "GPS service not available")
        elif parsed_path.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            
            html = """
            <html>
            <head><title>VirtualBox GPS Service</title></head>
            <body>
            <h1>VirtualBox GPS Service</h1>
            <p>GPS location endpoint: <a href="/gps">/gps</a></p>
            </body>
            </html>
            """
            self.wfile.write(html.encode('utf-8'))
        else:
            self.send_error(404, "Endpoint not found")
    
    def log_message(self, format, *args):
        """Suppress HTTP request logging"""
        pass


class VBoxGPSService:
    """VirtualBox GPS sharing service"""
    
    def __init__(self, vm_name: str, demo_mode: bool = False, interval: int = 5, 
                 network_mode: bool = True, http_port: int = 8089):
        self.vm_name = vm_name
        self.demo_mode = demo_mode
        self.interval = interval
        self.network_mode = network_mode
        self.http_port = http_port
        self.gps = GPSLocationProvider(demo_mode=demo_mode)
        self.vbox = None
        self.machine = None
        self.http_server = None
        self.http_thread = None
        
        if VBOX_AVAILABLE and not demo_mode:
            self._init_vbox()
        
        if network_mode:
            self._start_http_server()
    
    def _start_http_server(self):
        """Start HTTP server for network-based GPS sharing"""
        try:
            self.http_server = HTTPServer(('0.0.0.0', self.http_port), GPSHTTPHandler)
            self.http_server.gps_service = self  # type: ignore
            
            self.http_thread = threading.Thread(target=self.http_server.serve_forever, daemon=True)
            self.http_thread.start()
            
            print(f"✓ HTTP server started on port {self.http_port}")
            print(f"  Guest can access GPS at: http://<host-ip>:{self.http_port}/gps")
        except Exception as e:
            print(f"Warning: Failed to start HTTP server: {e}")
            print("GPS will only be available via Guest Properties")
            self.network_mode = False
    
    def _stop_http_server(self):
        """Stop HTTP server"""
        if self.http_server:
            self.http_server.shutdown()
            print("HTTP server stopped")
    
    def _init_vbox(self):
        """Initialize VirtualBox connection"""
        try:
            if vboxapi is not None:
                self.vbox = vboxapi.VirtualBoxManager(None, None)  # type: ignore
                self.machine = self.vbox.vbox.findMachine(self.vm_name)  # type: ignore
                print(f"✓ Connected to VirtualBox VM via SDK: {self.vm_name}")
        except Exception as e:
            print(f"Warning: VirtualBox SDK initialization failed: {e}")
            print("Will use VBoxManage CLI as fallback for guest property operations")
            self.vbox = None
            self.machine = None
    
    def _set_property_via_cli(self, key: str, value: str) -> bool:
        """Set guest property using VBoxManage CLI (fallback method)"""
        try:
            result = subprocess.run(
                ['VBoxManage', 'guestproperty', 'set', self.vm_name, key, value],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                return True
            else:
                print(f"VBoxManage error: {result.stderr.strip()}")
                return False
        except FileNotFoundError:
            print("VBoxManage not found. Please install VirtualBox or run in demo mode.")
            return False
        except subprocess.TimeoutExpired:
            print("VBoxManage command timed out")
            return False
        except Exception as e:
            print(f"Error running VBoxManage: {e}")
            return False
    
    def _set_property_via_sdk(self, key: str, value: str) -> bool:
        """Set guest property using VirtualBox Python SDK"""
        try:
            if self.vbox is None or self.machine is None:
                return False
            
            session = self.vbox.mgr.getSessionObject(self.vbox.vbox)  # type: ignore
            self.machine.lockMachine(session, 1)  # type: ignore  # LockType_Shared = 1
            
            try:
                session.machine.setGuestPropertyValue(key, value)  # type: ignore
                return True
            finally:
                session.unlockMachine()  # type: ignore
                
        except Exception as e:
            print(f"SDK error setting guest property: {e}")
            return False
    
    def set_guest_property(self, key: str, value: str):
        """Set a guest property that can be read from inside the VM"""
        if self.demo_mode:
            print(f"[DEMO] Would set property: {key} = {value}")
            return
        
        success = False
        
        if VBOX_AVAILABLE and self.vbox is not None:
            success = self._set_property_via_sdk(key, value)
        
        if not success:
            success = self._set_property_via_cli(key, value)
        
        if success:
            truncated_value = value[:50] + '...' if len(value) > 50 else value
            print(f"Set property: {key} = {truncated_value}")
        else:
            print(f"Failed to set property: {key}")
    
    def update_location(self):
        """Get current location and update guest property"""
        location = self.gps.get_location()
        location_json = json.dumps(location)
        
        # Update via Guest Properties (for Linux/Windows guests)
        if not self.demo_mode:
            self.set_guest_property("/VirtualBox/GuestInfo/GPS/Location", location_json)
            self.set_guest_property("/VirtualBox/GuestInfo/GPS/Latitude", str(location['latitude']))
            self.set_guest_property("/VirtualBox/GuestInfo/GPS/Longitude", str(location['longitude']))
            self.set_guest_property("/VirtualBox/GuestInfo/GPS/Timestamp", location['timestamp'])
        
        # HTTP server provides data automatically (for macOS and all guests)
        
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] GPS Update:")
        print(f"  Location: {location['latitude']}, {location['longitude']}")
        print(f"  Altitude: {location.get('altitude', 'N/A')} m")
        print(f"  Accuracy: {location.get('accuracy', 'N/A')} m")
        print(f"  Source: {location.get('source', 'unknown')}")
        if self.network_mode:
            print(f"  Available via HTTP: http://<host-ip>:{self.http_port}/gps")
        
        return location
    
    def run(self):
        """Main service loop"""
        print("=" * 70)
        print("VirtualBox GPS Host Service")
        print("=" * 70)
        print(f"VM Name: {self.vm_name}")
        print(f"Mode: {'DEMO' if self.demo_mode else 'PRODUCTION'}")
        print(f"Update Interval: {self.interval} seconds")
        print(f"VirtualBox SDK: {'Available' if VBOX_AVAILABLE else 'Not Available'}")
        if not self.demo_mode:
            if VBOX_AVAILABLE and self.vbox is not None:
                print(f"Guest Properties: SDK (with VBoxManage CLI fallback)")
            else:
                print(f"Guest Properties: VBoxManage CLI only")
        if self.network_mode:
            print(f"Network Mode: Enabled (HTTP server on port {self.http_port})")
            print(f"  → macOS guests: Use --host <host-ip> on guest client")
            print(f"  → Linux/Windows: Can use Guest Properties OR network mode")
        print("=" * 70)
        print("\nStarting GPS location sharing...")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                self.update_location()
                time.sleep(self.interval)
        except KeyboardInterrupt:
            print("\n\nStopping GPS service...")
            if self.network_mode:
                self._stop_http_server()
            print("Service stopped.")


def main():
    parser = argparse.ArgumentParser(
        description='VirtualBox GPS Host Service - Share GPS location with guest VMs'
    )
    parser.add_argument(
        '--vm',
        type=str,
        default='MyVM',
        help='Name of the VirtualBox VM (default: MyVM)'
    )
    parser.add_argument(
        '--demo',
        action='store_true',
        help='Run in demo mode with simulated GPS data'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=5,
        help='Update interval in seconds (default: 5)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=8089,
        help='HTTP server port for network mode (default: 8089)'
    )
    parser.add_argument(
        '--no-network',
        action='store_true',
        help='Disable network mode (Guest Properties only)'
    )
    
    args = parser.parse_args()
    
    service = VBoxGPSService(
        vm_name=args.vm,
        demo_mode=args.demo,
        interval=args.interval,
        network_mode=not args.no_network,
        http_port=args.port
    )
    service.run()


if __name__ == '__main__':
    main()
