#!/bin/bash

# === Configuration ===
SCRIPT_DIR="$(dirname "$0")"
SRC_DIR="$SCRIPT_DIR/src/python"
OUTPUT_DIR="$SCRIPT_DIR/build/magnetic_imager"
EXEC_NAME="magnetic_logger_gui"

# === Handle clean option ===
if [[ "$1" == "clean" ]]; then
    echo "[*] Cleaning previous build..."
    rm -rf "$SCRIPT_DIR/build"
    echo "[✔] Clean complete."
    exit 0
fi

# === Build with pyinstaller from script dir ===
echo "[*] Building executable (folder-based distribution)..."
pyinstaller \
    --noconsole --clean --strip \
    -n "$EXEC_NAME" \
    --distpath "$OUTPUT_DIR" \
    --workpath "$SCRIPT_DIR/build/pyinstaller_work" \
    --specpath "$SCRIPT_DIR/build/pyinstaller_spec" \
    "$SRC_DIR/magnetic_logger_gui.py"

# === Verify build success ===
if [[ ! -d "$OUTPUT_DIR/$EXEC_NAME" ]]; then
    echo "[✘] Build failed: $OUTPUT_DIR/$EXEC_NAME folder not found."
    exit 1
fi

# === Copy license files ===
mkdir -p "$OUTPUT_DIR/licenses"
cp "$SCRIPT_DIR/licenses/"* "$OUTPUT_DIR/licenses/"

echo "[✔] Executable folder created: $OUTPUT_DIR/$EXEC_NAME"
echo "[✔] Licenses copied into $OUTPUT_DIR/"
echo "[✔] Run with: $OUTPUT_DIR/$EXEC_NAME/$EXEC_NAME"

