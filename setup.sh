#!/usr/bin/env bash
# KrishiMitra-AI Setup Script for Linux/WSL

echo "=== KrishiMitra-AI Setup ==="

# Install Mojo if not present
if ! command -v mojo &> /dev/null; then
    echo "Installing Mojo..."
    curl -sSf https://get.modular.com | sh -s -- --yes
    source $HOME/.modular/env 2>/dev/null || true
fi

mojo --version 2>&1

# Install Python dependencies
pip install -e packages/mojo 2>/dev/null || true

echo "Setup complete!"
