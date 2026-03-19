#!/bin/bash
set -e

cd srcs/

echo "Building for $(uname -s) $(uname -m)..."

# Install dependencies
pip install dotenv python-dotenv inquirerpy inquirer oci pyinstaller

# TIP: Add the current directory to the PYTHONPATH
export PYTHONPATH="$(pwd):$PYTHONPATH"

# Check that Python can find the modules
echo "🔍 Verifying modules are importable..."
python3 << 'EOF'
import sys
print("PYTHONPATH:", sys.path)

try:
    import classes
    print("✅ classes found")
except ImportError as e:
    print("❌ classes NOT found:", e)
    sys.exit(1)

try:
    from management_resources.users_handler import users_handler
    print("✅ users_handler found")
    from management_resources.groupes_handler import groups_handler
    print("✅ groupes_handler found")
    from management_resources.policy_handler import policy_handler
    print("✅ policy_handler found")
except ImportError as e:
    print("❌ management_resources handler NOT found:", e)
    sys.exit(1)

try:
    from governance_resources.compartment_handler import compartment_handler, compartment_selection
    print("✅ compartment_handler and compartment_selection found")
except ImportError as e:
    print("❌ governance_resources handler NOT found:", e)
    sys.exit(1)

try:
  from utils.config import YELLOW, RESET
  print("✅ config found")
  from utils.inquire_handler import (
      inquire_display_user_actions,
      inquirer_oci_users
  )
  print("✅ inquire_handler found")
except ImportError as e:
    print("❌ utils methods NOT found:", e)
    sys.exit(1)
print("✅ All modules importable")
EOF

# Build with PyInstaller
pyinstaller oci-resource-ctl.spec --clean

# Detect OS and architecture
OS=$(uname -s)
ARCH=$(uname -m)

# Determine output name
if [[ "$OS" == "Darwin" ]]; then
    if [[ "$ARCH" == "arm64" ]]; then
        OUTPUT_NAME="oci-resource-ctl-macos-arm64"
    elif [[ "$ARCH" == "x86_64" ]]; then
        OUTPUT_NAME="oci-resource-ctl-macos-x86_64"
    else
        OUTPUT_NAME="oci-resource-ctl-macos-$ARCH"
    fi
elif [[ "$OS" == "Linux" ]]; then
    if [[ "$ARCH" == "x86_64" ]]; then
        OUTPUT_NAME="oci-resource-ctl-linux-x86_64"
    elif [[ "$ARCH" == "aarch64" ]]; then
        OUTPUT_NAME="oci-resource-ctl-linux-arm64"
    else
        OUTPUT_NAME="oci-resource-ctl-linux-$ARCH"
    fi
else
    OUTPUT_NAME="oci-resource-ctl-$OS-$ARCH"
fi

# Rename binary
mv dist/oci-resource-ctl "dist/$OUTPUT_NAME"

# macOS: Remove quarantine
if [[ "$OS" == "Darwin" ]]; then
    echo "🔓 Removing macOS quarantine..."
    xattr -d com.apple.quarantine "dist/$OUTPUT_NAME" 2>/dev/null || true
    chmod +x "dist/$OUTPUT_NAME"
fi

echo "✅ Build complete: dist/$OUTPUT_NAME"
