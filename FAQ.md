# Batata VPN - Frequently Asked Questions

## Installation & Setup

### Q: What are the system requirements?

**A:** For Windows client:
- Windows 10 64-bit (build 1909+) or Windows 11 64-bit
- Python 3.9 or later
- WireGuard for Windows (separate installation)
- Administrator privileges

For server:
- Ubuntu 20.04+, 22.04+, or Debian 11+
- Root or sudo access
- Public IP address
- Internet connectivity

### Q: Do I need to install Proton VPN?

**A:** No. Batata VPN is completely independent. It only requires:
- Python 3.9+
- WireGuard for Windows (official, free)
- A Linux VPS with WireGuard

### Q: Can I run Batata VPN on Linux?

**A:** Not in the MVP. The client is Windows-only. However, you can:
- Run the server on Linux
- Use `wg-quick` directly on Linux clients

Linux support planned for Phase 10.

### Q: Can I run Batata VPN on macOS?

**A:** Not in the MVP. macOS support planned for Phase 9.

## Configuration

### Q: How do I generate the client.conf file?

**A:** Run the server setup script on your Linux VPS:

```bash
sudo bash setup_wireguard.sh
```

The script will output the complete client configuration. Copy it exactly.

### Q: Where should I save the config file?

**A:** Anywhere on your Windows PC. When you start Batata VPN, click "Load Config" and select it.

Recommended: `C:\Users\YourUsername\Documents\batata_nl.conf`

### Q: Can I use multiple config files?

**A:** Not simultaneously in MVP. You can load different configs sequentially, but Batata VPN only manages one tunnel at a time.

Multi-server support planned for Phase 2.

### Q: What if I lose my config file?

**A:** You'll need to:
1. SSH to your VPS
2. Get the keys from `/etc/wireguard/`
3. Recreate the client.conf manually

Or run the server setup script again and generate new keys.

## Connection & Usage

### Q: Why does it say "Administrator privileges required"?

**A:** Creating VPN tunnels on Windows requires administrator access. This is a Windows security restriction, not a Batata VPN limitation.

**Solution:** 
1. Close Batata VPN
2. Right-click main.py → "Run as administrator"
3. Or open Command Prompt as admin first

### Q: Why is my connection slower with VPN?

**A:** Possible reasons:
1. **Server distance** - VPN server far from you
2. **Server load** - Too many connections
3. **Network congestion** - ISP or server-side
4. **Encryption overhead** - Small (~5-10% typical)
5. **Server specs** - Cheap/overloaded VPS

Try:
- Choosing a closer VPS geographically
- Checking server load: `top` on VPS
- Testing without VPN to compare

### Q: Can I use Batata VPN while working?

**A:** Yes, but be aware:
- All traffic goes through VPN (including work VPN)
- Some work VPNs may conflict
- Performance impact depends on server
- Test thoroughly before relying on it for work

### Q: What happens if the VPN disconnects?

**A:** In MVP:
- Internet traffic continues unencrypted
- No automatic reconnection
- No kill switch

**Solution:**
1. Click DISCONNECT in Batata VPN
2. Click CONNECT to reconnect

Kill switch coming in Phase 2.

## Security & Privacy

### Q: Is my traffic encrypted?

**A:** Yes, between your PC and the VPN server. Your ISP can't see what sites you visit.

BUT:
- The VPN server can see unencrypted traffic
- DNS queries may leak (see "DNS Leak Detection")
- IPv6 may leak if not properly configured

### Q: Does Batata VPN track me?

**A:** No. There's:
- No analytics
- No telemetry
- No tracking pixels
- No phone-home code
- No ad partners
- No data collection

You can audit the code: https://github.com/Adamxx11/BtataVpnNew

### Q: Is my private key safe?

**A:** The private key:
- Never displayed in UI
- Never written to logs
- Never sent anywhere
- Only used by WireGuard locally

**Your responsibility:**
- Protect `client.conf` file (it contains private key)
- Don't share config file
- Don't commit config to Git

### Q: What about DNS leaks?

**A:** Batata VPN:
- ✓ Detects DNS leaks (shows status)
- ✗ Does NOT actively filter DNS (MVP limitation)
- ✗ Does NOT force secure DNS

Phase 3 will add DNS filtering.

### Q: What about IPv6 leaks?

**A:** Batata VPN:
- ✓ Detects IPv6 status
- ✗ Does NOT block IPv6 (MVP limitation)
- ✗ Does NOT tunnel IPv6

Phase 6 will add IPv6 protection.

## Troubleshooting

### Q: Connection says "Public IP unchanged"

**A:** Causes:
1. Server isn't running
2. Firewall blocking port 51820
3. Config endpoint is wrong
4. Network interface issue

**Debug steps:**
```bash
# On server:
sudo systemctl status wg-quick@wg0
sudo ufw status  # Should show 51820/udp ALLOW
```

