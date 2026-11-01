
# Mojo-accelerated kernels
try:
    import krishimitra_mojo
    _MOJO_AVAILABLE = True
except ImportError:
    _MOJO_AVAILABLE = False
