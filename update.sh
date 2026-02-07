#!/bin/bash
set -e

echo "=== Jay Updater ==="

if [ ! -f "/usr/local/bin/jay" ]; then
    echo "Jay is not installed. Please run install.sh first."
    exit 1
fi

./install.sh
echo "✅ Jay updated successfully."
