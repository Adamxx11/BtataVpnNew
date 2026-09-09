# Batata VPN - Contributing Guide

## Welcome!

Thank you for your interest in contributing to Batata VPN. This document explains how to get involved.

## Before You Start

Please understand the MVP scope:

- **In scope:** Bug fixes, Windows compatibility, tests, documentation
- **Out of scope (for MVP):** Multi-country, user accounts, kill switch, DNS filtering

See CHANGELOG.md for post-MVP roadmap.

## How to Contribute

### 1. Report a Bug

**Found an issue?** Please report it:

1. Check existing issues first (avoid duplicates)
2. Click "New Issue"
3. Select "Bug Report" template
4. Provide:
   - Windows version (10 or 11)
   - Python version
   - Steps to reproduce
   - Expected behavior
   - Actual behavior
   - Logs (sanitized, no private keys)

### 2. Suggest a Feature

**Have an idea?** Please share it:

1. Check if it fits MVP scope
2. Click "New Issue"
3. Select "Feature Request" template
4. Explain:
   - What problem it solves
   - Why it's needed
   - How it should work

### 3. Submit Code

**Ready to code?** Follow these steps:

#### Step 1: Fork and Clone

```bash
# Fork the repository on GitHub
# Clone your fork
git clone https://github.com/YOUR-USERNAME/BtataVpnNew.git
cd BtataVpnNew
```

#### Step 2: Create a Branch

```bash
# Create a feature branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/issue-description
```

#### Step 3: Make Changes

- Write clean, readable code
- Follow PEP 8 style guide
- Add type hints
- Add docstrings
- Update tests
- Never log private keys

#### Step 4: Test

```bash
# Run unit tests
python run_tests.py

# Run integration tests
python tests/integration_test.py

# On Windows 10/11: Manual testing
# See TESTING.md
```

#### Step 5: Commit

```bash
# Use clear commit messages
git commit -m "[Feature] Add feature name

Brief description of changes.
Include why this change is needed.

Fixes: #123  (if fixing an issue)"
```

#### Step 6: Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then:
1. Go to GitHub
2. Click "Create Pull Request"
3. Fill out PR template
4. Explain what changed and why
5. Reference any related issues

### 4. Write Tests

All code needs tests:

```python
# tests/test_your_module.py
import pytest
from src.your_module import YourClass

class TestYourClass:
    def test_basic_functionality(self):
        obj = YourClass()
        assert obj.method() == expected_result
    
    def test_error_handling(self):
        obj = YourClass()
        with pytest.raises(ValueError):
            obj.bad_input()
```

### 5. Improve Documentation

**Better docs help everyone:**

- Update README.md for user-facing changes
- Update DEVELOPMENT.md for developer docs
- Update TESTING.md for test procedures
- Add comments for complex code
- Add docstrings to all functions

## Code Standards

### Python Style

```python
# Good
def get_tunnel_name(config_path: str) -> str:
    """
    Extract tunnel name from config filename.
    
    Args:
        config_path: Path to config file
        
    Returns:
        Tunnel name (lowercase)
    """
    filename = Path(config_path).stem
    return filename.lower()

# Bad
def get_tunnel_name(path):
    return Path(path).stem.lower()
```

### Security

```python
# ✓ Good
print(f"Config: {sanitized_config}")
logger.debug(f"Tunnel: {tunnel_name}")

# ✗ Bad
print(f"Private key: {private_key}")
logger.debug(f"Config: {full_config_content}")
```

### Windows Compatibility

```python
# ✓ Good (Windows paths)
config_path = "C:\\Users\\User\\config.conf"
os.path.exists(config_path)

# ✗ Bad (Linux paths)
config_path = "/home/user/config.conf"
os.path.exists(config_path)
```

## Pull Request Process

### PR Checklist

Before submitting, verify:

- [ ] Tests pass: `python run_tests.py`
- [ ] No private keys in code
- [ ] No telemetry/tracking added
- [ ] Windows 10/11 compatible
- [ ] Documentation updated
- [ ] Commit messages clear
- [ ] Manual Windows test (if needed)

### PR Description Template

```markdown
## Description
Brief description of changes.

## Related Issue
Fixes #123

## Changes Made
- Change 1
- Change 2
- Change 3

## Testing
How to test these changes:
1. Step 1
2. Step 2

## Notes
Any additional context.
```

## Review Process

1. Maintainer reviews code
2. Tests must pass (automatic)
3. Code review feedback addressed
4. PR approved and merged

## Code of Conduct

- Be respectful and inclusive
- Assume good intentions
- Constructive feedback only
- No harassment or discrimination
- Report violations to maintainers

## Questions?

- **Setup issues:** See README.md
- **Testing issues:** See TESTING.md  
- **Code questions:** Start a discussion
- **Bug reports:** Create an issue

## Thank You!

Your contributions help make Batata VPN better for everyone. 🎉