### Q: "WireGuard not found" error

**A:** WireGuard for Windows isn't installed.

**Solution:**
1. Download from https://www.wireguard.com/install/
2. Install it
3. Restart Batata VPN

### Q: Tunnel installed but says "Connection failed"

**A:** Tunnel installed but handshake didn't happen.

**Debug:**
```bash
# Check tunnel status
wg show batata_nl

# Should show peer with recent "latest handshake"
```

### Q: Application crashes

**A:** Please:
1. Note the error message
2. Check Python version: `python --version`
3. Verify WireGuard installed
4. Report on GitHub with:
   - Windows version
   - Error message
   - Steps to reproduce

### Q: Server setup script fails

**A:** Common issues:
1. Not running with sudo: `sudo bash setup_wireguard.sh`
2. Ubuntu/Debian only (not CentOS, Alpine, etc.)
3. No internet: `ping 8.8.8.8`
4. Insufficient disk space: `df -h`
5. apt broken: `sudo apt --fix-broken install`

## Performance & Optimization

### Q: How much bandwidth does VPN use?

**A:** VPN adds minimal overhead:
- WireGuard: ~100 bytes per packet
- Typical overhead: 2-5%
- Encryption: Minimal CPU impact

### Q: Can I use Batata VPN for gaming?

**A:** Technically yes, but:
- Added latency (depends on server location)
- Potential packet loss
- May violate game terms of service
- Better for casual play than competitive

### Q: Will it work over slow internet?

**A:** Yes, but:
- Connection time longer
- Speed limited by slowest link
- May timeout on very slow connections (<512 Kbps)

## Costs & Hosting

### Q: Is Batata VPN free?

**A:** Batata VPN software is free (MIT License). The VPN server cost depends on hosting:
- Oracle Cloud: Free (Always Free Tier)
- AWS: ~$10-20/month
- DigitalOcean: ~$5/month
- Linode: ~$5/month
- Other: Varies

### Q: What server should I use?

**A:** Recommended for MVP:
- **Free:** Oracle Cloud (Always Free, 24/7)
- **Cheap:** DigitalOcean, Linode ($5/month)
- **Reliable:** AWS, Google Cloud
- **Privacy:** Hetzner (good privacy policies)

Choose based on:
- Geographic location
- Budget
- Privacy policy
- Uptime guarantee

### Q: Will there be cloud hosting?

**A:** Phase 4 (post-MVP) may include managed VPN servers.

No promises, no timeline yet.

## Legal & Compliance

### Q: Is using a VPN legal?

**A:** VPNs are legal in most countries, but:
- Check your country's laws
- Some workplaces prohibit VPNs
- Don't use VPN to hide illegal activity
- Respect terms of service

### Q: Can I use Batata VPN to bypass geo-blocking?

**A:** Technically yes, but:
- Violates most services' terms of service
- May be illegal in some jurisdictions
- Services actively block VPN traffic
- Your account may be banned

Batata VPN is for privacy, not circumvention.

### Q: What about copyright/DMCA?

**A:** Batata VPN:
- ✓ Fully open source
- ✓ No circumvention mechanisms
- ✓ Uses standard VPN protocol (WireGuard)
- ✓ Legal in most jurisdictions

BUT: Using it for piracy is illegal. That's on you.

## Development & Contribution

### Q: Can I contribute?

**A:** Yes! See CONTRIBUTING.md for:
- Bug reports
- Feature requests
- Code contributions
- Documentation

### Q: What's the roadmap?

**A:** See CHANGELOG.md for phases 2-10:
- Phase 2: Kill switch
- Phase 3: Multi-country
- Phase 4: User accounts
- ...
- Phase 10: Linux client

### Q: Can I fork and modify?

**A:** Yes, MIT License allows:
- ✓ Personal modifications
- ✓ Private forks
- ✓ Commercial use (with attribution)
- ✓ Redistribution (with license)

Just include the LICENSE file.

## Support

### Q: Where do I get help?

**A:** Options:
1. Read README.md and TESTING.md
2. Check DEVELOPMENT.md for code questions
3. Search existing issues on GitHub
4. Create new issue if not found
5. Join discussions for ideas

### Q: How do I report a bug?

**A:** Click "Issues" on GitHub:
1. Check existing issues first
2. Click "New Issue"
3. Select "Bug Report" template
4. Provide:
   - Windows/Python version
   - Steps to reproduce
   - Error message/logs

### Q: How do I request a feature?

**A:** Click "Issues" on GitHub:
1. Click "New Issue"
2. Select "Feature Request" template
3. Explain:
   - What problem it solves
   - Why it's important
   - How it should work

## Still Have Questions?

Create a discussion on GitHub:
https://github.com/Adamxx11/BtataVpnNew/discussions
