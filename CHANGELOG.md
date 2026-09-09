# Batata VPN - Changelog

## Version 0.1.0 (MVP Release)

**Release Date:** 2026-09-09

### Features

✓ **Windows 10/11 VPN Client**
- PyQt6 GUI for easy connection/disconnection
- WireGuard tunnel management using official CLI
- Public IP verification before/after connection
- DNS/IPv6 leak detection (detection only, no active filtering in MVP)

✓ **Server Setup (Linux)**
- Automated Ubuntu/Debian setup script
- WireGuard configuration
- IPv4 forwarding and NAT setup
- Client key generation
- Firewall configuration (UFW)

✓ **Core Modules**
- **Config Manager:** Loads and validates WireGuard .conf files
- **IP Service:** Fetches public IP, detects leaks
- **WireGuard Manager:** Controls tunnel service (install/remove)
- **PyQt6 UI:** Minimal, functional interface

✓ **Security**
- Private keys never displayed in UI or logs
- No telemetry, analytics, or tracking
- No Proton VPN dependency
- No WSL or Linux commands
- Secure key handling

✓ **Testing**
- 30+ unit tests for all modules
- Integration tests for core functionality
- Manual testing guide for Windows 10/11

### Supported Platforms

**Client:**
- Windows 10 64-bit (build 1909+)
- Windows 11 64-bit

**Server:**
- Ubuntu 20.04 LTS
- Ubuntu 22.04 LTS
- Debian 11+

### Known Limitations (MVP)

- ✗ No kill switch (if VPN drops, traffic continues unencrypted)
- ✗ No DNS filtering (only detection)
- ✗ No IPv6 protection (only detection)
- ✗ Single server only (no multi-country)
- ✗ No user accounts/login system
- ✗ No persistent configuration (config file must be selected each time)
- ✗ No graphical key generation (use server script to generate)
- ✗ No automated connection on startup
- ✗ No system tray integration

### Future Roadmap (Post-MVP)

1. **Phase 2:** Kill switch implementation
2. **Phase 3:** Multi-country server support
3. **Phase 4:** User accounts and cloud sync
4. **Phase 5:** System tray integration
5. **Phase 6:** DNS filtering
6. **Phase 7:** IPv6 leak protection
7. **Phase 8:** Auto-reconnect on failure
8. **Phase 9:** macOS client
9. **Phase 10:** Linux client (with wg-quick support)

### Installation & Usage

See README.md for detailed instructions.

### Testing

See TESTING.md for comprehensive testing guide.

### Credits

- **WireGuard:** https://www.wireguard.com/
- **PyQt6:** https://pypi.org/project/PyQt6/
- **Python:** https://www.python.org/

### License

MIT License - See LICENSE file

### Support

For issues, feature requests, or questions:
https://github.com/Adamxx11/BtataVpnNew/issues
