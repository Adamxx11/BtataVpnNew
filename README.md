# Batata VPN

A simple, standalone VPN client for Windows 10/11 using WireGuard.

## Project Goal

Batata VPN is a minimal MVP that enables Windows users to:

1. Connect to a personal WireGuard VPN server
2. Route internet traffic through the VPN tunnel
3. Verify that their public IP has changed
4. Disconnect and return to normal internet routing

**Key Principle:** No false claims. If something isn't implemented, it won't be advertised.

## Architecture

### Components

```
Windows 10/11 PC
    ↓
 Batata VPN (PyQt6 GUI)
    ↓
WireGuard Tunnel
    ↓
Linux VPN Server (WireGuard)
    ↓
 Internet
```

### What's Included

- **Windows Client** (`src/`) - PyQt6 GUI application
- **Server Setup** (`server/`) - Bash script for Ubuntu/Debian
- **Tests** (`tests/`) - Unit tests for core modules

## Requirements

### For Windows Client

- **Windows 10 64-bit** or **Windows 11 64-bit**
- **Python 3.9+**
- **WireGuard for Windows** (must be installed separately)
  - Download from: https://www.wireguard.com/install/
  - User installs manually (not bundled)

### For VPN Server

- **Ubuntu 20.04 LTS**, **22.04 LTS**, or **Debian 11+**
- Root or sudo access
- Accessible public IP address

## Installation

### Windows Client Setup

1. **Install Python 3.9+**
   - Download from https://www.python.org/downloads/
   - Ensure "Add Python to PATH" is checked during installation

2. **Install WireGuard for Windows**
   - Download from https://www.wireguard.com/install/
   - Run the installer
   - Verify installation: Open Command Prompt and run `where wireguard.exe`

3. **Clone Batata VPN Repository**
   ```bash
   git clone https://github.com/Adamxx11/BtataVpnNew.git
   cd BtataVpnNew
   ```

4. **Create Virtual Environment (Recommended)**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

5. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

6. **Obtain Client Configuration**
   - Run the server setup script (see below)
   - You will receive a `client.conf` file
   - Place it in the `BtataVpnNew` directory or a known location

7. **Run Batata VPN**
   ```bash
   python main.py
   ```
   - Right-click and select "Run as administrator" if prompted
   - Or use Command Prompt with admin privileges

### VPN Server Setup

1. **Prepare a Linux Server**
   - Ubuntu 20.04 LTS, 22.04 LTS, or Debian 11+
   - Root or sudo access
   - Public IP address
   - Recommended: Oracle Cloud Always Free Tier (2 Ampere ARM instances, 24/7)

2. **Run Setup Script**
   ```bash
   sudo bash setup_wireguard.sh
   ```

3. **Follow Script Output**
   - Script will generate WireGuard keys
   - Output will include:
     - Server Public Key
     - Server Endpoint (IP:port)
     - Client configuration template
   - **DO NOT commit these keys to GitHub**
   - Transfer `client.conf` securely to your Windows PC (e.g., via email, secure file transfer)

4. **Verify Server is Running**
   ```bash
   sudo systemctl status wg-quick@wg0
   sudo wg show
   ```

## Usage

### Connecting to VPN

1. **Start Batata VPN** (as Administrator on Windows)
   ```bash
   python main.py
   ```

2. **Load Configuration**
   - GUI will prompt for `client.conf` location
   - Select the config file received from server setup

3. **Click CONNECT**
   - Batata VPN will install the WireGuard tunnel service
   - Tunnel will activate automatically
   - Public IP will be fetched and displayed
   - **Connection is successful only if:**
     - Tunnel is active (shown in status)
     - Public IP has changed (different from original)
     - New IP is verified as server's egress IP

4. **View Status**
   - Status: Connected/Disconnected
   - Public IP: Current external IP
   - DNS Leak Detection: Shows if DNS is leaking
   - IPv6 Status: Shows if IPv6 is available

### Disconnecting from VPN

1. **Click DISCONNECT**
   - Batata VPN will deactivate the tunnel
   - Tunnel service will be removed
   - Public IP will revert to ISP IP

## Security & Privacy

### What's Protected

✓ **Internet traffic** routed through WireGuard tunnel  
✓ **Private keys** never displayed in UI or logs  
✓ **Config content** never logged to files  
✓ **No telemetry** or tracking

### What's NOT Protected (Yet)

