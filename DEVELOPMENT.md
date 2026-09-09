# Batata VPN - Development Guide

## Project Structure Overview

```
BtataVpnNew/
├── main.py                          # Application entry point
├── run_tests.py                     # Test runner script
├── requirements.txt                 # Python dependencies
├── README.md                        # User guide and setup instructions
├── TESTING.md                       # Testing procedures and checklist
├── CHANGELOG.md                     # Version history and roadmap
├── LICENSE                          # MIT License
├── .gitignore                       # Git ignore rules (no .conf, .key)
│
├── src/
│   ├── __init__.py                  # Package initialization
│   ├── config_manager.py            # WireGuard config parsing & validation
│   ├── wireguard_manager.py         # Tunnel service management (Windows)
│   ├── ip_service.py                # Public IP fetching & leak detection
│   │
│   └── ui/
│       ├── __init__.py
│       └── main_window.py           # PyQt6 GUI implementation
│
├── server/
│   ├── setup_wireguard.sh           # Ubuntu/Debian server setup script
│   └── README.md                    # Server setup instructions
│
└── tests/
    ├── __init__.py
    ├── test_config_manager.py       # Config manager unit tests
    ├── test_ip_service.py           # IP service unit tests
    ├── test_wireguard_manager.py    # WireGuard manager unit tests
    └── integration_test.py          # Integration tests
```

## Module Responsibilities

### `config_manager.py`
Handles WireGuard configuration file operations:
- Load and parse `.conf` files
- Validate configuration syntax
- Extract tunnel name from filename
- Provide sanitized output for logging (hide private keys)
- Validate key format, CIDR addresses, endpoints

**Key Methods:**
```python
load_config(conf_path: str) -> bool
validate_config() -> bool
get_tunnel_name(conf_path: str) -> str
get_private_key() -> Optional[str]
get_server_endpoint() -> Optional[str]
sanitize_for_logging() -> Dict
```

### `wireguard_manager.py`
Manages WireGuard tunnel lifecycle on Windows 10/11:
- Detect WireGuard installation
- Install tunnel service: `wireguard.exe /installtunnelservice`
- Verify tunnel is active (handshake check)
- Disconnect/remove tunnel: `wireguard.exe /uninstalltunnelservice`
- Check administrator privileges

**Key Methods:**
```python
detect_wireguard() -> bool
install_tunnel_service(conf_path: str) -> Tuple[bool, str]
verify_tunnel_active(tunnel_name: str) -> bool
get_tunnel_status(tunnel_name: str) -> str
disconnect_tunnel(tunnel_name: str) -> Tuple[bool, str]
is_admin() -> bool
requires_admin() -> bool
```

**Important:**
- Uses **official `wireguard.exe` CLI only** (not `wg-quick`, not low-level APIs)
- No ctypes, no named-pipe manipulation
- Handles admin privilege elevation
- Proper error handling and exit codes

### `ip_service.py`
Verifies VPN connectivity and detects leaks:
- Fetch public IP from api.ipify.org (with fallback)
- Verify IP changed after VPN connection
- Detect DNS leaks (checks resolver IP)
- Detect IPv6 status (available/unavailable)

**Key Methods:**
```python
get_public_ip() -> Optional[str]
verify_tunnel_connection(ip_before, ip_after, server_endpoint) -> Dict
detect_dns_leak() -> Dict
detect_ipv6_leak() -> Dict
```

