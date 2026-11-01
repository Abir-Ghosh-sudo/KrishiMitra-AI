# Mojo-accelerated irrigation kernels
fn compute_et0(temp: Float32, humidity: Float32, wind: Float32, radiation: Float32) -> Float32:
    let delta = 4098.0 * (0.6108 * exp(17.27 * temp / (temp + 237.3))) / ((temp + 237.3) * (temp + 237.3))
    let gamma = 0.665
    let es = 0.6108 * exp(17.27 * temp / (temp + 237.3))
    let ea = es * humidity / 100.0
    let et0 = (0.408 * delta * radiation + gamma * 900.0 / (temp + 273.0) * wind * (es - ea)) / (delta + gamma * (1.0 + 0.34 * wind))
    if et0 < 0.0:
        return 0.0
    return et0

fn compute_water_requirement(kc: Float32, et0: Float32, area_ha: Float32, rainfall: Float32) -> Float32:
    let etc = kc * et0
    let net_req = etc - rainfall
    if net_req < 0.0:
        return 0.0
    return net_req / 0.8 * area_ha * 10.0
