#!/bin/bash
set -e

cd srcs/

echo "🔨 Building for $(uname -s) $(uname -m)..."

# Install dependencies
pip install dotenv python-dotenv inquirerpy inquirer oci pyinstaller

# CRITIQUE : Ajouter le répertoire courant au PYTHONPATH
export PYTHONPATH="$(pwd):$PYTHONPATH"

# Vérifier que Python trouve les modules
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
except ImportError as e:
    print("❌ users_handler NOT found:", e)
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
