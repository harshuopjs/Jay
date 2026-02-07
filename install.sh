#!/bin/bash
set -e

INSTALL_DIR="/usr/local/lib/jay"
BIN_DIR="/usr/local/bin"
SOURCE_DIR="$(dirname "$0")/jay"
ICON_DIR="/usr/share/icons/hicolor/512x512/mimetypes"
MIME_DIR="/usr/share/mime/packages"

echo "=== Jay Installer v7.0 ==="

if [ "$(id -u)" -ne 0 ]; then
    echo "Error: Run as root (sudo)."
    exit 1
fi

echo "Installing to $INSTALL_DIR..."
# Clean install
rm -rf "$INSTALL_DIR"
mkdir -p "$INSTALL_DIR"
cp -r "$SOURCE_DIR"/* "$INSTALL_DIR"

# Launcher
echo "Creating launcher..."
cat <<EOF > "$BIN_DIR/jay"
#!/bin/bash
exec python3 "$INSTALL_DIR/cli.py" "\$@"
EOF
chmod +x "$BIN_DIR/jay"

# Icons & MIME
if command -v xdg-mime >/dev/null; then
    echo "Installing Icons & File Associations..."
    mkdir -p "$ICON_DIR"
    cp "$SOURCE_DIR/icons/jay.png" "$ICON_DIR/jay.png"
    
    if [ -f "$(dirname "$0")/jay.xml" ]; then
        cp "$(dirname "$0")/jay.xml" "$MIME_DIR/jay.xml"
        update-mime-database /usr/share/mime || echo "Warning: MIME update failed"
        gtk-update-icon-cache /usr/share/icons/hicolor || echo "Warning: Icon cache update failed"
    fi
else
    echo "Skipping MIME integration (desktop tools not found)."
fi

# VS Code Extension Installation
VSCODE_EXT_DIR="$HOME/.vscode/extensions"
JAY_EXT_DIR="$VSCODE_EXT_DIR/jay-language-support"

if [ -d "$VSCODE_EXT_DIR" ]; then
    echo "Installing VS Code Extension..."
    rm -rf "$JAY_EXT_DIR"
    mkdir -p "$JAY_EXT_DIR"
    cp -r "$(dirname "$0")/jay-vscode-extension"/* "$JAY_EXT_DIR"
    echo "VS Code extension installed."
else
    echo "VS Code extensions directory not found. Skipping extension install."
fi

echo "----------------------------------------"
echo "Jay has been installed successfully."
echo "To complete the installation, please restart your system."
echo "After restart, you can use:"
echo "    jay --version"
echo "----------------------------------------"
