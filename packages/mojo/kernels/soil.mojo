# Mojo-accelerated soil kernels
fn compute_water_holding_capacity(sand: Float32, silt: Float32, clay: Float32, organic_matter: Float32) -> Float32:
    let total = sand + silt + clay
    if total < 1e-8:
        return 0.0
    let s = sand / total
    let c = clay / total
    let om = organic_matter / 100.0
    let whc = 0.05 + 0.3 * c + 0.1 * om + 0.05 * (1.0 - s)
    return whc * 100.0

fn compute_soil_features(ph: Float32, oc: Float32, n: Float32, p: Float32, k: Float32) -> Float32:
    var score: Float32 = 0.0
    if ph >= 6.0 and ph <= 7.5:
        score += 20.0
    else:
        score += 10.0
    if oc > 0.75:
        score += 20.0
    if n > 280:
        score += 20.0
    if p > 25:
        score += 20.0
    if k > 280:
        score += 20.0
    return score
