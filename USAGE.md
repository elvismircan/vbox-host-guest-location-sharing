# Usage Guide

This guide explains how to use the VirtualBox GPS Plugin after installation.

## Quick Start

### Demo Mode (No VirtualBox Required)

Test the plugin without VirtualBox or real GPS hardware:

**Terminal 1 - Host Service:**
```bash
python3 vbox_gps_host.py --demo
```

**Terminal 2 - Guest Client:**
```bash
python3 vbox_gps_guest.py --demo
```

Both will display simulated GPS data independently.

### Interactive Demo

Run a complete demonstration showing host-to-guest communication:

```bash
python3 demo.py
```

This simulates the complete workflow in a single process.

## Production Usage

### Step 1: Start Your VM

```bash
# Start the VM (if not running)
VBoxManage startvm "MyVM"

# Or start it from VirtualBox GUI
```

### Step 2: Start the Host Service

On your host machine:

```bash
python3 vbox_gps_host.py --vm "MyVM" --interval 5
```

Replace "MyVM" with your actual VM name.

**Output:**
```
============================================================
VirtualBox GPS Host Service
============================================================
VM Name: MyVM
Mode: PRODUCTION
Update Interval: 5 seconds
VirtualBox SDK: Available
============================================================

Starting GPS location sharing...
Press Ctrl+C to stop

[2025-10-21 10:30:15] GPS Update:
  Location: 37.779234, -122.425678
  Altitude: 45.23 m
  Accuracy: 12.45 m
  Source: simulated
```

### Step 3: Start the Guest Client

Inside your guest VM:

```bash
python3 vbox_gps_guest.py --interval 5
```

**Output:**
```
============================================================
VirtualBox GPS Guest Client
============================================================
Mode: PRODUCTION
Update Interval: 5 seconds
============================================================

Listening for GPS location updates...
Press Ctrl+C to stop

[2025-10-21 10:30:16] GPS Location Received:
  Latitude:  37.779234
  Longitude: -122.425678
  Altitude:  45.23 m
  Accuracy:  12.45 m
  Timestamp: 2025-10-21T10:30:15Z
  Source:    simulated
```

## Command-Line Options

### Host Service (`vbox_gps_host.py`)

```bash
python3 vbox_gps_host.py [OPTIONS]
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--vm NAME` | VirtualBox VM name | MyVM |
| `--demo` | Run in demo mode with simulated GPS | False |
| `--interval N` | Update interval in seconds | 5 |

**Examples:**

```bash
# Production mode with custom VM
python3 vbox_gps_host.py --vm "Ubuntu_Test" --interval 10

# Demo mode with fast updates
python3 vbox_gps_host.py --demo --interval 2

# Default settings
python3 vbox_gps_host.py
```

### Guest Client (`vbox_gps_guest.py`)

```bash
python3 vbox_gps_guest.py [OPTIONS]
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--demo` | Run in demo mode | False |
| `--interval N` | Update interval in seconds | 5 |
| `--once` | Get location once and exit | False |

**Examples:**

```bash
# Production mode with custom interval
python3 vbox_gps_guest.py --interval 10

# Get location once and exit
python3 vbox_gps_guest.py --once

# Demo mode
python3 vbox_gps_guest.py --demo

# Fast updates
python3 vbox_gps_guest.py --interval 2
```

### Demo Script (`demo.py`)

```bash
python3 demo.py [OPTIONS]
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--duration N` | Demo duration in seconds | 30 |
| `--interval N` | Update interval in seconds | 3 |

**Examples:**

```bash
# Run for 1 minute
python3 demo.py --duration 60

# Run with fast updates
python3 demo.py --interval 1

# Long demo with slow updates
python3 demo.py --duration 300 --interval 10
```

## Use Cases

### 1. Continuous Location Monitoring

Monitor location changes in real-time:

**Host:**
```bash
python3 vbox_gps_host.py --vm "MyVM" --interval 1
```

**Guest:**
```bash
python3 vbox_gps_guest.py --interval 1
```

### 2. One-Time Location Query

Get current location and exit:

**Guest:**
```bash
python3 vbox_gps_guest.py --once
```

### 3. Background Service

Run the host service in the background:

**Linux/macOS:**
```bash
nohup python3 vbox_gps_host.py --vm "MyVM" > gps_host.log 2>&1 &
```

**Windows:**
```powershell
Start-Process python3 -ArgumentList "vbox_gps_host.py --vm MyVM" -WindowStyle Hidden
```

### 4. Testing and Development

Use demo mode for development:

```bash
# Terminal 1
python3 vbox_gps_host.py --demo --interval 2

# Terminal 2
python3 vbox_gps_guest.py --demo --interval 2
```

## Integration with Applications

### Reading GPS Data from Scripts

**Python Example:**

```python
#!/usr/bin/env python3
import subprocess
import json

def get_gps_location():
    """Get GPS location from VirtualBox guest properties"""
    result = subprocess.run(
        ['VBoxControl', 'guestproperty', 'get', '/VirtualBox/GuestInfo/GPS/Location'],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0 and 'Value:' in result.stdout:
        json_str = result.stdout.split('Value:', 1)[1].strip()
        return json.loads(json_str)
    
    return None

location = get_gps_location()
if location:
    print(f"Current location: {location['latitude']}, {location['longitude']}")
```

