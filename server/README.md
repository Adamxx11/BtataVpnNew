# Batata VPN Server Setup

## Prerequisites

- **Ubuntu 20.04 LTS**, **22.04 LTS**, or **Debian 11+**
- Root or sudo access
- Public IP address (static preferred)
- Recommended: Oracle Cloud Always Free Tier (2 Ampere A1 ARM instances, 24/7)

## Quick Setup

```bash
sudo bash setup_wireguard.sh
```

The script will:
1. Detect your Linux distribution (Ubuntu/Debian only)
2. Detect your primary network interface
3. Install WireGuard and tools
4. Enable IPv4 forwarding
5. Generate server and client keys
6. Configure NAT/masquerading
7. Setup firewall rules
8. Generate client configuration
9. Start WireGuard service

## Output

After successful setup, you will see:

```
✓ WireGuard installed
✓ IPv4 forwarding enabled
✓ Server keys generated
✓ Client keys generated
✓ wg0 interface configured
✓ Firewall configured
✓ WireGuard started

--- CLIENT CONFIGURATION ---
Server Public IP: 203.0.113.45
Server Public Key: <server_public_key>
Server Endpoint: 203.0.113.45:51820

Client config:
[Interface]
PrivateKey = <CLIENT_PRIVATE_KEY_HERE>
Address = 10.0.0.2/24
DNS = 1.1.1.1

[Peer]
PublicKey = <server_public_key>
Endpoint = 203.0.113.45:51820
AllowedIPs = 0.0.0.0/0
PersistentKeepalive = 25
```

## Next Steps

1. **Save the output** - Write down or copy the client configuration

2. **Replace placeholder** - In the client config, replace `<CLIENT_PRIVATE_KEY_HERE>` with the actual client private key shown in the output

3. **Save as .conf file** - Save the complete config as `batata_nl.conf` (or any name you prefer)

4. **Transfer to Windows** - Securely transfer `batata_nl.conf` to your Windows PC
   - Email it to yourself
   - Use secure file transfer
   - USB drive
   - Never share the private key publicly

5. **Load in Batata VPN** - On Windows:
   - Run `python main.py` as administrator
   - Select the `batata_nl.conf` file
   - Click CONNECT

## Verification

After setup, verify the server is running:

```bash
# Check WireGuard service status
sudo systemctl status wg-quick@wg0

# View WireGuard interface
sudo wg show

# Check firewall rules
sudo ufw status
```

You should see:
- WireGuard service: `active (exited)`
- Interface `wg0` with listen port 51820
- One peer (your Windows client)
- UFW allowing port 51820/udp

## Troubleshooting

### "Command not found: bash"

**Problem:** Running on non-Ubuntu/Debian system  
**Solution:** This script only supports Ubuntu/Debian. Adapt for your OS.

### "Permission denied"

**Problem:** Not running with sudo  
**Solution:** Run with `sudo bash setup_wireguard.sh`

### "WireGuard installation failed"

**Problem:** apt package manager issue  
**Solution:**
```bash
sudo apt update
sudo apt upgrade
sudo bash setup_wireguard.sh
```

### "wg0 interface not found"

**Problem:** WireGuard service didn't start  
**Solution:**
```bash
sudo systemctl restart wg-quick@wg0
sudo wg show
```

## Security Notes

- **Private keys are NOT printed to console** during setup
- Keys are stored in `/etc/wireguard/` with restricted permissions
- The script only needs to be run once
- Never commit the generated keys to GitHub
- Protect `client.conf` like any private key material
- Change firewall rules if you need to restrict access

## Advanced: Manual Setup

If you need to customize the setup:

1. **Install WireGuard**
   ```bash
   sudo apt update
   sudo apt install -y wireguard wireguard-tools
   ```

2. **Enable IP forwarding**
   ```bash
   echo "net.ipv4.ip_forward=1" | sudo tee -a /etc/sysctl.conf
   sudo sysctl -p
   ```

3. **Generate keys** (replace with actual network interface)
   ```bash
   umask 077
   wg genkey | tee /etc/wireguard/privatekey | wg pubkey > /etc/wireguard/publickey
   wg genkey | tee /tmp/client_private | wg pubkey > /tmp/client_public
   ```

4. **Create wg0.conf** - Edit `/etc/wireguard/wg0.conf`:
   ```
   [Interface]
   PrivateKey = <content of /etc/wireguard/privatekey>
   Address = 10.0.0.1/24
   ListenPort = 51820
   PostUp = iptables -A FORWARD -i wg0 -j ACCEPT; iptables -A FORWARD -o wg0 -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
   PostDown = iptables -D FORWARD -i wg0 -j ACCEPT; iptables -D FORWARD -o wg0 -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE
   
   [Peer]
   PublicKey = <content of /tmp/client_public>
   AllowedIPs = 10.0.0.2/32
   ```

5. **Enable and start WireGuard**
   ```bash
   sudo systemctl enable wg-quick@wg0
   sudo systemctl start wg-quick@wg0
   ```

6. **Setup firewall**
   ```bash
   sudo ufw allow 51820/udp
   sudo ufw enable
   ```

## Support

For issues or questions:
- Check logs: `sudo journalctl -u wg-quick@wg0 -n 50`
- WireGuard docs: https://www.wireguard.com/
- This repository: https://github.com/Adamxx11/BtataVpnNew
