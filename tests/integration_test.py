"""
Batata VPN - Integration Test Utilities

Helper functions for testing the complete VPN workflow.
Note: Actual Windows VPN testing requires Windows 10/11.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config_manager import ConfigManager
from wireguard_manager import WireGuardManager
from ip_service import IPService


def test_config_parsing():
    """
    Test config file parsing without VPN operation.
    """
    print("\n[TEST] Config Parsing")
    print("-" * 40)
    
    # Create a sample config for testing
    sample_config = """
[Interface]
PrivateKey = KJjLn0LsUJYvIbBVkXXXXXXXXXXXXXXXXXXXXXX
Address = 10.0.0.2/24
DNS = 1.1.1.1

[Peer]
PublicKey = KXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX=
Endpoint = 203.0.113.45:51820
AllowedIPs = 0.0.0.0/0
PersistentKeepalive = 25
"""
    
    # Write to temp file
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.conf', delete=False) as f:
        f.write(sample_config)
        temp_path = f.name
    
    # Test parsing
    manager = ConfigManager()
    if manager.load_config(temp_path):
        print("✓ Config loaded successfully")
        print(f"  - Tunnel name: {manager.tunnel_name}")
        print(f"  - Address: {manager.get_interface_section().get('Address')}")
        print(f"  - Endpoint: {manager.get_server_endpoint()}")
        print(f"  - Private key: [HIDDEN]")
        return True
    else:
        print("✗ Config parsing failed")
        return False
    
    # Cleanup
    import os
    os.unlink(temp_path)


def test_wireguard_detection():
    """
    Test WireGuard installation detection.
    """
    print("\n[TEST] WireGuard Detection")
    print("-" * 40)
    
    manager = WireGuardManager()
    if manager.detect_wireguard():
        print("✓ WireGuard for Windows detected")
        print(f"  - wireguard.exe: {manager.wireguard_exe}")
        if manager.wg_exe:
            print(f"  - wg.exe: {manager.wg_exe}")
        return True
    else:
        print("⚠ WireGuard for Windows not detected")
        print("  (Install from https://www.wireguard.com/install/)")
        return False


def test_admin_check():
    """
    Test administrator privilege detection.
    """
    print("\n[TEST] Administrator Check")
    print("-" * 40)
    
    manager = WireGuardManager()
    if manager.is_admin():
        print("✓ Running with administrator privileges")
        return True
    else:
        print("✗ Not running as administrator")
        print("  (Required for VPN tunnel management)")
        return False


def test_ip_service():
    """
    Test public IP fetching.
    """
    print("\n[TEST] IP Service")
    print("-" * 40)
    
    service = IPService()
    ip = service.get_public_ip()
    
    if ip:
        print(f"✓ Public IP fetched: {ip}")
        return True
    else:
        print("✗ Failed to fetch public IP")
        print("  (Check internet connectivity)")
        return False


def test_leak_detection():
    """
    Test DNS/IPv6 leak detection.
    """
    print("\n[TEST] Leak Detection")
    print("-" * 40)
    
    service = IPService()
    
    dns_result = service.detect_dns_leak()
    print(f"  DNS: {dns_result.get('message', 'Unknown')}")
    
    ipv6_result = service.detect_ipv6_leak()
    print(f"  IPv6: {ipv6_result.get('message', 'Unknown')}")
    
    return True


def run_all_tests():
    """
    Run all integration tests.
    """
    print("\n" + "="*60)
    print("Batata VPN - Integration Test Suite")
    print("="*60)
    print("\nNote: These tests verify core functionality.")
    print("Full Windows VPN testing requires Windows 10/11.")
    
    results = []
    
    try:
        results.append(("Config Parsing", test_config_parsing()))
    except Exception as e:
        print(f"✗ Config Parsing failed: {e}")
        results.append(("Config Parsing", False))
    
    try:
        results.append(("WireGuard Detection", test_wireguard_detection()))
    except Exception as e:
        print(f"✗ WireGuard Detection failed: {e}")
        results.append(("WireGuard Detection", False))
    
    try:
        results.append(("Admin Check", test_admin_check()))
    except Exception as e:
        print(f"✗ Admin Check failed: {e}")
        results.append(("Admin Check", False))
    
    try:
        results.append(("IP Service", test_ip_service()))
    except Exception as e:
        print(f"✗ IP Service failed: {e}")
        results.append(("IP Service", False))
    
    try:
        results.append(("Leak Detection", test_leak_detection()))
    except Exception as e:
        print(f"✗ Leak Detection failed: {e}")
        results.append(("Leak Detection", False))
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓" if result else "✗"
        print(f"{status} {name}")
    
    print(f"\nPassed: {passed}/{total}")
    print("="*60)
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
