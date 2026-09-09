"""
Batata VPN - Configuration Manager

Handles loading, parsing, and validation of WireGuard .conf files.
Never logs or displays private keys.
"""

import os
from pathlib import Path
from typing import Dict, Optional
import re


class ConfigManager:
    """
    Manages WireGuard configuration files.
    
    Responsibilities:
    - Load and parse .conf files
    - Extract tunnel name from filename
    - Validate configuration syntax
    - Provide sanitized version for logging (hide private keys)
    """

    # WireGuard config sections
    INTERFACE_SECTION = "[Interface]"
    PEER_SECTION = "[Peer]"

    # Required fields in each section
    REQUIRED_INTERFACE_FIELDS = ["PrivateKey", "Address"]
    REQUIRED_PEER_FIELDS = ["PublicKey", "Endpoint"]

    def __init__(self, conf_path: Optional[str] = None):
        """
        Initialize config manager.
        
        Args:
            conf_path: Path to .conf file (optional, can be loaded later)
        """
        self.conf_path = conf_path
        self.config = {}
        self.tunnel_name = ""

    def load_config(self, conf_path: str) -> bool:
        """
        Load and parse WireGuard configuration file.
        
        Args:
            conf_path: Path to .conf file
            
        Returns:
            True if config loaded successfully, False otherwise
        """
        try:
            if not os.path.exists(conf_path):
                raise FileNotFoundError(f"Config file not found: {conf_path}")

            self.conf_path = conf_path
            self.tunnel_name = self.get_tunnel_name(conf_path)

            # Parse the config file
            self.config = self._parse_config_file(conf_path)

            # Validate the config
            if not self.validate_config():
                return False

            return True

        except Exception as e:
            print(f"Error loading config: {e}")
            return False

    def _parse_config_file(self, conf_path: str) -> Dict:
        """
        Parse WireGuard .conf file into a dictionary.
        
        Returns dict with structure:
        {
            "Interface": {"PrivateKey": "...", "Address": "...", ...},
            "Peer": {"PublicKey": "...", "Endpoint": "...", ...}
        }
        """
        config = {}
        current_section = None

        try:
            with open(conf_path, 'r') as f:
                for line in f:
                    line = line.strip()

                    # Skip empty lines and comments
                    if not line or line.startswith("#"):
                        continue

                    # Check for section headers
                    if line == self.INTERFACE_SECTION:
                        current_section = "Interface"
                        config[current_section] = {}
                        continue
                    elif line == self.PEER_SECTION:
                        current_section = "Peer"
                        config[current_section] = {}
                        continue

                    # Parse key-value pairs
                    if current_section and "=" in line:
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.strip()

                        # Store the value (don't print it)
                        config[current_section][key] = value

            return config

        except Exception as e:
            print(f"Error parsing config file: {e}")
            return {}

    def validate_config(self) -> bool:
        """
        Validate WireGuard configuration.
        
        Checks:
        - [Interface] section exists
        - Required Interface fields present
        - [Peer] section exists
        - Required Peer fields present
        
        Returns:
            True if valid, False otherwise
        """
        if not self.config:
            print("Error: Config is empty")
            return False

        # Check Interface section
        if "Interface" not in self.config:
            print("Error: [Interface] section not found")
            return False

        interface = self.config["Interface"]
        for field in self.REQUIRED_INTERFACE_FIELDS:
            if field not in interface:
                print(f"Error: Required field '{field}' missing in [Interface]")
                return False

        # Validate PrivateKey format (base64, 44 characters)
        if not self._validate_key(interface.get("PrivateKey")):
            print("Error: Invalid PrivateKey format")
            return False

        # Validate Address format (CIDR notation)
        if not self._validate_address(interface.get("Address")):
            print("Error: Invalid Address format (expected CIDR, e.g., 10.0.0.2/24)")
            return False

        # Check Peer section
        if "Peer" not in self.config:
            print("Error: [Peer] section not found")
            return False

        peer = self.config["Peer"]
        for field in self.REQUIRED_PEER_FIELDS:
            if field not in peer:
                print(f"Error: Required field '{field}' missing in [Peer]")
                return False

        # Validate PublicKey format
        if not self._validate_key(peer.get("PublicKey")):
            print("Error: Invalid PublicKey format")
            return False

        # Validate Endpoint format (IP:port or hostname:port)
        if not self._validate_endpoint(peer.get("Endpoint")):
            print("Error: Invalid Endpoint format (expected IP:port or hostname:port)")
            return False

        return True

    @staticmethod
    def _validate_key(key: str) -> bool:
        """
        Validate WireGuard key format (base64, 44 characters).
        """
        if not key:
            return False
        # WireGuard keys are 44 characters base64
        return len(key) == 44 and all(c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=' for c in key)

    @staticmethod
    def _validate_address(address: str) -> bool:
        """
        Validate CIDR notation address (e.g., 10.0.0.2/24).
        """
        if not address:
            return False
        # Simple check: should have one slash and valid IP-like format
        if "/" not in address:
            return False
        parts = address.split("/")
        if len(parts) != 2:
            return False
        ip_part, cidr_part = parts
        try:
            # Check CIDR range
            cidr = int(cidr_part)
            if not (0 <= cidr <= 32):
                return False
            # Simple IP check (at least 3 dots)
            if ip_part.count(".") != 3:
                return False
            return True
        except ValueError:
            return False

    @staticmethod
    def _validate_endpoint(endpoint: str) -> bool:
        """
        Validate endpoint format (IP:port or hostname:port).
        """
        if not endpoint:
            return False
        if ":" not in endpoint:
            return False
        parts = endpoint.rsplit(":", 1)
        if len(parts) != 2:
            return False
        host, port = parts
        try:
            port_num = int(port)
            if not (1 <= port_num <= 65535):
                return False
            # Host should not be empty
            if not host:
                return False
            return True
        except ValueError:
            return False

    def get_tunnel_name(self, conf_path: str) -> str:
        """
        Extract tunnel name from config filename.
        
        Example: /path/to/batata_nl.conf → "batata_nl"
        
        Returns:
            Tunnel name (lowercase, alphanumeric + underscore)
        """
        filename = Path(conf_path).stem  # Get filename without extension
        # Convert to lowercase and remove invalid characters
        tunnel_name = re.sub(r'[^a-zA-Z0-9_]', '_', filename).lower()
        return tunnel_name

    def get_interface_section(self) -> Dict:
        """
        Get [Interface] section.
        
        Returns:
            Interface configuration dict
        """
        return self.config.get("Interface", {})

    def get_peer_section(self) -> Dict:
        """
        Get [Peer] section.
        
        Returns:
            Peer configuration dict
        """
        return self.config.get("Peer", {})

    def get_private_key(self) -> Optional[str]:
        """
        Get private key from [Interface] section.
        
        Returns:
            Private key or None if not found
        """
        return self.get_interface_section().get("PrivateKey")

    def get_server_endpoint(self) -> Optional[str]:
        """
        Get VPN server endpoint from [Peer] section.
        
        Returns:
            Endpoint (IP:port) or None if not found
        """
        return self.get_peer_section().get("Endpoint")

    def get_dns(self) -> Optional[str]:
        """
        Get DNS servers from [Interface] section (optional).
        
        Returns:
            DNS servers (comma-separated) or None if not set
        """
        return self.get_interface_section().get("DNS")

    def sanitize_for_logging(self) -> Dict:
        """
        Return config with private keys masked for safe logging.
        
        Returns:
            Sanitized config dict (PrivateKey → "***HIDDEN***")
        """
        sanitized = {}
        for section, fields in self.config.items():
            sanitized[section] = {}
            for key, value in fields.items():
                if key == "PrivateKey" or key == "preshared_key":
                    sanitized[section][key] = "***HIDDEN***"
                else:
                    sanitized[section][key] = value
        return sanitized

    def __repr__(self) -> str:
        """
        String representation (sanitized, no private keys).
        """
        return f"ConfigManager(tunnel={self.tunnel_name}, config={self.sanitize_for_logging()})"
