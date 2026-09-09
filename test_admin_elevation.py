#!/usr/bin/env python3
"""
Test script to verify pyuac module and admin elevation logic.
Can run on any platform to verify imports and structure.
"""

import sys

def test_pyuac_import():
    """Test if pyuac can be imported."""
    print("\n[TEST] pyuac Import")
    print("-" * 50)
    
    try:
        import pyuac
        print("✓ pyuac imported successfully")
        print(f"  - Module: {pyuac}")
        print(f"  - Version: {getattr(pyuac, '__version__', 'Unknown')}")
        
        # Check for required functions
        if hasattr(pyuac, 'isUserAdmin'):
            print("✓ pyuac.isUserAdmin() available")
        else:
            print("✗ pyuac.isUserAdmin() NOT found")
            return False
        
        if hasattr(pyuac, 'runAsAdmin'):
            print("✓ pyuac.runAsAdmin() available")
        else:
            print("✗ pyuac.runAsAdmin() NOT found")
            return False
        
        return True
    except ImportError as e:
        print(f"✗ Failed to import pyuac: {e}")
        return False


def test_admin_logic():
    """Test admin check logic (doesn't actually elevate)."""
    print("\n[TEST] Admin Check Logic")
    print("-" * 50)
    
    try:
        import pyuac
        
        # Get current admin status (doesn't elevate)
        is_admin = pyuac.isUserAdmin()
        print(f"Current admin status: {is_admin}")
        
        if is_admin:
            print("✓ Running with administrator privileges")
        else:
            print("⚠ NOT running as administrator")
            print("  (This is expected in non-Windows environments)")
        
        return True
    except Exception as e:
        print(f"✗ Error checking admin status: {e}")
        return False


def test_main_py_structure():
    """Test that main.py can be parsed and imports work."""
    print("\n[TEST] main.py Structure")
    print("-" * 50)
    
    try:
        # Try to parse main.py without executing it
        import ast
        
        with open('main.py', 'r') as f:
            code = f.read()
        
        ast.parse(code)
        print("✓ main.py syntax is valid")
        
        # Check for pyuac import handling
        if 'import pyuac' in code:
            print("✓ pyuac import statement found")
        else:
            print("✗ pyuac import NOT found")
            return False
        
        if 'pyuac.isUserAdmin()' in code:
            print("✓ pyuac.isUserAdmin() check found")
        else:
            print("✗ pyuac.isUserAdmin() check NOT found")
            return False
        
        if 'pyuac.runAsAdmin()' in code:
            print("✓ pyuac.runAsAdmin() call found")
        else:
            print("✗ pyuac.runAsAdmin() call NOT found")
            return False
        
        return True
    except SyntaxError as e:
        print(f"✗ Syntax error in main.py: {e}")
        return False
    except FileNotFoundError:
        print("✗ main.py not found")
        return False
    except Exception as e:
        print(f"✗ Error parsing main.py: {e}")
        return False


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*50)
    print("Admin Elevation Test Suite")
    print("="*50)
    
    results = []
    
    # Test 1: pyuac import
    try:
        results.append(("pyuac Import", test_pyuac_import()))
    except Exception as e:
        print(f"✗ Exception in pyuac import test: {e}")
        results.append(("pyuac Import", False))
    
    # Test 2: Admin logic
    try:
        results.append(("Admin Check Logic", test_admin_logic()))
    except Exception as e:
        print(f"✗ Exception in admin check test: {e}")
        results.append(("Admin Check Logic", False))
    
    # Test 3: main.py structure
    try:
        results.append(("main.py Structure", test_main_py_structure()))
    except Exception as e:
        print(f"✗ Exception in main.py structure test: {e}")
        results.append(("main.py Structure", False))
    
    # Summary
    print("\n" + "="*50)
    print("Test Summary")
    print("="*50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓" if result else "✗"
        print(f"{status} {name}")
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n✅ All tests passed!")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed")
    
    print("="*50)
    print("\nNOTE: Full Windows VPN testing requires Windows 10/11")
    print("="*50)
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
