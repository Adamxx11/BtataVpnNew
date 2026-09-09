# Batata VPN - Testing Guide

## Unit Tests (Can Run on Linux/Cloud)

Run all unit tests:

```bash
python -m pytest tests/ -v
```

Or use the test runner:

```bash
python run_tests.py
```

### Test Coverage

**Config Manager Tests** (`test_config_manager.py`):
- ✓ Loading valid/invalid config files
- ✓ Config validation (required fields, format)
- ✓ Tunnel name extraction from filename
- ✓ Private key extraction
- ✓ Endpoint validation
- ✓ Key format validation (WireGuard base64)
- ✓ CIDR address validation
- ✓ Endpoint (IP:port) validation
- ✓ Sanitization for logging (private key masking)

**IP Service Tests** (`test_ip_service.py`):
- ✓ Public IP fetching (mock API)
- ✓ IP fetch failure handling
- ✓ Tunnel connection verification (IP changed)
- ✓ Tunnel verification (IP unchanged)
- ✓ DNS leak detection
- ✓ IPv6 status detection

**WireGuard Manager Tests** (`test_wireguard_manager.py`):
- ✓ Tunnel name extraction
- ✓ Admin privilege checking
- ✓ WireGuard installation detection
- ✓ Tunnel installation (mocked CLI calls)
- ✓ Tunnel disconnection
- ✓ Service status checking
- ✓ Error handling

## Integration Tests (Light Testing)

Run integration tests (checks config, IP service, WireGuard detection):

```bash
python tests/integration_test.py
```

This verifies:
- Config file parsing works
- WireGuard is installed (if on Windows)
- Admin privileges are available (if on Windows)
- Public IP fetching works
- Leak detection functions work

## End-to-End Testing (Requires Windows 10/11)

**IMPORTANT:** Full VPN functionality can only be tested on Windows 10/11 with:
- WireGuard for Windows installed
- Administrator privileges
- Real VPN server configured
- Active internet connection

### Manual Testing Checklist (Windows 10/11)

1. **Setup Phase:**
   - [ ] Install Python 3.9+
   - [ ] Install WireGuard for Windows
   - [ ] Clone repository
   - [ ] Create virtual environment
   - [ ] Install dependencies: `pip install -r requirements.txt`
   - [ ] Run server setup script on Linux VPS
   - [ ] Obtain client.conf file

2. **Application Start:**
   - [ ] Run `python main.py` as Administrator
   - [ ] Check "WireGuard detected" message
   - [ ] Check "Administrator privileges" message

3. **Config Loading:**
   - [ ] Click "Load Config"
   - [ ] Select client.conf file
   - [ ] Verify config loads successfully
   - [ ] Verify public IP is fetched
   - [ ] Note the initial public IP (before VPN)

4. **Connection:**
   - [ ] Click "CONNECT" button
   - [ ] Wait for tunnel to activate
   - [ ] Verify status changes to "Connected"
   - [ ] Verify button changes to "DISCONNECT"
   - [ ] **Verify public IP CHANGED**
   - [ ] Verify new IP is server's external IP (not original)
   - [ ] Check DNS/IPv6 status

5. **Connection Verification:**
   - [ ] Open web browser
   - [ ] Visit https://whatismyipaddress.com/
   - [ ] Confirm shown IP matches application's displayed IP
   - [ ] Confirm it's NOT your original ISP IP
   - [ ] Confirm it IS the VPN server's IP

6. **Disconnection:**
   - [ ] Click "DISCONNECT" button
   - [ ] Wait for tunnel to deactivate
   - [ ] Verify status changes to "Disconnected"
   - [ ] Verify button changes to "CONNECT"
   - [ ] **Verify public IP REVERTED**
   - [ ] Verify new IP matches original IP from step 3

7. **Repeat Connection/Disconnection:**
   - [ ] Connect again
   - [ ] Verify IP changes to server IP
   - [ ] Disconnect
   - [ ] Verify IP reverts to original
   - [ ] Repeat 2-3 times to ensure stability

8. **Error Handling:**
   - [ ] Load config, then disable internet connection
   - [ ] Try to connect
   - [ ] Verify appropriate error message
   - [ ] Restore internet connection
   - [ ] Connect successfully

9. **Admin Check:**
   - [ ] Run application WITHOUT admin privileges
   - [ ] Verify warning about administrator requirements
   - [ ] Verify CONNECT button disabled
   - [ ] Close and restart as administrator
   - [ ] Verify CONNECT button enabled

10. **Cleanup:**
    - [ ] Disconnect if connected
    - [ ] Close application
    - [ ] Verify no lingering WireGuard tunnels
    - [ ] Verify IP is back to normal

### Troubleshooting During Testing

**"WireGuard not found"**
- Install WireGuard for Windows from https://www.wireguard.com/install/
- Restart application

**"Administrator privileges required"**
- Close application
- Right-click main.py → "Run as administrator"
- Or open Command Prompt as admin, then: `python main.py`

**"Connection failed — IP unchanged"**
- Check server is running: `sudo systemctl status wg-quick@wg0`
- Check firewall isn't blocking UDP 51820
- Check server has internet connectivity
- Verify server endpoint IP in config is correct

**"Tunnel installed but not active"**
- Check WireGuard GUI — tunnel should appear as "Active"
- Check Windows logs: Event Viewer → WireGuard
- Restart WireGuard service

**Public IP didn't change after 30 seconds**
- Wait longer (WireGuard may take time to establish)
- Check tunnel in WireGuard GUI
- Try `wg show` in admin Command Prompt to see tunnel details

## Test Results Interpretation

### Unit Tests Pass ✓
- All code logic is correct
- Config parsing works
- IP verification works
- Manager error handling works
- **Does NOT verify:** Actual Windows VPN functionality

### Integration Tests Pass ✓
- Config files parse correctly
- IP fetching works
- WireGuard is installed
- Admin privileges available
- **Does NOT verify:** Actual tunnel creation/activation

### Windows Manual Tests Pass ✓
- **VPN actually works**
- Public IP genuinely changes
- Tunnel activates/deactivates
- DNS/IPv6 detection works
- All edge cases handled
- **This is the only real proof of functionality**

## Continuous Testing

After each code change:

1. Run unit tests: `python run_tests.py`
2. If no Windows available, ensure tests pass
3. If Windows available, run manual checklist
4. Commit only after both pass

## Known Limitations

**Cannot test on Linux:**
- wireguard.exe execution (Windows only)
- Windows Service API calls (Windows only)
- Admin privilege elevation (Windows only)
- Actual tunnel interface creation (Windows only)
- Real VPN traffic routing (Windows only)

**Can only test on Windows 10/11:**
- Actual VPN tunnel functionality
- Public IP change through tunnel
- DNS/IPv6 behavior through tunnel
- Service management
- Administrator privilege handling

## Reporting Test Results

**If all tests pass:**
```
✓ Unit tests: PASS (all modules)
✓ Integration tests: PASS (config, IP service, WireGuard detection)
✓ Windows manual tests: PASS (real VPN connection/disconnection)
```

**If some tests fail:**
```
✓ Unit tests: PASS (config parsing, validation)
✗ Integration tests: FAIL (IP service timeout)
✗ Windows manual tests: FAIL (tunnel won't start)

Issue: Public API not responding, check internet connectivity
```
