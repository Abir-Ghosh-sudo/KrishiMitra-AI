# Geospatial Computing in Mojo
from math import sqrt, sin, cos, atan2

fn haversine_distance(lat1: Float64, lon1: Float64, lat2: Float64, lon2: Float64) -> Float64:
    let R: Float64 = 6371.0
    let pi: Float64 = 3.14159265358979323846
    let dlat = (lat2 - lat1) * pi / 180.0
    let dlon = (lon2 - lon1) * pi / 180.0
    let a = sin(dlat / 2.0) * sin(dlat / 2.0) + cos(lat1 * pi / 180.0) * cos(lat2 * pi / 180.0) * sin(dlon / 2.0) * sin(dlon / 2.0)
    let c = 2.0 * atan2(sqrt(a), sqrt(1.0 - a))
    return R * c

fn euclidean_distance(x1: Float64, y1: Float64, x2: Float64, y2: Float64) -> Float64:
    let dx = x2 - x1
    let dy = y2 - y1
    return sqrt(dx * dx + dy * dy)

fn compute_centroid[x: Int](latitudes: DTypePointer[Float64], longitudes: DTypePointer[Float64], out_lat: DTypePointer[Float64], out_lon: DTypePointer[Float64]) -> None:
    var sum_lat: Float64 = 0.0
    var sum_lon: Float64 = 0.0
    for i in range(x):
        sum_lat += latitudes[i]
        sum_lon += longitudes[i]
    out_lat[0] = sum_lat / x.to_float64()
    out_lon[0] = sum_lon / x.to_float64()

fn main() -> None:
    let d = haversine_distance(28.6139, 77.2090, 19.0760, 72.8777)
    print("Mojo Geospatial Kernels Ready, sample dist:", d)
