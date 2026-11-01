# Crop Growth Simulation in Mojo
fn compute_growing_degree_days[t_steps: Int](tmin: DTypePointer[Float32], tmax: DTypePointer[Float32], tbase: Float32, out_gdd: DTypePointer[Float32]) -> None:
    var cumulative: Float32 = 0.0
    for i in range(t_steps):
        var tavg = (tmin[i] + tmax[i]) / 2.0
        if tavg < tbase: tavg = tbase
        if tavg > 30.0: tavg = 30.0
        let gdd = tavg - tbase
        if gdd > 0.0:
            cumulative += gdd
        out_gdd[i] = cumulative

fn compute_biomass_accumulation[days: Int](gdd_cum: DTypePointer[Float32], radiation: DTypePointer[Float32], lai: DTypePointer[Float32], rue: Float32, out_biomass: DTypePointer[Float32]) -> None:
    var biomass: Float32 = 0.0
    for i in range(days):
        let intercepted = lai[i] * (1.0 - exp(-0.5 * lai[i]))
        let daily_growth = radiation[i] * intercepted * rue
        biomass += daily_growth
        out_biomass[i] = biomass

fn simulate_phenology[gdd_total: Int](gdd: DTypePointer[Float32], emergence_gdd: Float32, flowering_gdd: Float32, maturity_gdd: Float32) -> Int32:
    var stage: Int32 = 0
    for i in range(gdd_total):
        if gdd[i] >= emergence_gdd and stage == 0:
            stage = 1
        if gdd[i] >= flowering_gdd and stage == 1:
            stage = 2
        if gdd[i] >= maturity_gdd and stage == 2:
            stage = 3
            break
    return stage

fn main() -> None:
    print("Mojo Crop Growth Simulation Kernels Ready")
