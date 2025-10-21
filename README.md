# VirtualBox GPS Location Plugin

A VirtualBox plugin that shares GPS location data from the host machine to guest virtual machines in real-time.

## Overview

This plugin consists of two components:
- **Host Service** (`vbox_gps_host.py`): Runs on the host machine, captures GPS location data and shares it with guest VMs
- **Guest Client** (`vbox_gps_guest.py`): Runs inside the guest VM, receives location data from the host

## Features

- ✅ Real-time GPS location sharing from host to guest
- ✅ Supports latitude, longitude, altitude, and accuracy
- ✅ Configurable update intervals
- ✅ Demo mode with simulated GPS data for testing
- ✅ Platform-agnostic protocol using VirtualBox Guest Properties
- ✅ Simple command-line interface
- ✅ Automatic timestamp tracking

## How It Works

The plugin uses **VirtualBox Guest Properties** as a communication channel:

1. The host service reads GPS location data from the system
2. It stores the location in VirtualBox guest properties (e.g., `/VirtualBox/GuestInfo/GPS/Location`)
3. The guest client reads these properties from inside the VM
4. Location updates happen at configurable intervals (default: 5 seconds)

## Requirements

### Host Machine
- VirtualBox installed (with VBoxManage CLI)
- Python 3.7+
- VirtualBox SDK for Python (optional, provides better performance)

### Guest VM
- VirtualBox Guest Additions installed
- Python 3.7+ (for the Python client)

## Installation

### 1. Install on Host

```bash
# Clone or download the plugin files
git clone <repository-url>
cd vbox-gps-plugin

# Optional: Install VirtualBox SDK (improves performance)
pip install vboxapi
```

**Note:** The VirtualBox SDK is optional. The plugin will automatically use the VBoxManage command-line tool if the SDK is not available. The SDK provides better performance through direct API access.

### 2. Install on Guest

```bash
# Install VirtualBox Guest Additions (if not already installed)
# On Linux guest:
sudo apt-get install virtualbox-guest-utils

# Copy the guest client to your VM
# (Use shared folders or network transfer)
```

## Usage

### Running the Host Service

**Demo Mode (recommended for testing):**
```bash
python vbox_gps_host.py --demo --vm "MyVM" --interval 5
```

**Production Mode (with real GPS):**
```bash
python vbox_gps_host.py --vm "MyVM" --interval 10
```

**Command-line options:**
- `--vm NAME`: Name of your VirtualBox VM (default: "MyVM")
- `--demo`: Run in demo mode with simulated GPS data
- `--interval SECONDS`: Update interval in seconds (default: 5)

### Running the Guest Client

**Inside the guest VM:**

**Demo Mode:**
```bash
python vbox_gps_guest.py --demo --interval 5
```

**Production Mode:**
```bash
python vbox_gps_guest.py --interval 5
```

**Get location once and exit:**
```bash
python vbox_gps_guest.py --once
```

**Command-line options:**
- `--demo`: Run in demo mode
- `--interval SECONDS`: Update interval in seconds (default: 5)
- `--once`: Get location once and exit

## Example Output

### Host Service Output
```
============================================================
VirtualBox GPS Host Service
============================================================
VM Name: MyVM
Mode: DEMO
Update Interval: 5 seconds
VirtualBox SDK: Not Available
============================================================

Starting GPS location sharing...
Press Ctrl+C to stop

[2025-10-21 10:30:15] GPS Update:
  Location: 37.779234, -122.425678
  Altitude: 45.23 m
  Accuracy: 12.45 m
  Source: simulated
```

### Guest Client Output
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

## Data Format

The GPS location data is shared in JSON format:

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

### Guest Properties Used

- `/VirtualBox/GuestInfo/GPS/Location` - Full JSON location data
- `/VirtualBox/GuestInfo/GPS/Latitude` - Latitude value only
- `/VirtualBox/GuestInfo/GPS/Longitude` - Longitude value only
- `/VirtualBox/GuestInfo/GPS/Timestamp` - Last update timestamp

## Platform-Specific GPS Sources

The plugin is designed to support real GPS data from various platforms:

- **Windows**: Windows Location API
- **Linux**: GeoClue D-Bus service
- **macOS**: CoreLocation framework

*Note: Real GPS integration requires additional platform-specific setup and is currently in development. Use demo mode for testing.*

## Troubleshooting

### "VBoxControl not found" in guest
- Install VirtualBox Guest Additions in your guest VM
- Verify installation: `VBoxControl --version`

### No location data received
- Make sure the host service is running
- Verify the VM name matches: `VBoxManage list vms`
- Check that Guest Additions are properly installed
- Try running both host and guest in demo mode first

### Permission errors
- On Linux hosts, you may need to add your user to the `vboxusers` group
- Run: `sudo usermod -aG vboxusers $USER` and log out/in

## Development

### Testing Demo Mode

Both components can run in demo mode without VirtualBox:

```bash
# Terminal 1 - Host service
python vbox_gps_host.py --demo

# Terminal 2 - Guest client  
python vbox_gps_guest.py --demo
```

### Extending the Plugin

To add support for additional GPS data:

1. Update the `GPSLocationProvider.get_location()` method in `vbox_gps_host.py`
2. Add new guest properties in `VBoxGPSService.update_location()`
3. Update the guest client to read the new properties

## Architecture

```
┌─────────────────────────────────────────┐
│           Host Machine                   │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │  GPS Location Provider              │ │
│  │  (System GPS / Simulated)           │ │
│  └───────────────┬────────────────────┘ │
│                  │                       │
│  ┌───────────────▼────────────────────┐ │
│  │  VBox GPS Host Service             │ │
│  │  - Read GPS data                   │ │
│  │  - Update guest properties         │ │
│  └───────────────┬────────────────────┘ │
│                  │                       │
│         VirtualBox Guest Properties      │
│                  │                       │
│  ┌───────────────▼────────────────────┐ │
│  │      Guest VM                      │ │
│  │                                    │ │
│  │  ┌──────────────────────────────┐ │ │
│  │  │  VBox GPS Guest Client       │ │ │
│  │  │  - Read guest properties     │ │ │
│  │  │  - Display location data     │ │ │
│  │  └──────────────────────────────┘ │ │
│  └────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

## License

MIT License - Feel free to use and modify as needed.

## Contributing

Contributions welcome! Areas for improvement:
- Real GPS integration for Windows/Linux/macOS
- Support for additional location metadata
- GUI interface
- Multiple VM support
- Location history and logging
- Configuration file support

## Support

For issues or questions, please open an issue on the GitHub repository.
