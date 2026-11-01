# Image Processing in Mojo
from sys import argv
from memory import memset_zero

fn rgb_to_grayscale[height: Int, width: Int, channels: Int](image: DTypePointer[Float32], out: DTypePointer[Float32]) -> None:
    for i in range(height):
        for j in range(width):
            let idx = i * width * channels + j * channels
            out[i * width + j] = 0.299 * image[idx] + 0.587 * image[idx + 1] + 0.114 * image[idx + 2]

fn normalize_image[size: Int](image: DTypePointer[Float32], out: DTypePointer[Float32]) -> None:
    var min_val: Float32 = image[0]
    var max_val: Float32 = image[0]
    for i in range(1, size):
        if image[i] < min_val: min_val = image[i]
        if image[i] > max_val: max_val = image[i]
    let range_val = max_val - min_val
    if range_val < 1e-8:
        for i in range(size):
            out[i] = 0.0
    else:
        for i in range(size):
            out[i] = (image[i] - min_val) / range_val

fn apply_gaussian_blur[height: Int, width: Int](image: DTypePointer[Float32], kernel_size: Int, sigma: Float32, out: DTypePointer[Float32]) -> None:
    let pad = kernel_size // 2
    for i in range(pad, height - pad):
        for j in range(pad, width - pad):
            var val: Float32 = 0.0
            for ki in range(kernel_size):
                for kj in range(kernel_size):
                    let di = ki - pad
                    let dj = kj - pad
                    let weight = exp(-(di*di + dj*dj).to_float32() / (2.0 * sigma * sigma))
                    val += image[(i + di) * width + (j + dj)] * weight
            out[i * width + j] = val

fn main() -> None:
    print("Mojo Image Processing Kernels Ready")
