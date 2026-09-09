"""
Batata VPN - Main Window GUI

PyQt6-based user interface for connecting/disconnecting VPN.
Minimal design focused on functionality.
"""

import sys
import os
from pathlib import Path
from typing import Optional
import threading
from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel,
    QFileDialog, QMessageBox, QProgressDialog
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject, QThread
from PyQt6.QtGui import QFont, QIcon

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config_manager import ConfigManager
from wireguard_manager import WireGuardManager
from ip_service import IPService


class WorkerThread(QThread):
    """
    Worker thread for long-running operations (to keep UI responsive).
    """
    finished = pyqtSignal()
    error = pyqtSignal(str)
    result = pyqtSignal(dict)

    def __init__(self, operation, *args):
        super().__init__()
        self.operation = operation
        self.args = args

    def run(self):
        try:
            result = self.operation(*self.args)
            self.result.emit(result)
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.finished.emit()


class MainWindow(QMainWindow):
    """
    Main Batata VPN window.
    
    Features:
    - Load WireGuard config file
    - Connect/Disconnect buttons
    - IP verification
    - DNS/IPv6 status display
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Batata VPN")
        self.setGeometry(100, 100, 500, 600)
        self.setStyleSheet(self.get_stylesheet())

        # Components
        self.config_manager = ConfigManager()
        self.wireguard_manager = WireGuardManager()
        self.ip_service = IPService()

        # State
        self.config_loaded = False
        self.connected = False
        self.ip_before = None
        self.tunnel_name = ""

        # UI Setup
        self.init_ui()
        self.check_wireguard()

    def init_ui(self):
        """
        Initialize UI components.
        """
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Title
        title = QLabel("BATATA VPN")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Country (placeholder)
        country = QLabel("🇳🇱 Netherlands")
        country_font = QFont()
        country_font.setPointSize(14)
        country.setFont(country_font)
        country.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(country)

        # Status section
        status_label = QLabel("Status:")
        status_font = QFont()
        status_font.setPointSize(11)
        status_label.setFont(status_font)
        layout.addWidget(status_label)

        self.status_display = QLabel("Disconnected")
        status_display_font = QFont()
        status_display_font.setPointSize(12)
        status_display_font.setBold(True)
        self.status_display.setFont(status_display_font)
        self.status_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_display.setStyleSheet("color: #ff6b6b;")
        layout.addWidget(self.status_display)

        layout.addSpacing(10)

        # IP section
        ip_label = QLabel("Public IP:")
        ip_label.setFont(status_font)
        layout.addWidget(ip_label)

        self.ip_display = QLabel("Click 'Load Config' to get started")
        ip_display_font = QFont()
        ip_display_font.setPointSize(11)
        ip_display_font.setFamily("Courier")
        self.ip_display.setFont(ip_display_font)
        self.ip_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.ip_display)

        layout.addSpacing(20)

        # Button row
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.load_config_btn = QPushButton("Load Config")
        self.load_config_btn.setMinimumHeight(50)
        self.load_config_btn.clicked.connect(self.load_config)
        button_layout.addWidget(self.load_config_btn)

        self.connect_btn = QPushButton("CONNECT")
        self.connect_btn.setMinimumHeight(50)
        self.connect_btn.setStyleSheet(
            "QPushButton { background-color: #4CAF50; color: white; font-size: 14px; font-weight: bold; }"
        )
        self.connect_btn.clicked.connect(self.on_connect_clicked)
        self.connect_btn.setEnabled(False)
        button_layout.addWidget(self.connect_btn)

        layout.addLayout(button_layout)

        layout.addSpacing(20)

        # DNS/IPv6 section
        dns_label = QLabel("DNS Leak Detection:")
        dns_label.setFont(status_font)
        layout.addWidget(dns_label)

        self.dns_display = QLabel("Checking...")
        self.dns_display.setFont(ip_display_font)
        layout.addWidget(self.dns_display)

        layout.addSpacing(10)

        ipv6_label = QLabel("IPv6:")
        ipv6_label.setFont(status_font)
        layout.addWidget(ipv6_label)

        self.ipv6_display = QLabel("Checking...")
        self.ipv6_display.setFont(ip_display_font)
        layout.addWidget(self.ipv6_display)

        layout.addSpacing(20)

        # Info label
        self.info_label = QLabel("")
        info_font = QFont()
        info_font.setPointSize(9)
        self.info_label.setFont(info_font)
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.info_label)

        layout.addStretch()

        central_widget.setLayout(layout)

    def get_stylesheet(self) -> str:
        """
        Return application stylesheet.
        """
        return """
        QMainWindow {
            background-color: #f5f5f5;
        }
        QLabel {
            color: #333;
        }
        QPushButton {
            border: none;
            border-radius: 5px;
            padding: 8px;
            background-color: #e0e0e0;
            color: #333;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #d0d0d0;
        }
        QPushButton:pressed {
            background-color: #c0c0c0;
        }
        QPushButton:disabled {
            background-color: #ccc;
            color: #999;
        }
        """

    def check_wireguard(self):
        """
        Check if WireGuard is installed.
        """
        if not self.wireguard_manager.detect_wireguard():
            self.show_error(
                "WireGuard Not Found",
                "WireGuard for Windows is not installed.\n\n"
                "Please download and install it from:\nhttps://www.wireguard.com/install/\n\n"
                "After installation, restart Batata VPN."
            )
            self.load_config_btn.setEnabled(False)
            self.info_label.setText("⚠️ WireGuard not installed")
        else:
            self.info_label.setText("✓ WireGuard detected")
            # Check for admin privileges
            if not self.wireguard_manager.is_admin():
                self.show_warning(
                    "Administrator Privileges Required",
                    "Batata VPN needs to run as administrator to manage VPN tunnels.\n\n"
                    "Please close and reopen Batata VPN as administrator."
                )
                self.load_config_btn.setEnabled(False)
                self.info_label.setText("⚠️ Administrator privileges required")

    def load_config(self):
        """
        Load WireGuard config file via file dialog.
        """
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setNameFilter("WireGuard Config (*.conf);;All Files (*)")
        file_dialog.setDirectory(os.path.expanduser("~"))

        if file_dialog.exec():
            config_path = file_dialog.selectedFiles()[0]
            if self.config_manager.load_config(config_path):
                self.config_loaded = True
                self.tunnel_name = self.config_manager.tunnel_name
                self.connect_btn.setEnabled(True)
                self.info_label.setText(f"✓ Config loaded: {self.tunnel_name}")
                
                # Fetch initial public IP
                self.fetch_initial_ip()
            else:
                self.show_error(
                    "Invalid Config",
                    "The selected config file is invalid.\n\n"
                    "Please check the file and try again."
                )

    def fetch_initial_ip(self):
        """
        Fetch public IP before connection.
        """
        self.ip_display.setText("Fetching public IP...")
        self.dns_display.setText("Checking...")
        self.ipv6_display.setText("Checking...")

        thread = WorkerThread(self._fetch_ip_worker)
        thread.result.connect(self._on_initial_ip_result)
        thread.error.connect(lambda e: self.show_error("IP Fetch Failed", str(e)))
        thread.start()

    def _fetch_ip_worker(self) -> dict:
        """
        Worker for fetching initial IP and leak detection.
        """
        ip = self.ip_service.get_public_ip()
        dns_result = self.ip_service.detect_dns_leak()
        ipv6_result = self.ip_service.detect_ipv6_leak()
        
        return {
            "ip": ip,
            "dns": dns_result,
            "ipv6": ipv6_result
        }

    def _on_initial_ip_result(self, result: dict):
        """
        Handle initial IP fetch result.
        """
        ip = result.get("ip")
        dns_result = result.get("dns", {})
        ipv6_result = result.get("ipv6", {})

        if ip:
            self.ip_before = ip
            self.ip_display.setText(ip)
        else:
            self.ip_display.setText("Unable to fetch IP")
            self.show_warning("IP Fetch Failed", "Could not fetch your public IP.")

        # Update leak detection displays
        dns_status = dns_result.get("status", "UNKNOWN")
        self.dns_display.setText(f"{dns_result.get('message', 'Unknown')}")

        ipv6_status = ipv6_result.get("status", "UNKNOWN")
        self.ipv6_display.setText(f"{ipv6_result.get('message', 'Unknown')}")

    def on_connect_clicked(self):
        """
        Handle CONNECT button click.
        """
        if not self.config_loaded:
            self.show_error("No Config", "Please load a config file first.")
            return

        if self.connected:
            self.disconnect_vpn()
        else:
            self.connect_vpn()

    def connect_vpn(self):
        """
        Connect to VPN.
        """
        self.status_display.setText("Connecting...")
        self.connect_btn.setEnabled(False)
        self.load_config_btn.setEnabled(False)

        thread = WorkerThread(self._connect_worker)
        thread.result.connect(self._on_connect_result)
        thread.error.connect(self._on_connect_error)
        thread.finished.connect(lambda: self.connect_btn.setEnabled(True))
        thread.start()

    def _connect_worker(self) -> dict:
        """
        Worker for connection operation.
        """
        # Get config path from config manager
        conf_path = self.config_manager.conf_path

        # Install tunnel service
        success, message = self.wireguard_manager.install_tunnel_service(conf_path)
        if not success:
            return {"success": False, "message": message}

        # Wait a bit for tunnel to settle
        import time
        time.sleep(2)

        # Fetch public IP after connection
        ip_after = self.ip_service.get_public_ip()
        dns_result = self.ip_service.detect_dns_leak()
        ipv6_result = self.ip_service.detect_ipv6_leak()

        # Verify connection
        server_endpoint = self.config_manager.get_server_endpoint()
        verification = self.ip_service.verify_tunnel_connection(
            self.ip_before,
            ip_after,
            server_endpoint
        )

        return {
            "success": verification["tunnel_active"],
            "message": verification["message"],
            "ip_after": ip_after,
            "dns": dns_result,
            "ipv6": ipv6_result
        }

    def _on_connect_result(self, result: dict):
        """
        Handle connection result.
        """
        success = result.get("success", False)
        message = result.get("message", "Unknown error")

        if success:
            self.connected = True
            self.status_display.setText("Connected")
            self.status_display.setStyleSheet("color: #4CAF50; font-weight: bold;")
            self.connect_btn.setText("DISCONNECT")
            self.connect_btn.setStyleSheet(
                "QPushButton { background-color: #f44336; color: white; font-size: 14px; font-weight: bold; }"
            )
            self.load_config_btn.setEnabled(False)

            # Update IP and leak detection
            ip_after = result.get("ip_after")
            if ip_after:
                self.ip_display.setText(ip_after)

            dns_result = result.get("dns", {})
            self.dns_display.setText(dns_result.get("message", "Unknown"))

            ipv6_result = result.get("ipv6", {})
            self.ipv6_display.setText(ipv6_result.get("message", "Unknown"))

            self.show_success("Connected", message)
        else:
            self.status_display.setText("Connection Failed")
            self.status_display.setStyleSheet("color: #f44336; font-weight: bold;")
            self.connect_btn.setEnabled(True)
            self.load_config_btn.setEnabled(True)
            self.show_error("Connection Failed", message)

    def _on_connect_error(self, error: str):
        """
        Handle connection error.
        """
        self.status_display.setText("Connection Error")
        self.status_display.setStyleSheet("color: #f44336; font-weight: bold;")
        self.connect_btn.setEnabled(True)
        self.load_config_btn.setEnabled(True)
        self.show_error("Connection Error", error)

    def disconnect_vpn(self):
        """
        Disconnect from VPN.
        """
        self.status_display.setText("Disconnecting...")
        self.connect_btn.setEnabled(False)

        thread = WorkerThread(self._disconnect_worker)
        thread.result.connect(self._on_disconnect_result)
        thread.error.connect(self._on_disconnect_error)
        thread.finished.connect(lambda: self.connect_btn.setEnabled(True))
        thread.start()

    def _disconnect_worker(self) -> dict:
        """
        Worker for disconnection operation.
        """
        # Disconnect tunnel
        success, message = self.wireguard_manager.disconnect_tunnel(self.tunnel_name)
        if not success:
            return {"success": False, "message": message}

        # Wait for tunnel to stop
        import time
        time.sleep(1)

        # Fetch public IP after disconnection
        ip_final = self.ip_service.get_public_ip()
        dns_result = self.ip_service.detect_dns_leak()
        ipv6_result = self.ip_service.detect_ipv6_leak()

        return {
            "success": True,
            "message": message,
            "ip_final": ip_final,
            "dns": dns_result,
            "ipv6": ipv6_result
        }

    def _on_disconnect_result(self, result: dict):
        """
        Handle disconnection result.
        """
        success = result.get("success", False)
        message = result.get("message", "Unknown error")

        if success:
            self.connected = False
            self.status_display.setText("Disconnected")
            self.status_display.setStyleSheet("color: #ff6b6b; font-weight: bold;")
            self.connect_btn.setText("CONNECT")
            self.connect_btn.setStyleSheet(
                "QPushButton { background-color: #4CAF50; color: white; font-size: 14px; font-weight: bold; }"
            )
            self.load_config_btn.setEnabled(True)

            # Update IP and leak detection
            ip_final = result.get("ip_final")
            if ip_final:
                self.ip_display.setText(ip_final)

            dns_result = result.get("dns", {})
            self.dns_display.setText(dns_result.get("message", "Unknown"))

            ipv6_result = result.get("ipv6", {})
            self.ipv6_display.setText(ipv6_result.get("message", "Unknown"))

            self.show_success("Disconnected", message)
        else:
            self.status_display.setText("Disconnection Error")
            self.status_display.setStyleSheet("color: #f44336; font-weight: bold;")
            self.connect_btn.setEnabled(True)
            self.show_error("Disconnection Failed", message)

    def _on_disconnect_error(self, error: str):
        """
        Handle disconnection error.
        """
        self.status_display.setText("Disconnection Error")
        self.status_display.setStyleSheet("color: #f44336; font-weight: bold;")
        self.connect_btn.setEnabled(True)
        self.show_error("Disconnection Error", error)

    def show_success(self, title: str, message: str):
        """
        Show success message dialog.
        """
        QMessageBox.information(self, title, message)

    def show_error(self, title: str, message: str):
        """
        Show error message dialog.
        """
        QMessageBox.critical(self, title, message)

    def show_warning(self, title: str, message: str):
        """
        Show warning message dialog.
        """
        QMessageBox.warning(self, title, message)