**Important:**
- Detection does NOT mean protection in MVP
- DNS/IPv6 detection only, no active filtering
- Honest messaging (doesn't claim "100% secure")

### `ui/main_window.py`
PyQt6 GUI for user interaction:
- Load WireGuard config file
- Display connection status
- Show public IP (before/after)
- Display DNS/IPv6 status
- Connect/Disconnect buttons
- Error and success messages

**Key Features:**
- Worker threads for non-blocking operations
- WireGuard detection on startup
- Admin privilege checking
- Real-time status updates
- Leak detection display

## Development Workflow

### 1. Local Setup

```bash
# Clone repository
git clone https://github.com/Adamxx11/BtataVpnNew.git
cd BtataVpnNew

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Running Tests

```bash
# Run all unit tests
python run_tests.py

# Or with pytest directly
python -m pytest tests/ -v

# Run integration tests
python tests/integration_test.py
```

### 3. Running Application (Windows 10/11 only)

```bash
# Run as administrator (required for VPN)
python main.py
```

### 4. Code Style

- Follow PEP 8
- Use type hints
- Add docstrings to all functions
- Never log private keys
- Mask sensitive data in debug output

## Key Design Principles

### 1. **Windows-First Client**
- All client code designed for Windows 10/11 64-bit
- No Linux-specific code in Windows paths
- No WSL, no `wg-quick`, no Linux commands
- Official WireGuard for Windows API only

### 2. **Security by Default**
- Private keys never displayed or logged
- No telemetry, analytics, or tracking
- Honest messaging (no false claims)
- Detection ≠ Protection

### 3. **Simplicity First**
- MVP features only
- Single server, single client peer
- No multi-country complexity
- No user accounts
- Functionality > UI polish

### 4. **Honest Error Handling**
- Clear error messages
- No silent failures
- User knows what went wrong
- Easy troubleshooting

### 5. **Verification Required**
- Connection only successful if:
  - Tunnel service starts
  - Handshake established
  - Public IP changes
  - New IP is server's IP (not original)
- Never claim "connected" without proof

## Common Development Tasks

### Adding a New Feature

1. Create module in `src/`
2. Add unit tests in `tests/`
3. Update imports in relevant files
4. Test with: `python run_tests.py`
5. Commit with clear message

### Fixing a Bug

1. Write test that reproduces bug
2. Fix the bug
3. Verify test passes
4. Check all tests still pass
5. Commit with "Fix: ..." message

### Updating Documentation

1. Update relevant `.md` file
2. Keep instructions accurate
3. Test instructions if they're steps
4. Commit with "Docs: ..." message

## Debugging

### Windows Tunnel Issues

```bash
# Check tunnel status
sc query "WireGuardTunnel$batata_nl"

# View tunnel details
wg show batata_nl

# Check Windows event logs
# Event Viewer → Windows Logs → System → WireGuard
```

### IP Service Issues

```python
# Test IP fetching
from src.ip_service import IPService
service = IPService()
print(service.get_public_ip())
```

### Config Parsing Issues

```python
# Test config loading
from src.config_manager import ConfigManager
manager = ConfigManager()
if manager.load_config("path/to/config.conf"):
    print(manager.sanitize_for_logging())
else:
    print("Config invalid")
```

## Testing Philosophy

### Unit Tests (30+)
- **Run on:** Linux, Cloud, Windows
- **Verify:** Logic, validation, error handling
- **Cannot verify:** Windows-specific functionality
- **Command:** `python run_tests.py`

### Integration Tests
- **Run on:** Linux, Cloud, Windows
- **Verify:** Config parsing, IP fetching, WireGuard detection
- **Cannot verify:** Actual tunnel creation
- **Command:** `python tests/integration_test.py`

### Manual Windows Tests
- **Run on:** Windows 10/11 only
- **Verify:** Actual VPN functionality
- **Procedure:** See TESTING.md checklist
- **Result:** Only proof that VPN actually works

## Contribution Guidelines

### Before Submitting PR

1. ✓ All unit tests pass
2. ✓ No private keys in code/logs
3. ✓ No telemetry or tracking
4. ✓ Windows 10/11 compatible
5. ✓ Updated documentation
6. ✓ Clear commit messages
7. ✓ Manual Windows test (if affecting VPN)

### Commit Message Format

```
[Type] Brief description

Optional detailed explanation

Types: Feature, Fix, Docs, Refactor, Test
```

### Examples

```
[Feature] Add kill switch implementation

- Check if tunnel is still active
- Disconnect VPN if tunnel drops
- Reconnect automatically

[Fix] Prevent private key logging

Mask PrivateKey field in sanitize_for_logging()

[Docs] Update Windows setup instructions
```

## Performance Considerations

### Network Calls
- IP fetch: ~2-5 seconds timeout
- DNS lookup: ~1 second timeout
- Tunnel creation: ~15 seconds timeout

### UI Responsiveness
- All network calls in worker threads
- GUI never blocks
- Progress feedback to user

### Memory
- PyQt6: ~50-100 MB
- Python: ~30-50 MB
- Total: ~100-150 MB idle

## Security Considerations

### Private Key Handling
- Never in logs: `[HIDDEN]` in debug output
- Never in UI: Config file displayed, key masked
- Never in memory: Only when necessary
- File permissions: Handled by WireGuard

### API Calls
- IP API: Only fetches public IP (no sensitive data)
- No authentication tokens
- No API keys
- Public APIs only

### User Data
- No user tracking
- No analytics
- No crash reporting
- No telemetry

## Roadmap (Post-MVP)

See CHANGELOG.md for detailed roadmap.

**Priority features:**
1. Kill switch (prevent data leak if VPN drops)
2. DNS filtering
3. IPv6 leak protection
4. Multi-country support
5. System tray integration

## Getting Help

- **Setup issues:** See README.md
- **Testing issues:** See TESTING.md
- **Code questions:** Check docstrings
- **Bug reports:** GitHub issues
- **Feature requests:** GitHub discussions

## License

MIT License - See LICENSE file

## Acknowledgments

- WireGuard team for excellent VPN protocol
- PyQt6 for cross-platform GUI framework
- Community feedback and contributions
