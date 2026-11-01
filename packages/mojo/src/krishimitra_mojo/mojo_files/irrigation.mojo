# Irrigation Optimization in Mojo
from math import exp

fn compute_penman_monteith_et0(temp: Float32, humidity: Float32, wind_speed: Float32, solar_radiation: Float32) -> Float32:
    let delta = 4098.0 * (0.6108 * exp(17.27 * temp / (temp + 237.3))) / ((temp + 237.3) * (temp + 237.3))
    let gamma: Float32 = 0.665
    let es = 0.6108 * exp(17.27 * temp / (temp + 237.3))
    let ea = es * humidity / 100.0
    let numerator = 0.408 * delta * solar_radiation + gamma * 900.0 / (temp + 273.0) * wind_speed * (es - ea)
    let denominator = delta + gamma * (1.0 + 0.34 * wind_speed)
    var et0 = numerator / denominator
    if et0 < 0.0: et0 = 0.0
    return et0

fn compute_crop_water_requirement[kc_points: Int](kc: DTypePointer[Float32], et0: Float32, area_ha: Float32, rainfall: Float32, out: DTypePointer[Float32]) -> None:
    let etc = kc[0] * et0
    var net_req = etc - rainfall
    if net_req < 0.0: net_req = 0.0
    let total_water_liters = net_req / 0.8 * area_ha * 10.0
    out[0] = total_water_liters

fn optimize_irrigation_schedule[hours: Int](et0_daily: DTypePointer[Float32], soil_moisture: DTypePointer[Float32], field_capacity: Float32, out_schedule: DTypePointer[Int32]) -> None:
    for i in range(hours):
        if soil_moisture[i] < field_capacity * 0.5 and et0_daily[i] > 4.0:
            out_schedule[i] = 1
        else:
            out_schedule[i] = 0

fn main() -> None:
    let et0 = compute_penman_monteith_et0(25.0, 60.0, 2.0, 15.0)
    print("Mojo Irrigation Optimization Kernels Ready, ET0:", et0)
