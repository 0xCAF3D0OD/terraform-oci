#!/bin/bash
# build.sh - Compile for current architecture

set -e  # Exit on error

echo "🔨 Building for $(uname -m)..."
pip install dotenv python-dotenv inquirerpy inquirer oci pyinstaller

pyinstaller oci-resource-ctl.spec --clean

# Rename binary by architecture
ARCH=$(uname -m)
if [[ "$ARCH" == "x86_64" ]]; then
    OUTPUT_NAME="oci-resource-ctl-linux-x86_64"
elif [[ "$ARCH" == "aarch64" ]]; then
    OUTPUT_NAME="oci-resource-ctl-linux-arm64"
else
    OUTPUT_NAME="oci-resource-ctl-$ARCH"
fi

mv srcs/dist/oci-resource-ctl "srcs/dist/$OUTPUT_NAME"

echo "✅ Build complete: srcs/dist/$OUTPUT_NAME"