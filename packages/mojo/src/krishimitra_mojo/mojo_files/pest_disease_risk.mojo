# Pest & Disease Risk Scoring in Mojo
fn compute_pest_risk_score[n: Int](temp: DTypePointer[Float32], humidity: DTypePointer[Float32], rainfall: DTypePointer[Float32], wind: DTypePointer[Float32], leaf_wetness: DTypePointer[Float32], out_risk: DTypePointer[Float32]) -> None:
    for i in range(n):
        var risk: Float32 = 0.0
        let t = temp[i]
        let h = humidity[i]
        let r = rainfall[i]
        let lw = leaf_wetness[i]
        if t >= 20.0 and t <= 30.0:
            risk += 25.0 * (1.0 - abs(t - 25.0) / 10.0)
        if h > 70.0:
            risk += 20.0 * ((h - 70.0) / 30.0)
        if r > 0.0:
            risk += 15.0
        if lw > 0.5:
            risk += 25.0 * lw
        if risk > 100.0: risk = 100.0
        if risk < 0.0: risk = 0.0
        out_risk[i] = risk

fn compute_disease_risk_score[n: Int](temp: DTypePointer[Float32], humidity: DTypePointer[Float32], leaf_wetness_duration: DTypePointer[Float32], rainfall: DTypePointer[Float32], out_risk: DTypePointer[Float32]) -> None:
    for i in range(n):
        var risk: Float32 = 0.0
        let t = temp[i]
        let h = humidity[i]
        let lwd = leaf_wetness_duration[i]
        if h > 80.0:
            risk += 30.0
        if lwd > 6.0:
            risk += 30.0
        if t >= 15.0 and t <= 25.0 and h > 80.0:
            risk += 25.0
        if risk > 100.0: risk = 100.0
        if risk < 0.0: risk = 0.0
        out_risk[i] = risk

fn batch_fungal_risk[n: Int](temp: DTypePointer[Float32], rh: DTypePointer[Float32], hours_wet: DTypePointer[Float32], out: DTypePointer[Float32]) -> None:
    for i in range(n):
        var risk: Float32 = 0.0
        if rh[i] >= 90.0 and hours_wet[i] >= 12.0:
            risk = 90.0
        elif rh[i] >= 85.0 and hours_wet[i] >= 8.0:
            risk = 70.0
        elif rh[i] >= 80.0 and hours_wet[i] >= 6.0:
            risk = 50.0
        else:
            risk = 20.0
        if temp[i] >= 15.0 and temp[i] <= 25.0:
            risk += 10.0
        if risk > 100.0: risk = 100.0
        out[i] = risk

fn main() -> None:
    print("Mojo Pest & Disease Risk Scoring Kernels Ready")
