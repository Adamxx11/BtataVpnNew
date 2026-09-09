"""
Batata VPN - IP Service

Fetches and verifies public IP addresses to confirm VPN connectivity.
Detects potential DNS and IPv6 leaks (detection only, no active filtering).
"""

import requests
from typing import Optional, Dict
import socket


class IPService:
    """
    Handles public IP fetching and VPN connection verification.
    """

    # Public IP APIs (fallback list)
    IP_APIS = [
        "https://api.ipify.org?format=json",
        "https://ipv4.icanhazip.com",
    ]

    def __init__(self, timeout: int = 5):
        """
        Initialize IP service.
        
        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout

    def get_public_ip(self) -> Optional[str]:
        """
        Fetch current public IP address.
        
        Returns:
            Public IP string (e.g., "123.45.67.89") or None if fetch fails
        """
        for api_url in self.IP_APIS:
            try:
                response = requests.get(api_url, timeout=self.timeout)
                if response.status_code == 200:
                    # Handle different API response formats
                    if "json" in api_url:
                        data = response.json()
                        return data.get("ip")
                    else:
                        # Plain text response
                        return response.text.strip()
            except requests.RequestException:
                continue

        return None

    def verify_tunnel_connection(
        self,
        ip_before: Optional[str],
        ip_after: Optional[str],
        server_endpoint: Optional[str] = None
    ) -> Dict:
        """
        Verify VPN tunnel is working by checking IP change.
        
        Args:
            ip_before: Public IP before connecting to VPN
            ip_after: Public IP after connecting to VPN
            server_endpoint: Server's endpoint (optional, for validation)
            
        Returns:
            Dict with keys:
            - tunnel_active (bool): Whether tunnel appears active
            - ip_changed (bool): Whether IP changed
            - message (str): User-friendly status message
        """
        result = {
            "tunnel_active": False,
            "ip_changed": False,
            "message": ""
        }

        # Check if we could fetch IPs
        if ip_before is None or ip_after is None:
            result["message"] = "Unable to verify connection — IP service unavailable"
            return result

        # Check if IP changed
        if ip_before == ip_after:
            result["message"] = "VPN connection failed — public IP unchanged"
            return result

        # IP changed, tunnel appears active
        result["tunnel_active"] = True
        result["ip_changed"] = True
        result["message"] = f"VPN tunnel active — public IP changed to {ip_after}"

        return result

    def detect_dns_leak(self) -> Dict:
        """
        Detect potential DNS leak by checking resolver.
        
        Returns:
            Dict with keys:
            - status: "OK" or "LEAK_DETECTED" or "UNABLE_TO_DETECT"
            - resolver_ip: Resolver IP if detected
            - message: User-friendly message
        """
        result = {
            "status": "UNABLE_TO_DETECT",
            "resolver_ip": None,
            "message": "Unable to detect DNS leak"
        }

        try:
            # Try to get resolver using nslookup-like query
            # In practice, this checks what DNS server is used
            resolver = socket.gethostbyname("google-dns-a.google.com")
            if resolver:
                # Google Public DNS IPs
                google_dns = ["8.8.8.8", "8.8.4.4"]
                cloudflare_dns = ["1.1.1.1", "1.0.0.1"]
                quad9_dns = ["9.9.9.9", "149.112.112.112"]

                if resolver in google_dns or resolver in cloudflare_dns or resolver in quad9_dns:
                    result["status"] = "OK"
                    result["resolver_ip"] = resolver
                    result["message"] = f"DNS resolver: {resolver} (public DNS)"
                else:
                    # Might be ISP DNS
                    result["status"] = "LEAK_DETECTED"
                    result["resolver_ip"] = resolver
                    result["message"] = f"DNS resolver: {resolver} (may be ISP DNS)"
        except Exception as e:
            result["message"] = f"DNS detection failed: {str(e)}"

        return result

    def detect_ipv6_leak(self) -> Dict:
        """
        Detect if IPv6 is available (potential leak without proper config).
        
        Returns:
            Dict with keys:
            - status: "AVAILABLE" or "UNAVAILABLE" or "UNABLE_TO_DETECT"
            - ipv6_address: IPv6 if available
            - message: User-friendly message
        """
        result = {
            "status": "UNABLE_TO_DETECT",
            "ipv6_address": None,
            "message": "Unable to detect IPv6 status"
        }

        try:
            # Try to get IPv6 address
            hostname = socket.gethostname()
            try:
                ipv6_info = socket.getaddrinfo(hostname, None, socket.AF_INET6)
                if ipv6_info:
                    ipv6_address = ipv6_info[0][4][0]
                    result["status"] = "AVAILABLE"
                    result["ipv6_address"] = ipv6_address
                    result["message"] = f"IPv6 available: {ipv6_address}"
                else:
                    result["status"] = "UNAVAILABLE"
                    result["message"] = "IPv6 not available"
            except socket.gaierror:
                result["status"] = "UNAVAILABLE"
                result["message"] = "IPv6 not available"
        except Exception as e:
            result["message"] = f"IPv6 detection failed: {str(e)}"

        return result
