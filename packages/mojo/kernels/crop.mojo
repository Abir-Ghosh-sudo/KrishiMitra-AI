# Mojo-accelerated crop growth kernels
fn compute_gdd(tmin: Float32, tmax: Float32, tbase: Float32) -> Float32:
    var tavg = (tmin + tmax) / 2.0
    if tavg < tbase:
        return 0.0
    if tavg > 30.0:
        tavg = 30.0
    return tavg - tbase

fn compute_pest_risk_mojo(temp: Float32, humidity: Float32, rainfall: Float32, wind: Float32, leaf_wetness: Float32) -> Float32:
    var risk: Float32 = 0.0
    if temp >= 20.0 and temp <= 30.0:
        risk += 25.0 * (1.0 - abs(temp - 25.0) / 10.0)
    if humidity > 70.0:
        risk += 20.0 * ((humidity - 70.0) / 30.0)
    if rainfall > 0.0:
        risk += 15.0
    if leaf_wetness > 0.5:
        risk += 25.0 * leaf_wetness
    if risk > 100.0:
        risk = 100.0
    if risk < 0.0:
        risk = 0.0
    return risk

fn compute_disease_risk_mojo(temp: Float32, humidity: Float32, lw_duration: Float32, rainfall: Float32) -> Float32:
    var risk: Float32 = 0.0
    if humidity > 80.0:
        risk += 30.0
    if lw_duration > 6.0:
        risk += 30.0
    if temp >= 15.0 and temp <= 25.0 and humidity > 80.0:
        risk += 25.0
    if risk > 100.0:
        risk = 100.0
    return risk
