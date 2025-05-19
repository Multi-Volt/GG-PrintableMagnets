#!/usr/bin/env bash
# Build the hollowblender binary for Linux as small as reasonably possible.
set -euo pipefail

APP=hollowblender
VERSION=$(git describe --tags --always 2>/dev/null || echo "dev")
BUILD_DIR=build
RELEASE_DIR=releases

# Create directories if they don't exist
mkdir -p "$BUILD_DIR"
mkdir -p "$RELEASE_DIR"

# Copy licenses if needed
if [ ! -d "$BUILD_DIR/licenses" ] && [ -d "licenses" ]; then
  cp -r licenses "$BUILD_DIR/"
fi

echo "Building Linux/amd64"
GOOS=linux GOARCH=amd64 \
  go build -trimpath -ldflags "-s -w -X main.version=$VERSION" -o "$BUILD_DIR/${APP}_linux" ./src

# Strip binary
if command -v strip >/dev/null 2>&1; then
  strip --strip-unneeded "$BUILD_DIR/${APP}_linux" || true
else
  echo "(strip not found – skipping binary stripping)"
fi

# Create tar.gz archive
ARCHIVE_NAME="${RELEASE_DIR}/${APP}_linux_${VERSION}.tar.gz"
tar -czf "$ARCHIVE_NAME" -C "$BUILD_DIR" "${APP}_linux" licenses

echo "Done:"
ls -lh "$BUILD_DIR/${APP}_linux"
ls -lh "$ARCHIVE_NAME"

