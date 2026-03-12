# SciPy MCP (Model Context Protocol) Service README

## 1) Project Introduction

This MCP (Model Context Protocol) service exposes practical SciPy capabilities to LLM agents and developer tools.  
It is designed for numerical/scientific workflows such as:

- Linear algebra (`solve`, `svd`, `eig`, `qr`)
- Optimization (`minimize`, `least_squares`, `linprog`, `milp`)
- Integration/ODEs (`quad`, `solve_ivp`)
- Interpolation (`interp1d`, `griddata`, `RegularGridInterpolator`)
- Sparse matrices and sparse solvers (`csr_matrix`, `spsolve`, `cg`, `eigs`)
- Signal processing (`convolve`, `butter`, `welch`, `find_peaks`)
- Statistics (`ttest_ind`, `pearsonr`, `bootstrap`, distributions)
- FFT (`fft`, `rfft`, `fftn`)
- Special functions (`gamma`, `erf`, `logsumexp`)
- Spatial algorithms (`KDTree`, `Delaunay`, `ConvexHull`)

Repository analyzed: https://github.com/scipy/scipy

---

## 2) Installation Method

### Prerequisites
- Python 3.10+ recommended
- `numpy` (required)
- Compiled SciPy runtime (BLAS/LAPACK backend such as OpenBLAS)
- Build toolchain only if building from source (C/C++/Fortran)

### Install core runtime
pip install -U numpy scipy

### Optional developer/test extras
pip install -U pytest mpmath matplotlib threadpoolctl pooch pybind11 pythran

### Verify installation
python -c "import scipy; print(scipy.__version__)"

---

## 3) Quick Start

### Basic service usage flow
1. Start your MCP (Model Context Protocol) host/runtime.
2. Register this SciPy service in your MCP server config.
3. Call endpoints by module + function name with JSON-like arguments.
4. Return numeric arrays/scalars/statistical summaries to the caller.

### Example calls (conceptual)
- `linalg.solve` with matrix `A` and vector `b` to solve linear systems.
- `optimize.minimize` with objective function definition and initial guess `x0`.
- `integrate.solve_ivp` for ODE systems over a time span.
- `stats.ttest_ind` for two-sample hypothesis testing.
- `fft.rfft` for real-valued spectral analysis.

---

## 4) Available Tools and Endpoints List

Suggested endpoint groups for this MCP (Model Context Protocol) service:

- `scipy.show_config`  
  Returns build/runtime configuration (BLAS/LAPACK/backend details).

- `linalg.*`  
  Dense linear algebra: `solve`, `inv`, `det`, `svd`, `eig`, `qr`, `lu`, `cholesky`, `lstsq`.

- `optimize.*`  
  Local/global optimization and root finding: `minimize`, `minimize_scalar`, `root`, `root_scalar`, `least_squares`, `linprog`, `milp`, `differential_evolution`, `basinhopping`.

- `integrate.*`  
  Quadrature and ODE integration: `quad`, `quad_vec`, `dblquad`, `nquad`, `solve_ivp`, `odeint`, `simpson`, `trapezoid`.

- `interpolate.*`  
  1D/ND interpolation: `interp1d`, `griddata`, `interpn`, spline APIs, regular-grid interpolators.

- `sparse.*` and `sparse.linalg.*`  
  Sparse matrix construction and solvers: `csr_matrix`, `coo_matrix`, `diags`, `spsolve`, `cg`, `gmres`, `eigs`, `svds`.

- `signal.*`  
  DSP/filtering/spectral tools: `convolve`, `lfilter`, `filtfilt`, `butter`, `welch`, `spectrogram`, `stft`, `find_peaks`.

- `stats.*`  
  Distributions, tests, and resampling: `norm`, `t`, `chi2`, `ttest_ind`, `pearsonr`, `spearmanr`, `bootstrap`, `permutation_test`, `gaussian_kde`.

- `fft.*`  
  Fast Fourier transforms: `fft`, `ifft`, `rfft`, `irfft`, `fftn`, `ifftn`, `fftshift`, `fftfreq`.

- `special.*`  
  Special/transcendental functions: `gamma`, `gammaln`, `erf`, `erfc`, `beta`, Bessel family, `logsumexp`.

- `spatial.*`  
  Geometry and nearest-neighbor: `KDTree`, `cKDTree`, `Delaunay`, `ConvexHull`, `Voronoi`, distance utilities.

---

## 5) Common Issues and Notes

- Binary compatibility:
  - Keep `numpy` and `scipy` versions compatible.
  - Prefer wheels unless you explicitly need source builds.

- Build-from-source complexity:
  - Requires working C/C++/Fortran toolchain and BLAS/LAPACK setup.
  - Use OpenBLAS where possible for simpler setup.

- Performance:
  - Use vectorized NumPy/SciPy operations.
  - Prefer sparse structures for large sparse systems.
  - Be careful with very large dense decompositions (memory-heavy).

- Numerical stability:
  - Scale inputs for optimization/integration where applicable.
  - Check solver diagnostics (`OptimizeResult`, warnings, convergence flags).

- Runtime environment:
  - In container/CI setups, pin versions for reproducibility.
  - For threaded workloads, tune BLAS thread count if oversubscription appears.

---

## 6) Reference Links / Documentation

- SciPy repository: https://github.com/scipy/scipy  
- SciPy docs: https://docs.scipy.org/doc/scipy/  
- API reference root: https://docs.scipy.org/doc/scipy/reference/  
- Build/setup notes (repo docs): `doc/README.md` in repository  
- PyPI package: https://pypi.org/project/scipy/