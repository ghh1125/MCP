# NeuroKit MCP (Model Context Protocol) Service README

## 1) Project Introduction

This service wraps core NeuroKit2 biosignal processing APIs into MCP (Model Context Protocol)-friendly tools for developer workflows.

It is designed for:
- End-to-end physiological signal processing (ECG, EDA, PPG, RSP, EMG, EOG)
- HRV computation
- Event detection and epoch creation
- Signal preprocessing and spectral analysis
- Built-in demo data access for testing

Repository: https://github.com/neuropsychology/NeuroKit

---

## 2) Installation Method

### Requirements
- Python 3.8+ (recommended)
- Core dependencies:
  - numpy
  - scipy
  - pandas
  - matplotlib

Optional (tool-dependent):  
scikit-learn, mne, PyWavelets, nolds, biosppy, cvxopt, opencv-python, imageio, numba

### Install commands
- Install NeuroKit2:
  pip install neurokit2

- (Optional) install common extras manually:
  pip install scikit-learn mne PyWavelets nolds biosppy cvxopt opencv-python imageio numba

---

## 3) Quick Start

### Basic import
import neurokit2 as nk

### Typical service-side function calls
- ECG pipeline: nk.ecg_process(signal, sampling_rate=...)
- EDA pipeline: nk.eda_process(signal, sampling_rate=...)
- PPG pipeline: nk.ppg_process(signal, sampling_rate=...)
- Respiration pipeline: nk.rsp_process(signal, sampling_rate=...)
- EMG pipeline: nk.emg_process(signal, sampling_rate=...)
- EOG pipeline: nk.eog_process(signal, sampling_rate=...)

### Demo data for smoke tests
data = nk.data("bio_resting_8min_200hz")

### HRV from peaks/intervals
hrv_features = nk.hrv(peaks, sampling_rate=...)

---

## 4) Available Tools and Endpoints List

Recommended MCP (Model Context Protocol) service endpoints:

- `bio_process`  
  Multimodal processing orchestrator for combined biosignal channels.

- `ecg_process`  
  ECG cleaning, R-peak detection, rate/features extraction.

- `eda_process`  
  EDA cleaning and tonic/phasic decomposition with peak-related outputs.

- `ppg_process`  
  PPG cleaning, peak extraction, and derived metrics.

- `rsp_process`  
  Respiration cleaning, phase/rate extraction, and related features.

- `emg_process`  
  EMG cleaning and activation-related metrics.

- `eog_process`  
  EOG cleaning, blink/peak feature extraction.

- `hrv`  
  Time, frequency, and nonlinear HRV features.

- `signal_filter`  
  General-purpose filtering utility for preprocessing.

- `signal_psd`  
  Power spectral density computation utility.

- `events_find`  
  Event/onset detection in time-series.

- `epochs_create`  
  Epoch segmentation around events for event-related analyses.

- `complexity`  
  High-level complexity feature aggregation (can be computationally heavy).

- `data`  
  Access built-in datasets for examples and tests.

---

## 5) Common Issues and Notes

- Optional dependency errors:  
  Some tools require non-core libraries (especially EEG/video/advanced methods). Install missing packages based on traceback.

- Sampling rate mismatches:  
  Incorrect `sampling_rate` is a common cause of poor peak detection and invalid metrics.

- Performance considerations:  
  `complexity`, some HRV nonlinear metrics, and long recordings can be CPU-intensive. Consider downsampling/chunking.

- Data format expectations:  
  Most pipelines expect 1D numeric arrays/Series and clean timestamps. Validate inputs before calling endpoints.

- Environment reproducibility:  
  Pin versions in your service deployment for stable outputs across environments.

---

## 6) Reference Links / Documentation

- NeuroKit repository:  
  https://github.com/neuropsychology/NeuroKit

- NeuroKit2 package/docs entry:  
  https://neuropsychology.github.io/NeuroKit/

- Source structure highlights:  
  `neurokit2/ecg`, `neurokit2/eda`, `neurokit2/ppg`, `neurokit2/rsp`, `neurokit2/hrv`, `neurokit2/signal`, `neurokit2/events`, `neurokit2/epochs`