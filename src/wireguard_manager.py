"""
Batata VPN - WireGuard Manager

Manages WireGuard tunnel lifecycle on Windows 10/11.
Uses official wireguard.exe CLI only.
"""

import subprocess
import os
import sys
from pathlib import Path
from typing import Optional, Tuple
import time


class WireGuardManager:
    """
    Manages WireGuard for Windows tunnel operations.
    
    Uses official wireguard.exe CLI:
    - /installtunnelservice <config_path> — Install and start tunnel
    - /uninstalltunnelservice <tunnel_name> — Stop and remove tunnel
    
    Does NOT use:
    - wg-quick (Linux only)
    - Low-level API calls
    - Undocumented mechanisms
    """

    # WireGuard for Windows standard install paths
    WIREGUARD_PATHS = [
        "C:\\Program Files\\WireGuard\\wireguard.exe",
        "C:\\Program Files (x86)\\WireGuard\\wireguard.exe",
    ]

    def __init__(self):
        """
        Initialize WireGuard manager.
        """
        self.wireguard_exe = None
        self.wg_exe = None
        self._detect_wireguard()

    def _detect_wireguard(self) -> bool:
        """
        Detect WireGuard for Windows installation.
        
        Returns:
            True if found, False otherwise
        """
        # Try standard install paths
        for path in self.WIREGUARD_PATHS:
            if os.path.exists(path):
                self.wireguard_exe = path
                # wg.exe is typically in the same directory
                wg_path = os.path.join(os.path.dirname(path), "wg.exe")
                if os.path.exists(wg_path):
                    self.wg_exe = wg_path
                return True

        # Try using 'where' command
        try:
            result = subprocess.run(
                ["where", "wireguard.exe"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                self.wireguard_exe = result.stdout.strip().split("\n")[0]
                # Find wg.exe in same directory
                wg_path = os.path.join(os.path.dirname(self.wireguard_exe), "wg.exe")
                if os.path.exists(wg_path):
                    self.wg_exe = wg_path
                return True
        except Exception:
            pass

        return False

    def detect_wireguard(self) -> bool:
        """
        Check if WireGuard is installed.
        
        Returns:
            True if wireguard.exe found, False otherwise
        """
        return self.wireguard_exe is not None

    def get_tunnel_name_from_config(self, conf_path: str) -> str:
        """
        Extract tunnel name from config filename.
        
        Example: C:\\Users\\User\\batata_nl.conf → "batata_nl"
        
        Args:
            conf_path: Path to config file
            
        Returns:
            Tunnel name (alphanumeric + underscore)
        """
        filename = Path(conf_path).stem  # Get filename without extension
        # Convert to lowercase and keep only valid characters
        tunnel_name = "".join(c.lower() if c.isalnum() or c == "_" else "_" for c in filename)
        return tunnel_name.replace("__", "_").strip("_")

    def is_admin(self) -> bool:
        """
        Check if current process has administrator privileges.
        
        Returns:
            True if running as admin, False otherwise
        """
        try:
            import ctypes
            return ctypes.windll.shell.IsUserAnAdmin()
        except Exception:
            return False

    def install_tunnel_service(self, conf_path: str) -> Tuple[bool, str]:
        """
        Install WireGuard tunnel service using official CLI.
        
        Uses: wireguard.exe /installtunnelservice <config_path>
        
        Args:
            conf_path: Path to .conf file
            
        Returns:
            Tuple (success: bool, message: str)
        """
        if not self.detect_wireguard():
            return False, "WireGuard not found. Install WireGuard for Windows first."

        if not self.is_admin():
            return False, "Administrator privileges required. Run as administrator."

        # Validate config file exists
        if not os.path.exists(conf_path):
            return False, f"Config file not found: {conf_path}"

        # Get tunnel name for later verification
        tunnel_name = self.get_tunnel_name_from_config(conf_path)

        try:
            # Install tunnel service
            result = subprocess.run(
                [self.wireguard_exe, "/installtunnelservice", conf_path],
                capture_output=True,
                text=True,
                timeout=15
            )

            if result.returncode != 0:
                error_msg = result.stderr or result.stdout or "Unknown error"
                return False, f"Failed to install tunnel: {error_msg}"

            # Wait a moment for service to start
            time.sleep(2)

            # Verify tunnel is active
            if not self.verify_tunnel_active(tunnel_name):
                return False, "Tunnel installed but not active. Check logs."

            return True, f"Tunnel '{tunnel_name}' installed and active"

        except subprocess.TimeoutExpired:
            return False, "Tunnel installation timed out"
        except Exception as e:
            return False, f"Error installing tunnel: {str(e)}"

    def verify_tunnel_active(self, tunnel_name: str) -> bool:
        """
        Verify tunnel is actually running (not just installed).
        
        Uses wg.exe to check for handshake/peer connection.
        
        Args:
            tunnel_name: Name of tunnel to check
            
        Returns:
            True if tunnel is active with peer handshake, False otherwise
        """
        if not self.wg_exe:
            # If wg.exe not available, do basic check via service status
            return self._check_service_running(tunnel_name)

        try:
            # Show tunnel details
            result = subprocess.run(
                [self.wg_exe, "show", tunnel_name],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                return False

            # Check for peer presence and handshake
            output = result.stdout
            if "peer" in output.lower() and "latest handshake" in output.lower():
                # Extract latest handshake time
                for line in output.split("\n"):
                    if "latest handshake" in line.lower():
                        # Should not be "never" or very old
                        if "never" not in line.lower():
                            return True

            return False

        except Exception:
            # Fallback: check service status
            return self._check_service_running(tunnel_name)

    def _check_service_running(self, tunnel_name: str) -> bool:
        """
        Check if Windows service is running.
        
        Args:
            tunnel_name: Service name
            
        Returns:
            True if service running, False otherwise
        """
        try:
            # SC query service status
            result = subprocess.run(
                ["sc", "query", f"WireGuardTunnel${tunnel_name}"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                # Check if RUNNING is in output
                if "RUNNING" in result.stdout.upper():
                    return True

            return False

        except Exception:
            return False

    def get_tunnel_status(self, tunnel_name: str) -> str:
        """
        Get current tunnel status.
        
        Returns:
            "connected" — tunnel active with handshake
            "disconnected" — service not running
            "error" — service error
            "unknown" — unable to determine
        """
        if not tunnel_name:
            return "unknown"

        try:
            if self.verify_tunnel_active(tunnel_name):
                return "connected"
            elif self._check_service_running(tunnel_name):
                return "error"  # Service running but no handshake
            else:
                return "disconnected"
        except Exception:
            return "unknown"

    def disconnect_tunnel(self, tunnel_name: str) -> Tuple[bool, str]:
        """
        Stop and remove tunnel service.
        
        Uses: wireguard.exe /uninstalltunnelservice <tunnel_name>
        
        Args:
            tunnel_name: Name of tunnel to remove
            
        Returns:
            Tuple (success: bool, message: str)
        """
        if not self.detect_wireguard():
            return False, "WireGuard not found"

        if not self.is_admin():
            return False, "Administrator privileges required"

        try:
            # Remove tunnel service
            result = subprocess.run(
                [self.wireguard_exe, "/uninstalltunnelservice", tunnel_name],
                capture_output=True,
                text=True,
                timeout=15
            )

            if result.returncode != 0:
                error_msg = result.stderr or result.stdout or "Unknown error"
                return False, f"Failed to disconnect: {error_msg}"

            # Wait for service to stop
            time.sleep(1)

            # Verify tunnel is gone
            if self._check_service_running(tunnel_name):
                return False, "Tunnel still running after removal"

            return True, f"Tunnel '{tunnel_name}' disconnected"

        except subprocess.TimeoutExpired:
            return False, "Tunnel removal timed out"
        except Exception as e:
            return False, f"Error disconnecting tunnel: {str(e)}"

    def requires_admin(self) -> bool:
        """
        Check if admin privileges are required (always true for Windows VPN).
        
        Returns:
            True (WireGuard tunnel service requires admin)
        """
        return True
