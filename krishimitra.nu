# KrishiMitra-AI Nushell Script

export def main [] {
    print "KrishiMitra-AI CLI (Nushell)"
    print "Use: nu krishimitra.nu <command>"
}

export def install [] {
    print "Installing dependencies..."
    pip install -e packages/mojo
    print "Done"
}

export def mojo-test [] {
    print "Testing Mojo kernels..."
    python -c "import krishimitra_mojo; print('OK')"
}

export def api [] {
    print "Starting API server..."
    cd apps/api
    uvicorn krishimitra_api.main:app --reload
}
