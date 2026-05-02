#!/bin/bash
# Build ParaphraseIt for macOS (.app bundle)
cd "$(dirname "$0")"

if [ ! -d "venv" ]; then
    python3 -m venv venv
    ./venv/bin/pip install -r requirements.txt
fi

./venv/bin/pyinstaller \
    --onefile \
    --windowed \
    --name "ParaphraseIt" \
    --icon "assets/icon.icns" \
    --add-data "assets:assets" \
    --add-data ".env:." \
    --osx-bundle-identifier "com.paraphraseit.app" \
    paraphrase.py

echo ""
echo "Build complete! Find ParaphraseIt.app in dist/"
