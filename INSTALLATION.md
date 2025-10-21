# Installation Guide

This guide walks you through installing the VirtualBox GPS Plugin on both host and guest systems.

## Prerequisites

### Host System Requirements
- VirtualBox 6.0 or later
- Python 3.7 or later
- Operating System: Windows, Linux, or macOS

### Guest VM Requirements
- VirtualBox Guest Additions installed
- Python 3.7 or later (for Python client)
- Operating System: Windows, Linux, or macOS

## Step 1: Install VirtualBox (Host)

If you don't already have VirtualBox installed:

### Windows
1. Download from [virtualbox.org](https://www.virtualbox.org/wiki/Downloads)
2. Run the installer
3. Follow the installation wizard

### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install virtualbox
```

### macOS
```bash
brew install --cask virtualbox
```

## Step 2: Install Python (Host)

### Check if Python is installed
```bash
python3 --version
```

### Install Python if needed

**Windows:**
Download from [python.org](https://www.python.org/downloads/)

**Linux:**
```bash
sudo apt install python3 python3-pip
```

**macOS:**
```bash
brew install python3
```

## Step 3: Install the Plugin (Host)

1. Download or clone the plugin files:
```bash
git clone <repository-url>
cd vbox-gps-plugin
```

2. (Optional) Install VirtualBox SDK for better performance:
```bash
pip3 install vboxapi
```

**Note:** The VirtualBox SDK is optional. The plugin will automatically use the VBoxManage command-line tool (installed with VirtualBox) if the SDK is not available. The SDK provides better performance through direct API access, but is not required for production use.

3. Make the scripts executable (Linux/macOS):
```bash
chmod +x vbox_gps_host.py
chmod +x vbox_gps_guest.py
chmod +x demo.py
```

## Step 4: Create a Virtual Machine

If you don't have a VM yet:

1. Open VirtualBox
2. Click "New" to create a VM
3. Configure:
   - Name: MyVM (or any name you prefer)
   - Type: Linux/Windows/macOS
   - Memory: 2048 MB (minimum)
   - Hard disk: Create a virtual hard disk
4. Install your operating system
5. **Important:** Note the VM name - you'll need it for the plugin

## Step 5: Install Guest Additions (Guest VM)

Guest Additions are required for the plugin to work.

### Install in Linux Guest

1. Start the VM
2. In VirtualBox menu: Devices → Insert Guest Additions CD Image
3. Run in terminal:
```bash
sudo apt update
sudo apt install virtualbox-guest-utils virtualbox-guest-x11
```

Or mount and install manually:
```bash
sudo mkdir /mnt/cdrom
sudo mount /dev/cdrom /mnt/cdrom
cd /mnt/cdrom
sudo sh ./VBoxLinuxAdditions.run
```

4. Reboot the VM:
```bash
sudo reboot
```

### Install in Windows Guest

1. Start the VM
2. In VirtualBox menu: Devices → Insert Guest Additions CD Image
3. Open File Explorer, find the CD drive
4. Run `VBoxWindowsAdditions.exe`
5. Follow the installation wizard
6. Reboot the VM

### Install in macOS Guest

1. Start the VM
2. In VirtualBox menu: Devices → Insert Guest Additions CD Image
3. Open the mounted image
4. Run the installer package
5. Reboot the VM

### Verify Installation

In the guest VM, run:
```bash
VBoxControl --version
```

You should see version information. If not, Guest Additions are not properly installed.

## Step 6: Install Plugin in Guest VM

Transfer the `vbox_gps_guest.py` file to your guest VM using one of these methods:

### Method 1: Shared Folder
1. In VirtualBox, configure a shared folder
2. Access it from the guest
3. Copy the file

### Method 2: Network Transfer
```bash
# On guest (if you have network access)
wget http://host-ip/vbox_gps_guest.py
# or use scp, etc.
```

### Method 3: Copy/Paste
1. Enable bidirectional clipboard in VirtualBox settings
2. Copy the file content
3. Paste into a new file in the guest

Then make it executable (Linux/macOS):
```bash
chmod +x vbox_gps_guest.py
```

## Step 7: Verify Installation

### On Host

Test in demo mode:
```bash
python3 vbox_gps_host.py --demo
```

You should see GPS updates being generated.

### On Guest

Test in demo mode:
```bash
python3 vbox_gps_guest.py --demo
```

You should see GPS location data being displayed.

## Step 8: Get Your VM Name

The plugin needs your exact VM name. Get it with:

```bash
VBoxManage list vms
```

Output example:
```
"MyVM" {12345678-1234-1234-1234-123456789abc}
"Ubuntu_Test" {87654321-4321-4321-4321-cba987654321}
```

Use the name in quotes (e.g., "MyVM") when running the plugin.

## Troubleshooting

### "VBoxControl not found" in guest
- Guest Additions are not installed or not in PATH
- Reinstall Guest Additions
- Try full path: `/usr/bin/VBoxControl` (Linux)

### "vboxapi not found" on host
- This is normal and expected
- The plugin will automatically use VBoxManage CLI instead
- For better performance (optional), install: `pip3 install vboxapi`

### Python version too old
- Upgrade to Python 3.7+
- Or use `python3.11` specifically if available

### Permission denied
- On Linux/macOS: Make scripts executable with `chmod +x`
- Run with `python3` explicitly: `python3 vbox_gps_host.py`

### VM not found
- Check VM name exactly matches: `VBoxManage list vms`
- VM names are case-sensitive
- Use quotes if name has spaces: `--vm "My VM"`

## Next Steps

Once installation is complete, proceed to the [Usage Guide](USAGE.md) to learn how to use the plugin.

## Uninstallation

### Host
```bash
# Remove plugin files
rm -rf vbox-gps-plugin/

# Optionally remove VirtualBox SDK
pip3 uninstall vboxapi
```

### Guest
```bash
# Remove guest client
rm vbox_gps_guest.py

# Optionally remove Guest Additions (not recommended)
# This will affect other VirtualBox features
```
