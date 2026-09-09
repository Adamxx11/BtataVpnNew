"""
Batata VPN - IP Service Tests

Tests public IP fetching and VPN connection verification.
"""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ip_service import IPService


class TestIPService:
    """
    Test IPService functionality.
    """

    @pytest.fixture
    def ip_service(self):
        """
        Create IPService instance.
        """
        return IPService(timeout=5)

    @patch('requests.get')
    def test_get_public_ip_success(self, mock_get, ip_service):
        """
        Test successful public IP fetch.
        """
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"ip": "203.0.113.45"}
        mock_get.return_value = mock_response

        ip = ip_service.get_public_ip()
        assert ip == "203.0.113.45"

    @patch('requests.get')
    def test_get_public_ip_failure(self, mock_get, ip_service):
        """
        Test public IP fetch failure.
        """
        # Mock failed API response
        mock_get.side_effect = Exception("Network error")

        ip = ip_service.get_public_ip()
        assert ip is None

    def test_verify_tunnel_connection_ip_changed(self, ip_service):
        """
        Test tunnel verification when IP changed.
        """
        result = ip_service.verify_tunnel_connection(
            ip_before="192.168.1.1",
            ip_after="203.0.113.45",
            server_endpoint="203.0.113.45:51820"
        )

        assert result["tunnel_active"] is True
        assert result["ip_changed"] is True
        assert "changed" in result["message"].lower()

    def test_verify_tunnel_connection_ip_unchanged(self, ip_service):
        """
        Test tunnel verification when IP did not change.
        """
        result = ip_service.verify_tunnel_connection(
            ip_before="192.168.1.1",
            ip_after="192.168.1.1",
            server_endpoint="203.0.113.45:51820"
        )

        assert result["tunnel_active"] is False
        assert result["ip_changed"] is False
        assert "unchanged" in result["message"].lower()

    def test_verify_tunnel_connection_missing_ip(self, ip_service):
        """
        Test tunnel verification when IP fetch failed.
        """
        result = ip_service.verify_tunnel_connection(
            ip_before=None,
            ip_after="203.0.113.45",
            server_endpoint="203.0.113.45:51820"
        )

        assert result["tunnel_active"] is False
        assert result["ip_changed"] is False
        assert "unavailable" in result["message"].lower()

    def test_detect_dns_leak(self, ip_service):
        """
        Test DNS leak detection.
        """
        result = ip_service.detect_dns_leak()
        
        # Result should have required keys
        assert "status" in result
        assert "message" in result
        assert result["status"] in ["OK", "LEAK_DETECTED", "UNABLE_TO_DETECT"]

    def test_detect_ipv6_status(self, ip_service):
        """
        Test IPv6 detection.
        """
        result = ip_service.detect_ipv6_leak()
        
        # Result should have required keys
        assert "status" in result
        assert "message" in result
        assert result["status"] in ["AVAILABLE", "UNAVAILABLE", "UNABLE_TO_DETECT"]
