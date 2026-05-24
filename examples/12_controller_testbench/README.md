# Controller Testbench

## Motivation

Most scientific and industrial publications on wind turbine control innovations evaluate their designs against only a subset of the full range of load cases. This makes it difficult to judge the true efficacy and readiness of novel controllers for adoption in industrial turbines. The knowledge required to select relevant load cases and the lack of convenient tooling make comprehensive evaluation cumbersome.

The **Controller Testbench** addresses this gap by providing a standardized benchmarking pipeline that automatically generates cases, runs simulations, post-processes results, and produces reports. It builds on NREL's [WEIS](https://github.com/WISDEM/WEIS) software stack and uses the [ROSCO](https://github.com/NREL/ROSCO) controller as the default baseline, though custom controllers are also supported.

## Overview

The testbench follows a four-stage pipeline:

1. **Case Generation** — Design load cases (DLCs 1.1, 1.3, 1.6), stability simulations (steady, step winds), power-curve (AEP) runs, and global-performance ramps are generated from a single YAML configuration file.
2. **Simulation** — OpenFAST simulations are executed with a Bladed-style dynamic library controller. Runs can be parallelised with MPI for efficiency.
3. **Post-Processing** — Results are reduced to fatigue and extreme loads, power capture and quality metrics, frequency-domain measures (tower/blade natural frequencies, N-per-rev), pitch actuator travel/wear, and load revolution/duration statistics.
4. **Reporting** — The companion Jupyter notebook (`WTCBench_Reporting.ipynb`) visualises the post-processed data as binned performance plots and time-series comparisons.

## Files in this Directory

| File | Description |
|------|-------------|
| `controller_testbench.py` | Main script — loads the YAML config, generates DLCs, runs OpenFAST, and post-processes results. |
| `WTCBench_Reporting.ipynb` | Jupyter notebook for visualising and comparing testbench outputs. |
| `reporting_helpers.py` | Plotting and data-loading utilities used by the notebook. |
| `testbench_options.yaml` | Full testbench configuration for the IEA 15 MW turbine. |
| `testbench_options_lite.yaml` | Lightweight configuration (fewer wind speeds, shorter sims) for quick testing. |
| `testbench_options_5mw.yaml` | Configuration for the NREL 5 MW reference turbine. |
| `testbench_options_lite_5mw.yaml` | Lite configuration for the 5 MW turbine. |
| `testbench_options_5mw_legacy.yaml` | Legacy 5 MW configuration. |

## Quick Start

### Prerequisites

- A working WEIS/WTCBench environment (see the top-level `environment.yml`).
- OpenFAST and TurbSim executables on your `PATH` (or specify paths in the YAML).

### Running

```bash
# Serial execution
python controller_testbench.py

# Parallel execution (4 ranks)
mpirun -np 4 python controller_testbench.py
```

By default the script uses `testbench_options_lite.yaml`. To change this, edit the `INPUT_FILE` variable at the top of `controller_testbench.py`.

### Viewing Results

After the simulations complete, open `WTCBench_Reporting.ipynb` and point it at the output directory specified in your YAML (`output_directory`). The notebook will load the pickled summary statistics and produce comparison plots.

## Configuration

The testbench YAML has the following top-level sections:

- **`Testbench_Options`** — Output directory, number of cores, and paths to OpenFAST/TurbSim executables.
- **`Controller`** — Optional `path2dll` (path to the controller shared library) and `DISCON_in` (path to the DISCON input file). If omitted, the default ROSCO library and the DISCON defined in the OpenFAST model are used.
- **`OpenFAST`** — Path to the OpenFAST input set (`openfast_dir`, `openfast_file`) and an optional regulation trajectory for initial conditions.
- **`PostProcessing`** — Binning time for statistics and frequency bins of interest (e.g., platform pitch, 1P, 3P).
- **`Turbine_Info`** — Turbine parameters (cut-in/cut-out/rated wind speeds, hub height, rotor radius, IEC class) and flags for offshore/floating/monopile configurations.
- **`DLC_driver`** — Metocean conditions and a list of DLCs to run, each with wind speeds, number of seeds, and simulation timing.

## Comparing Controllers

To benchmark a novel controller against the baseline:

1. Run the testbench once with the baseline controller (default ROSCO).
2. Run it again with your custom controller by setting `Controller.path2dll` and optionally `Controller.DISCON_in` in the YAML.
3. Use the reporting notebook to load both output directories and compare results side by side.

## Reference

> D. Zalkind, A. Gupta, J. Frederik, and S. P. Mulders, "WTCBench: A Standardized Benchmarking Procedure for Wind Turbine Control Solutions," *Wind Energy Science Conference*, Nantes, France, 2025.
