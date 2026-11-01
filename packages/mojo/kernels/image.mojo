# Mojo-accelerated image kernels
fn rgb_to_grayscale(image: DTypePointer[Float32], h: Int, w: Int, out: DTypePointer[Float32]):
    for i in range(h):
        for j in range(w):
            idx = i * w * 3 + j * 3
            out[i * w + j] = 0.299 * image[idx] + 0.587 * image[idx + 1] + 0.114 * image[idx + 2]

fn normalize_image(image: DTypePointer[Float32], size: Int, out: DTypePointer[Float32]):
    var min_val: Float32 = image[0]
    var max_val: Float32 = image[0]
    for i in range(size):
        if image[i] < min_val: min_val = image[i]
        if image[i] > max_val: max_val = image[i]
    let range_val = max_val - min_val
    if range_val < 1e-8:
        for i in range(size):
            out[i] = 0.0
    else:
        for i in range(size):
            out[i] = (image[i] - min_val) / range_val
