# macOS Guest Quick Start Guide

This guide explains how to use the VirtualBox GPS Plugin with **macOS as a guest operating system**.

## Important: macOS Guest Compatibility

VirtualBox Guest Additions **do not work properly on macOS guests**, which means the standard Guest Properties method won't work. This plugin now includes **network mode** specifically to support macOS guests!

## How It Works (Network Mode)

Instead of using Guest Properties, the plugin uses a simple HTTP server:

```
┌─────────────────┐          ┌─────────────────┐
│   Host Machine  │          │  macOS Guest VM │
│                 │          │                 │
│ GPS Host Service│          │  GPS Client     │
│ (HTTP Server)   │◄────────►│  (HTTP Client)  │
│ Port 8089       │  Network │                 │
└─────────────────┘          └─────────────────┘
```

## Step 1: Find Your Host IP Address

You need to know the IP address of your host machine that's accessible from the guest VM.

### Option A: Use Host-Only Network (Recommended)

1. In VirtualBox, configure a Host-Only network adapter for your macOS VM:
   - VM Settings → Network → Adapter 2
   - Enable Network Adapter
   - Attached to: Host-Only Adapter

2. Find the host IP on the host-only network:
   
   **On Windows host:**
   ```cmd
   ipconfig
   # Look for "VirtualBox Host-Only Network" adapter
   # Example: 192.168.56.1
   ```
   
   **On Linux host:**
   ```bash
   ip addr show vboxnet0
   # Look for inet address
   # Example: 192.168.56.1
   ```
   
   **On macOS host:**
   ```bash
   ifconfig vboxnet0
   # Look for inet address
   # Example: 192.168.56.1
   ```

### Option B: Use NAT with Port Forwarding

If using NAT, the guest can access the host at the special address:
- **IP:** `10.0.2.2` (default NAT gateway address)
- Configure port forwarding if needed

### Option C: Use Bridged Network

With bridged networking, find your host's actual IP address on the local network:
```bash
# The IP will be something like 192.168.1.100
```

## Step 2: Start the Host Service (on Host Machine)

On your host machine (Windows, Linux, or macOS), run:

```bash
python3 vbox_gps_host.py --demo --vm "YourMacOSVM"
```

You should see output like:

```
======================================================================
VirtualBox GPS Host Service
======================================================================
VM Name: YourMacOSVM
Mode: DEMO
Update Interval: 5 seconds
VirtualBox SDK: Available
Guest Properties: SDK (with VBoxManage CLI fallback)
Network Mode: Enabled (HTTP server on port 8089)
  → macOS guests: Use --host <host-ip> on guest client
  → Linux/Windows: Can use Guest Properties OR network mode
======================================================================

✓ HTTP server started on port 8089
  Guest can access GPS at: http://<host-ip>:8089/gps

Starting GPS location sharing...
```

**Important:** Note the port number (default: 8089). The HTTP server is now running!

## Step 3: Start the Guest Client (inside macOS VM)

Inside your macOS guest VM, run the client with the `--host` option:

```bash
python3 vbox_gps_guest.py --host 192.168.56.1
```

Replace `192.168.56.1` with your actual host IP address from Step 1.

You should see:

```
======================================================================
VirtualBox GPS Guest Client
======================================================================
Network mode: Will connect to http://192.168.56.1:8089/gps
Mode: PRODUCTION
Connection: HTTP (http://192.168.56.1:8089/gps)
  ✓ Compatible with macOS guests
Update Interval: 5 seconds
======================================================================

Listening for GPS location updates...
Press Ctrl+C to stop

[2025-10-21 10:30:15] GPS Location Received:
  Latitude:  37.779234
  Longitude: -122.425678
  Altitude:  45.23 m
  Accuracy:  12.45 m
  Timestamp: 2025-10-21T10:30:15Z
  Source:    simulated
```

🎉 **Success!** You're now receiving GPS data in your macOS guest!

## Command-Line Options

### Host Service

```bash
python3 vbox_gps_host.py [OPTIONS]

Options:
  --vm NAME           VirtualBox VM name (default: MyVM)
  --demo              Run in demo mode with simulated GPS
  --interval N        Update interval in seconds (default: 5)
  --port N            HTTP server port (default: 8089)
  --no-network        Disable network mode (not recommended for macOS)
```

### Guest Client

```bash
python3 vbox_gps_guest.py [OPTIONS]

Options:
  --host IP           Host IP address (REQUIRED for macOS guests)
  --port N            HTTP server port (default: 8089)
  --interval N        Update interval in seconds (default: 5)
  --once              Get location once and exit
  --demo              Run in demo mode (testing only)
```

## Complete Example

### Example 1: Using Host-Only Network

**Host (Windows):**
```bash
# Find host-only IP
ipconfig
# Shows: VirtualBox Host-Only Network: 192.168.56.1

# Start GPS host service
python vbox_gps_host.py --demo --vm "macOS-Sonoma"
```

**Guest (macOS VM):**
```bash
# Inside the macOS VM
python3 vbox_gps_guest.py --host 192.168.56.1
```

### Example 2: Using NAT Network

**Host:**
```bash
python3 vbox_gps_host.py --demo
```

