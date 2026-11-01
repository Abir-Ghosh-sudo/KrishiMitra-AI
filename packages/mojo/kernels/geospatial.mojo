# Mojo-accelerated geospatial kernels
fn haversine_distance(lat1: Float64, lon1: Float64, lat2: Float64, lon2: Float64) -> Float64:
    let R: Float64 = 6371.0
    let pi = 3.141592653589793
    let dlat = (lat2 - lat1) * pi / 180.0
    let dlon = (lon2 - lon1) * pi / 180.0
    let a = (dlat/2.0)*(dlat/2.0) + cos(lat1*pi/180.0)*cos(lat2*pi/180.0)*(dlon/2.0)*(dlon/2.0)
    let c = 2.0 * atan2(sqrt(a), sqrt(1.0-a))
    return R * c