**Bash Example:**

```bash
#!/bin/bash
# Get GPS location from guest properties

LOCATION=$(VBoxControl guestproperty get /VirtualBox/GuestInfo/GPS/Location | grep "Value:" | cut -d' ' -f2-)
echo "GPS Location: $LOCATION"

LATITUDE=$(VBoxControl guestproperty get /VirtualBox/GuestInfo/GPS/Latitude | grep "Value:" | cut -d' ' -f2-)
LONGITUDE=$(VBoxControl guestproperty get /VirtualBox/GuestInfo/GPS/Longitude | grep "Value:" | cut -d' ' -f2-)

echo "Coordinates: $LATITUDE, $LONGITUDE"
```

### Available Guest Properties

The plugin exposes these guest properties:

| Property Path | Content | Type |
|---------------|---------|------|
| `/VirtualBox/GuestInfo/GPS/Location` | Full JSON location data | JSON |
| `/VirtualBox/GuestInfo/GPS/Latitude` | Latitude only | Float |
| `/VirtualBox/GuestInfo/GPS/Longitude` | Longitude only | Float |
| `/VirtualBox/GuestInfo/GPS/Timestamp` | ISO 8601 timestamp | String |

**View all GPS properties:**
```bash
VBoxControl guestproperty enumerate | grep GPS
```

## Stopping the Services

### Stop Host Service
Press `Ctrl+C` in the terminal running the host service.

### Stop Guest Client
Press `Ctrl+C` in the terminal running the guest client.

### Kill Background Processes

**Linux/macOS:**
```bash
# Find process
ps aux | grep vbox_gps

# Kill by PID
kill <PID>

# Or kill by name
pkill -f vbox_gps_host.py
```

**Windows:**
```powershell
# Find and kill Python processes
Get-Process python | Where-Object {$_.CommandLine -like "*vbox_gps*"} | Stop-Process
```

## Configuration

### Using config.json

Edit `config.json` to set defaults:

```json
{
  "version": "1.0.0",
  "default_vm": "MyVM",
  "update_interval": 5,
  "demo_mode": true,
  "location": {
    "default_latitude": 37.7749,
    "default_longitude": -122.4194,
    "simulation_variance": 0.01
  }
}
```

### Environment Variables

Set environment variables for configuration:

```bash
export VBOX_GPS_VM="MyVM"
export VBOX_GPS_INTERVAL=5
export VBOX_GPS_DEMO=1
```

Then modify the scripts to read these variables.

## Performance Considerations

### Update Interval

- **Fast (1-2 seconds)**: High CPU usage, very responsive
- **Normal (5 seconds)**: Balanced, recommended for most uses
- **Slow (10+ seconds)**: Low overhead, suitable for background monitoring

### Resource Usage

Typical resource consumption:

| Component | CPU | Memory | Network |
|-----------|-----|--------|---------|
| Host Service | <1% | ~20 MB | None |
| Guest Client | <1% | ~15 MB | None |

### Multiple VMs

To share GPS with multiple VMs simultaneously:

```bash
# Terminal 1 - VM1
python3 vbox_gps_host.py --vm "VM1" --interval 5

# Terminal 2 - VM2
python3 vbox_gps_host.py --vm "VM2" --interval 5

# Terminal 3 - VM3
python3 vbox_gps_host.py --vm "VM3" --interval 5
```

## Troubleshooting

### No Data Received in Guest

1. Verify host service is running
2. Check VM name matches exactly
3. Verify Guest Additions are installed
4. Try demo mode on both sides

### Stale Data

If timestamps are old:

1. Restart the host service
2. Check for errors in host console
3. Verify VM is running
4. Increase update interval if too fast

### High CPU Usage

1. Increase update interval
2. Use `--interval 10` or higher
3. Check for multiple instances running

### Permission Errors

On Linux, add user to vboxusers group:
```bash
sudo usermod -aG vboxusers $USER
# Log out and back in
```

## Advanced Usage

### Logging to File

**Host:**
```bash
python3 vbox_gps_host.py --vm "MyVM" 2>&1 | tee gps_host.log
```

**Guest:**
```bash
python3 vbox_gps_guest.py 2>&1 | tee gps_guest.log
```

### Systemd Service (Linux Host)

Create `/etc/systemd/system/vbox-gps.service`:

```ini
[Unit]
Description=VirtualBox GPS Host Service
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/vbox-gps-plugin
ExecStart=/usr/bin/python3 vbox_gps_host.py --vm "MyVM"
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable vbox-gps
sudo systemctl start vbox-gps
sudo systemctl status vbox-gps
```

## Next Steps

- Integrate GPS data into your applications
- Set up automatic startup services
- Explore the source code for customization
- Contribute improvements to the project

## Support

For issues or questions:
- Check the [README.md](README.md) for architecture details
- Review the [INSTALLATION.md](INSTALLATION.md) for setup help
- Open an issue on the project repository