**Guest (macOS VM):**
```bash
# Use the NAT gateway address
python3 vbox_gps_guest.py --host 10.0.2.2
```

### Example 3: Custom Port

**Host:**
```bash
python3 vbox_gps_host.py --demo --port 9000
```

**Guest (macOS VM):**
```bash
python3 vbox_gps_guest.py --host 192.168.56.1 --port 9000
```

## Testing the Connection

### Test HTTP Server from Guest

Before running the client, you can test if the HTTP server is accessible:

**In macOS guest terminal:**
```bash
curl http://192.168.56.1:8089/gps
```

You should see JSON output like:
```json
{
  "latitude": 37.7749,
  "longitude": -122.4194,
  "altitude": 50.0,
  "accuracy": 10.0,
  "timestamp": "2025-10-21T10:30:15Z",
  "source": "simulated"
}
```

If you get "Connection refused":
- Check firewall settings on host
- Verify the host IP address
- Ensure the host service is running

## Troubleshooting

### "Network error: Connection refused"

**Cause:** Guest cannot reach host's HTTP server

**Solutions:**
1. **Check firewall** on host machine
   - Windows: Allow Python through Windows Firewall
   - macOS: System Preferences → Security & Privacy → Firewall
   - Linux: `sudo ufw allow 8089`

2. **Verify IP address** is correct
   ```bash
   # In macOS guest, try to ping the host
   ping 192.168.56.1
   ```

3. **Check network adapter** configuration in VirtualBox
   - Make sure Host-Only adapter is enabled
   - Ensure both host and guest are on the same network

### "URLError: [Errno 60] Operation timed out"

**Cause:** Network timeout reaching the host

**Solutions:**
1. Verify host service is running
2. Check if a different port is needed (try `--port 8090`)
3. Try using bridged networking instead of NAT

### "JSON Decode Error"

**Cause:** Receiving invalid data from server

**Solution:**
- Restart the host service
- Check that you're connecting to the correct URL

### Firewall Configuration

**Windows Host:**
```powershell
# Allow Python through firewall
netsh advfirewall firewall add rule name="VBox GPS" dir=in action=allow protocol=TCP localport=8089
```

**macOS Host:**
```bash
# Firewall usually allows localhost connections
# For external connections, add Python to firewall allowed apps
```

**Linux Host:**
```bash
# Using UFW
sudo ufw allow 8089/tcp

# Using firewalld
sudo firewall-cmd --add-port=8089/tcp --permanent
sudo firewall-cmd --reload
```

## Integration with macOS Apps

You can integrate GPS data into your macOS applications:

### Swift Example

```swift
import Foundation

func getGPSLocation(hostIP: String = "192.168.56.1", port: Int = 8089) -> [String: Any]? {
    let url = URL(string: "http://\(hostIP):\(port)/gps")!
    
    do {
        let data = try Data(contentsOf: url)
        let json = try JSONSerialization.jsonObject(with: data) as? [String: Any]
        return json
    } catch {
        print("Error: \(error)")
        return nil
    }
}

// Usage
if let location = getGPSLocation() {
    if let lat = location["latitude"] as? Double,
       let lon = location["longitude"] as? Double {
        print("Location: \(lat), \(lon)")
    }
}
```

### Python Example (inside macOS guest)

```python
import requests
import json

def get_gps():
    response = requests.get('http://192.168.56.1:8089/gps')
    return response.json()

location = get_gps()
print(f"Lat: {location['latitude']}, Lon: {location['longitude']}")
```

## Performance Notes

- **Latency:** Network mode adds ~10-50ms latency vs. Guest Properties
- **Reliability:** More reliable than Guest Properties on macOS
- **Updates:** Real-time updates every 5 seconds (configurable)

## Comparison: Network Mode vs Guest Properties

| Feature | Network Mode | Guest Properties |
|---------|--------------|------------------|
| **macOS Support** | ✅ Yes | ❌ No |
| **Linux Support** | ✅ Yes | ✅ Yes |
| **Windows Support** | ✅ Yes | ✅ Yes |
| **Setup Complexity** | Medium (need IP) | Low |
| **Latency** | ~10-50ms | ~1-5ms |
| **Firewall Impact** | May need config | None |
| **Guest Additions** | Not required | Required |

## Advantages for macOS Guests

✅ **Works without Guest Additions**
- No need to fight with macOS security settings
- No kernel extensions required
- Compatible with all macOS versions

✅ **Simple HTTP Protocol**
- Use any HTTP client (curl, Python, Swift, etc.)
- Easy to debug and test
- Standard web technology

✅ **Flexible Networking**
- Works with any network configuration
- Can access from multiple VMs simultaneously
- Can even work across physical networks

## Next Steps

- See [USAGE.md](USAGE.md) for advanced usage
- See [README.md](README.md) for architecture details
- Integrate GPS data into your macOS applications

## Getting Real GPS Data

Currently, the plugin uses simulated GPS data. To get real GPS data:

1. **On macOS Host:** Implement CoreLocation integration
2. **On Windows Host:** Use Windows Location API
3. **On Linux Host:** Use GeoClue D-Bus service

Check the main README for future updates on real GPS support.
