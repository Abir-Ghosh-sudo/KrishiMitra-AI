#!/usr/bin/env bash
# KrishiMitra-AI Shell Script

set -e

case "$1" in
    install)
        echo "Installing dependencies..."
        pip install -e packages/mojo
        pip install -e packages/core packages/database packages/ml packages/weather packages/geospatial packages/soil packages/optimization packages/simulation 2>/dev/null || true
        echo "Installation complete"
        ;;
    dev)
        echo "Setting up development environment..."
        pip install -r requirements-dev.txt 2>/dev/null || pip install pytest pytest-asyncio black ruff mypy
        make install 2>/dev/null || ./krishimitra.sh install
        echo "Dev environment ready"
        ;;
    api)
        echo "Starting API server..."
        cd apps/api && uvicorn krishimitra_api.main:app --reload --host 0.0.0.0 --port 8000
        ;;
    test)
        echo "Running tests..."
        pytest -v 2>/dev/null || python -m pytest -v
        ;;
    mojo)
        echo "Testing Mojo kernels..."
        python -c "
from krishimitra_mojo import image, geospatial, soil, irrigation, crop_sim, risk
import numpy as np
img = np.zeros((64,64,3), dtype=np.float32)
print('Image:', image.rgb_to_grayscale(img).shape)
print('Geo:', geospatial.haversine_distance(0,0,1,1))
print('Soil:', soil.compute_water_holding_capacity(30,40,30,2))
print('Irrigation:', irrigation.compute_et0(25,60,2,15))
print('Crop GDD:', crop_sim.compute_gdd(15,30,10))
print('Risk:', risk.compute_pest_risk(25,80,5,3,0.8))
print('All Mojo kernels OK')
"
        ;;
    clean)
        echo "Cleaning..."
        find . -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true
        find . -name '*.pyc' -delete 2>/dev/null || true
        ;;
    *)
        echo "KrishiMitra-AI CLI"
        echo "Usage: ./krishimitra.sh [install|dev|api|test|mojo|clean]"
        ;;
esac
