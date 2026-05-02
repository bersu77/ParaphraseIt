#!/bin/bash
# Build ParaphraseIt for Linux (standalone binary)
cd "$(dirname "$0")"

if [ ! -d "venv" ]; then
    python3 -m venv venv
    ./venv/bin/pip install -r requirements.txt
fi

./venv/bin/pyinstaller \
    --onefile \
    --windowed \
    --name "ParaphraseIt" \
    --add-data "assets:assets" \
    --add-data ".env:." \
    paraphrase.py

# Create .desktop file for Linux app menu
mkdir -p dist
cat > dist/ParaphraseIt.desktop << 'DESKTOP'
[Desktop Entry]
Name=ParaphraseIt
Comment=System-wide paraphrase tool (Ctrl+Shift+P)
Exec=APPDIR/ParaphraseIt
Icon=APPDIR/icon_256.png
Terminal=false
Type=Application
Categories=Utility;TextTools;
StartupNotify=false
DESKTOP

cp assets/icon_256.png dist/
APPDIR="$(cd dist && pwd)"
sed -i "s|APPDIR|$APPDIR|g" dist/ParaphraseIt.desktop

echo ""
echo "Build complete! Files in dist/"
echo "  - ParaphraseIt         (run directly)"
echo "  - ParaphraseIt.desktop (copy to ~/.local/share/applications/ for app menu)"
echo ""
echo "To auto-start on boot:"
echo "  cp dist/ParaphraseIt.desktop ~/.config/autostart/"
