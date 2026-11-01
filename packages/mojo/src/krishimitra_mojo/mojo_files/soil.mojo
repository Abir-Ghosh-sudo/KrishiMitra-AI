# Soil Analysis in Mojo
fn compute_soil_texture[samples: Int](sand: DTypePointer[Float32], silt: DTypePointer[Float32], clay: DTypePointer[Float32], out_class: DTypePointer[Int32]) -> None:
    for i in range(samples):
        let s = sand[i]
        let si = silt[i]
        let c = clay[i]
        let total = s + si + c
        if total < 1e-8:
            out_class[i] = 0
            continue
        let sp = s / total * 100.0
        let sip = si / total * 100.0
        let cp = c / total * 100.0
        if cp > 40.0:
            out_class[i] = 1
        elif cp > 27.0 and sip < 28.0:
            out_class[i] = 2
        elif sip > 80.0:
            out_class[i] = 3
        elif sip > 50.0:
            out_class[i] = 4
        elif cp > 20.0 and sip > 40.0:
            out_class[i] = 5
        elif cp > 7.0 and sip < 50.0:
            out_class[i] = 6
        else:
            out_class[i] = 7

fn compute_water_holding_capacity(sand: Float32, silt: Float32, clay: Float32, organic_matter: Float32) -> Float32:
    let total = sand + silt + clay
    if total < 1e-8:
        return 0.0
    let s_frac = sand / total
    let c_frac = clay / total
    let om_frac = organic_matter / 100.0
    let whc = 0.05 + 0.3 * c_frac + 0.1 * om_frac + 0.05 * (1.0 - s_frac)
    return whc * 100.0

fn extract_nutrient_index[n: Int](n_val: DTypePointer[Float32], p_val: DTypePointer[Float32], k_val: DTypePointer[Float32], ph: DTypePointer[Float32], out: DTypePointer[Float32]) -> None:
    for i in range(n):
        var score: Float32 = 0.0
        if ph[i] >= 6.0 and ph[i] <= 7.5: score += 20.0
        else: score += 10.0
        if n_val[i] > 280.0: score += 20.0
        if p_val[i] > 25.0: score += 20.0
        if k_val[i] > 280.0: score += 20.0
        out[i] = score

fn main() -> None:
    let whc = compute_water_holding_capacity(30.0, 40.0, 30.0, 2.0)
    print("Mojo Soil Analysis Kernels Ready, WHC:", whc)