✗ **DNS leaks** detected but not actively filtered (MVP)  
✗ **IPv6** detected but not actively blocked (MVP)  
✗ **Kill switch** not implemented (MVP)

### Important Notes

- **Private keys are never displayed in the UI or written to application logs.**
  - Keys exist only in WireGuard config file (required by WireGuard)
  - User must protect `client.conf` like any other private key material

- **No false claims**
  - If a feature isn't implemented, it won't be advertised
  - Detection ≠ Protection

## Platform Support

### Supported

- Windows 10 64-bit (build 1909+)
- Windows 11 64-bit
- Ubuntu 20.04 LTS (server)
- Ubuntu 22.04 LTS (server)
- Debian 11+ (server)

### NOT Supported

- Windows 32-bit
- Windows 7/8/8.1
- macOS (not yet)
- Linux client (use wg-quick directly)
- Any Linux distribution other than Ubuntu/Debian (server)

## Testing

### Unit Tests (Can Run on Linux/Cloud)

```bash
python -m pytest tests/
```

Tests cover:
- Config file parsing
- Key format validation
- IP service logic
- Error handling

### Integration Tests (Requires Windows 10/11)

**Cannot be automated on Linux.** Manual testing on Windows verifies:

1. WireGuard for Windows is detected
2. Tunnel service is created
3. Tunnel activates successfully
4. Public IP changes
5. New IP matches server's egress IP
6. DNS/IPv6 detection works
7. Tunnel deactivates cleanly
8. Public IP reverts to ISP IP

## Troubleshooting

### "WireGuard not found" Error

**Problem:** Batata VPN cannot find `wireguard.exe`  
**Solution:**
1. Install WireGuard for Windows from https://www.wireguard.com/install/
2. Run command prompt as administrator
3. Verify: `where wireguard.exe` (should return a path)
4. Restart Batata VPN

### "Administrator privileges required" Error

**Problem:** Cannot create tunnel without admin rights  
**Solution:**
1. Run Batata VPN as administrator
2. Right-click `main.py` → "Run as administrator"
3. Or open Command Prompt as admin, then: `python main.py`

### "Public IP unchanged" After Connect

**Problem:** Tunnel activated but IP didn't change  
**Solution:**
1. Check server is running: `sudo systemctl status wg-quick@wg0`
2. Check tunnel is active on Windows:
   - Open WireGuard GUI → should show tunnel as "Active"
   - Or: `wg show` in admin Command Prompt
3. Check firewall isn't blocking traffic
4. Verify server has internet connectivity

### Server Setup Script Fails

**Problem:** `setup_wireguard.sh` exits with error  
**Solution:**
1. Ensure you're running on Ubuntu/Debian
2. Run with root: `sudo bash setup_wireguard.sh`
3. Check internet connectivity: `ping 8.8.8.8`
4. Check disk space: `df -h`
5. Review error messages in script output

## Project Structure

```
BtataVpnNew/
├── main.py                          # Entry point
├── requirements.txt                 # Python dependencies
├── README.md                        # This file
├── LICENSE                          # MIT License
├── .gitignore                       # Git ignore rules
│
├── src/
│   ├── __init__.py
│   ├── wireguard_manager.py         # WireGuard tunnel control
│   ├── config_manager.py            # Config parsing
│   ├── ip_service.py                # IP verification
│   └── ui/
│       ├── __init__.py
│       └── main_window.py           # PyQt6 GUI
│
├── server/
│   ├── setup_wireguard.sh           # Server setup (Ubuntu/Debian)
│   └── README.md                    # Server setup instructions
│
└── tests/
    ├── __init__.py
    ├── test_config_manager.py       # Config tests
    ├── test_ip_service.py           # IP service tests
    └── test_wireguard_manager.py    # Manager tests
```

## Development

### Running Tests

```bash
python -m pytest tests/ -v
```

### Code Style

- Python PEP 8
- Type hints where applicable
- Descriptive variable/function names
- Comments for complex logic

### Contributing

Contributions welcome! Please:
1. Test on Windows 10/11 before submitting
2. Don't add telemetry or analytics
3. Be honest about what's actually implemented
4. Never commit private keys or secrets

## License

MIT License - See LICENSE file for details

## Disclaimer

Batata VPN is provided as-is for personal use. Users are responsible for:
- Complying with local laws and regulations
- Protecting their `client.conf` file
- Ensuring their VPN server is secure
- Understanding the security limitations of this MVP

The developers assume no liability for misuse or legal issues arising from VPN usage.
