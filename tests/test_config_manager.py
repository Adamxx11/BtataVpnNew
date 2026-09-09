"""
Batata VPN - Config Manager Tests

Tests config file parsing, validation, and tunnel name extraction.
"""

import pytest
import tempfile
import os
from pathlib import Path

# Add parent directory to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config_manager import ConfigManager


class TestConfigManager:
    """
    Test ConfigManager functionality.
    """

    @pytest.fixture
    def valid_config_content(self):
        """
        Create a valid WireGuard config for testing.
        """
        return """[Interface]
PrivateKey = KJjLn0LsUJYvIbBVkXXXXXXXXXXXXXXXXXXXXXX
Address = 10.0.0.2/24
DNS = 1.1.1.1

[Peer]
PublicKey = KXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX=
Endpoint = 203.0.113.45:51820
AllowedIPs = 0.0.0.0/0
PersistentKeepalive = 25
"""

    @pytest.fixture
    def config_file(self, valid_config_content):
        """
        Create a temporary config file.
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.conf', delete=False) as f:
            f.write(valid_config_content)
            f.flush()
            yield f.name
        # Cleanup
        os.unlink(f.name)

    def test_load_valid_config(self, config_file):
        """
        Test loading a valid config file.
        """
        manager = ConfigManager()
        assert manager.load_config(config_file) is True

    def test_load_nonexistent_config(self):
        """
        Test loading a non-existent config file.
        """
        manager = ConfigManager()
        assert manager.load_config("/nonexistent/path/config.conf") is False

    def test_validate_config_with_missing_interface(self, config_file):
        """
        Test config validation with missing [Interface] section.
        """
        manager = ConfigManager()
        manager.config = {"Peer": {"PublicKey": "test", "Endpoint": "1.1.1.1:51820"}}
        assert manager.validate_config() is False

    def test_validate_config_with_missing_peer(self, config_file):
        """
        Test config validation with missing [Peer] section.
        """
        manager = ConfigManager()
        manager.config = {
            "Interface": {
                "PrivateKey": "KJjLn0LsUJYvIbBVkXXXXXXXXXXXXXXXXXXXXXX",
                "Address": "10.0.0.2/24"
            }
        }
        assert manager.validate_config() is False

    def test_get_tunnel_name_from_config(self):
        """
        Test tunnel name extraction from config filename.
        """
        manager = ConfigManager()
        
        # Test normal name
        name1 = manager.get_tunnel_name("/path/to/batata_nl.conf")
        assert name1 == "batata_nl"
        
        # Test name with special characters
        name2 = manager.get_tunnel_name("/path/to/batata-nl-server.conf")
        assert name2 == "batata_nl_server"
        
        # Test name conversion to lowercase
        name3 = manager.get_tunnel_name("/path/to/BATATA_NL.conf")
        assert name3 == "batata_nl"

    def test_get_private_key(self, config_file):
        """
        Test extracting private key from config.
        """
        manager = ConfigManager()
        manager.load_config(config_file)
        
        private_key = manager.get_private_key()
        assert private_key is not None
        assert len(private_key) == 44
        assert private_key == "KJjLn0LsUJYvIbBVkXXXXXXXXXXXXXXXXXXXXXX"

    def test_get_server_endpoint(self, config_file):
        """
        Test extracting server endpoint from config.
        """
        manager = ConfigManager()
        manager.load_config(config_file)
        
        endpoint = manager.get_server_endpoint()
        assert endpoint is not None
        assert endpoint == "203.0.113.45:51820"

    def test_get_dns(self, config_file):
        """
        Test extracting DNS from config.
        """
        manager = ConfigManager()
        manager.load_config(config_file)
        
        dns = manager.get_dns()
        assert dns is not None
        assert dns == "1.1.1.1"

    def test_sanitize_for_logging(self, config_file):
        """
        Test that private key is masked in sanitized output.
        """
        manager = ConfigManager()
        manager.load_config(config_file)
        
        sanitized = manager.sanitize_for_logging()
        
        # Check that PrivateKey is masked
        assert sanitized["Interface"]["PrivateKey"] == "***HIDDEN***"
        
        # Check that other fields are present
        assert sanitized["Interface"]["Address"] == "10.0.0.2/24"
        assert sanitized["Peer"]["Endpoint"] == "203.0.113.45:51820"

    def test_validate_key_format(self):
        """
        Test WireGuard key format validation.
        """
        manager = ConfigManager()
        
        # Valid base64 key (44 chars)
        valid_key = "KJjLn0LsUJYvIbBVkXXXXXXXXXXXXXXXXXXXXXX"
        assert manager._validate_key(valid_key) is True
        
        # Invalid key (too short)
        invalid_key = "short"
        assert manager._validate_key(invalid_key) is False
        
        # Invalid key (invalid characters)
        invalid_key2 = "KJjLn0LsUJYvIbBVkXXXXXXXXXXXXXXXXXXXXX!" + "X" * 43
        assert manager._validate_key(invalid_key2) is False

    def test_validate_address_format(self):
        """
        Test CIDR address validation.
        """
        manager = ConfigManager()
        
        # Valid CIDR
        assert manager._validate_address("10.0.0.2/24") is True
        assert manager._validate_address("192.168.1.1/32") is True
        
        # Invalid CIDR (no slash)
        assert manager._validate_address("10.0.0.2") is False
        
        # Invalid CIDR (bad CIDR value)
        assert manager._validate_address("10.0.0.2/33") is False
        assert manager._validate_address("10.0.0.2/-1") is False

    def test_validate_endpoint_format(self):
        """
        Test endpoint validation.
        """
        manager = ConfigManager()
        
        # Valid endpoints
        assert manager._validate_endpoint("203.0.113.45:51820") is True
        assert manager._validate_endpoint("example.com:51820") is True
        assert manager._validate_endpoint("vpn.example.com:443") is True
        
        # Invalid endpoints
        assert manager._validate_endpoint("203.0.113.45") is False  # No port
        assert manager._validate_endpoint("203.0.113.45:99999") is False  # Port too high
        assert manager._validate_endpoint(":51820") is False  # No host
        assert manager._validate_endpoint("203.0.113.45:abc") is False  # Invalid port
