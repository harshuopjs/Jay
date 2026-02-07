#!/bin/bash
set -e

echo "=== Jay Uninstaller ==="

if [ "$(id -u)" -ne 0 ]; then
    echo "Error: Run as root."
    exit 1
fi

rm -rf "/usr/local/lib/jay"
rm -f "/usr/local/bin/jay"
rm -f "/usr/share/icons/hicolor/512x512/mimetypes/jay.png"
rm -f "/usr/share/mime/packages/jay.xml"

update-mime-database /usr/share/mime || true
gtk-update-icon-cache /usr/share/icons/hicolor || true

# Remove VS Code Extension
rm -rf "$HOME/.vscode/extensions/jay-language-support"

echo "✅ Jay uninstalled."
