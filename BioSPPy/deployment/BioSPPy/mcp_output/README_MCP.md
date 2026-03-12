# BioSPPy MCP (Model Context Protocol) Service README

## 1) Project Introduction

This MCP (Model Context Protocol) service wraps core BioSPPy capabilities for biosignal processing and feature extraction.  
It is designed for developer workflows where an LLM or external client needs consistent access to signal-analysis tools (ECG, EDA, EMG, PPG, RESP, EEG, HRV), shared DSP utilities, quality checks, plotting helpers, and optional biometrics/synthetic data utilities.

Typical use cases:
- Run end-to-end physiological signal pipelines
- Extract time/frequency/time-frequency/cepstral features
- Compute HRV and signal-quality metrics
- Build biometrics experiments (KNN/SVM/RandomForest wrappers)
- Generate synthetic ECG/EMG for testing

---

## 2) Installation Method

### Requirements
Core Python dependencies:
- numpy
- scipy
- matplotlib
- scikit-learn
- h5py
- bidict
- shortuuid
- joblib

Optional (recommended for extended workflows):
- pandas
- peakutils
- statsmodels

### Install with pip
pip install biosppy numpy scipy matplotlib scikit-learn h5py bidict shortuuid joblib

Optional extras:
pip install pandas peakutils statsmodels

Notes:
- Use Python virtual environments (venv/conda) to avoid version conflicts.
- If running on servers/containers, use a non-interactive matplotlib backend for plotting tasks.

---

## 3) Quick Start

### Basic import
from biosppy.signals import ecg, eda, emg, ppg, resp, eeg, hrv

### Run an ECG pipeline
result = ecg.ecg(signal=ecg_signal, sampling_rate=1000., show=False)

Typical ECG outputs include filtered signal, R-peaks, heart-rate series, and time vectors (exact return fields depend on BioSPPy version).

### Run other core pipelines
eda_result = eda.eda(signal=eda_signal, sampling_rate=1000., show=False)  
emg_result = emg.emg(signal=emg_signal, sampling_rate=1000., show=False)  
ppg_result = ppg.ppg(signal=ppg_signal, sampling_rate=1000., show=False)  
resp_result = resp.resp(signal=resp_signal, sampling_rate=1000., show=False)  
eeg_result = eeg.eeg(signal=eeg_signal, sampling_rate=256., show=False)

### HRV from RR intervals
hrv_result = hrv.hrv(rri=rri_ms, sampling_rate=4., show=False)

### Low-level DSP helpers
from biosppy.signals import tools  
filtered, _, _ = tools.filter_signal(signal=x, ftype='FIR', band='bandpass', order=101, frequency=[3, 45], sampling_rate=1000.)

---

## 4) Available Tools and Endpoints

Recommended MCP (Model Context Protocol) service endpoints:

- process.ecg  
  Run ECG preprocessing, peak detection, and heart-rate estimation.

- process.eda  
  Run EDA preprocessing and event/tonic-phasic related analysis.

- process.emg  
  Run EMG processing and onset-related computations.

- process.ppg  
  Run PPG pulse-related processing and fiducial extraction.

- process.resp  
  Process respiration signal and breathing-rate outputs.

- process.eeg  
  EEG-oriented processing and spectral feature workflows.

- process.hrv  
  HRV metrics from RR intervals.

- dsp.filter_signal  
  Generic filtering utility for custom pipelines.

- dsp.smoother  
  Signal smoothing helper.

- dsp.normalize  
  Signal normalization helper.

- features.time / features.frequency / features.time_freq / features.cepstral / features.phase_space  
  Feature extraction endpoints by domain.

- quality.assess  
  Signal quality metric computation.

- plotting.static / plotting.interactive  
  Visualization endpoints (headless-safe mode recommended in production).

- synth.ecg / synth.emg  
  Synthetic data generation for testing and benchmarking.

- biometrics.classify  
  Biometric model workflows using available wrappers (BaseClassifier, KNN, SVM, RandomForest, Combination).

---

## 5) Common Issues and Notes

- Sampling rate mismatch:  
  Most errors or poor outputs come from incorrect sampling_rate. Always validate it per channel.

- Signal shape/units:  
  Ensure 1D arrays where expected, and consistent units (e.g., RR intervals typically in ms in some workflows).

- Optional dependency gaps:  
  Some advanced routines may require optional packages (pandas, peakutils, statsmodels).

- Plotting in production:  
  Disable interactive plotting or set a non-GUI backend in containers/CI.

- Performance:  
  Long recordings and high sampling rates can be costly. Consider chunked processing and pre-filtering.

- Reproducibility:  
  Pin dependency versions for production MCP (Model Context Protocol) services.

---

## 6) Reference Links and Documentation

- Repository: https://github.com/scientisst/BioSPPy
- Main package: https://pypi.org/project/biosppy/
- Project README (usage/examples): https://github.com/scientisst/BioSPPy/blob/master/README.md
- Contribution guide: https://github.com/scientisst/BioSPPy/blob/master/CONTRIBUTING.md
- Example datasets/scripts: repository `examples/` and `example.py`