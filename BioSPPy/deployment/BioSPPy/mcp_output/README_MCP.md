# BioSPPy MCP (Model Context Protocol) Service README

## 1) Project Introduction

This MCP (Model Context Protocol) service wraps core BioSPPy capabilities for biosignal processing, feature extraction, quality assessment, clustering, plotting, and data I/O.

Primary service goals:
- Standardized processing pipelines for physiological signals (ECG, PPG, EDA, EMG, EEG, RESP, ABP, BVP, PCG, ACC)
- Reusable low-level signal tools (filtering, spectra, statistics, synchronization)
- Optional biometrics and clustering workflows
- Storage utilities (TXT/JSON/HDF5/ZIP)

Repository: https://github.com/PIA-Group/BioSPPy

---

## 2) Installation Method

### Requirements
- Python 3.x
- Core dependencies:
  - numpy
  - scipy
  - matplotlib
  - scikit-learn
  - h5py
  - bidict
  - shortuuid
  - six
- Optional:
  - mne (advanced EEG workflows)
  - pywavelets

### Install commands
- Install from PyPI:
  - pip install biosppy
- Or install from source:
  - git clone https://github.com/PIA-Group/BioSPPy.git
  - cd BioSPPy
  - pip install -r requirements.txt
  - pip install .

---

## 3) Quick Start

### Typical MCP (Model Context Protocol) service flow
1. Load a signal (e.g., ECG samples as a NumPy array)
2. Call the corresponding processing service endpoint
3. Read standardized outputs (timestamps, filtered signal, peaks/onsets, rates)
4. Optionally generate plots or persist outputs

### Example usage patterns
- ECG processing: `biosppy.signals.ecg.ecg(signal, sampling_rate=1000, show=False)`
- PPG processing: `biosppy.signals.ppg.ppg(signal, sampling_rate=1000, show=False)`
- EDA processing: `biosppy.signals.eda.eda(signal, sampling_rate=1000, show=False)`
- Generic filtering: `biosppy.signals.tools.filter_signal(...)`
- Spectrum: `biosppy.signals.tools.power_spectrum(...)`
- Save structured data: `biosppy.storage.serialize(data, path)`

Expected output style is tuple-like structured returns (commonly timestamps, processed signals, events, and derived rates/features).

---

## 4) Available Tools and Endpoints List

Below is a practical MCP (Model Context Protocol) service endpoint map (grouped by module).

### Signal Pipelines (`biosppy.signals.*`)
- `abp.abp`, `abp.find_onsets_zong2003`  
  Arterial blood pressure processing and onset detection.
- `acc.acc`, `acc.time_domain_feature_extractor`, `acc.frequency_domain_feature_extractor`  
  Accelerometer processing and feature extraction.
- `bvp.bvp`  
  Blood volume pulse processing.
- `ecg.ecg`, plus segmenters (`hamilton_segmenter`, `christov_segmenter`, etc.), SQI metrics (`bSQI`, `sSQI`, `kSQI`, `pSQI`, `fSQI`)  
  ECG full pipeline, beat detection, quality assessment.
- `eda.eda`, `eda.basic_scr`, `eda.kbk_scr`  
  Electrodermal activity processing and SCR detection.
- `eeg.eeg`, `eeg.car_reference`, `eeg.get_power_features`, `eeg.get_plf_features`  
  EEG referencing and feature extraction.
- `emg.emg`, `emg.find_onsets`, and multiple onset detectors  
  Electromyography processing and muscle activation onset detection.
- `pcg.pcg`, `pcg.find_peaks`, `pcg.identify_heart_sounds`  
  Phonocardiogram processing and heart sound analysis.
- `ppg.ppg`, `ppg.find_onsets_elgendi2013`, `ppg.find_onsets_kavsaoglu2016`, `ppg.ppg_segmentation`  
  PPG pipeline and onset/segmentation methods.
- `resp.resp`  
  Respiration processing.

### Signal Utilities (`biosppy.signals.tools`)
- Filtering: `get_filter`, `filter_signal`, `smoother`, `OnlineFilter`
- Frequency/phase: `power_spectrum`, `welch_spectrum`, `band_power`, `analytic_signal`, `phase_locking`
- Time-series ops: `zero_cross`, `find_extrema`, `finite_difference`, `windower`
- Similarity/join: `distance_profile`, `signal_self_join`, `signal_cross_join`
- HR and sync: `get_heart_rate`, `synchronize`
- Stats: `signal_stats`, `normalize`, `pearson_correlation`, `rms_error`

### Plotting (`biosppy.plotting`, `biosppy.inter_plotting`)
- Signal-specific visualization endpoints: `plot_ecg`, `plot_ppg`, `plot_eda`, `plot_emg`, `plot_eeg`, etc.
- Utility plots: `plot_filter`, `plot_spectrum`, `plot_clustering`, `plot_biometrics`

### Biometrics and ML Helpers
- `biosppy.biometrics`: classifiers (KNN, SVM), run assessment, cross-validation, score combination
- `biosppy.clustering`: kmeans, hierarchical, dbscan, consensus clustering, outlier utilities
- `biosppy.metrics`: pairwise distances and squareform helpers

### Data and Persistence (`biosppy.storage`)
- Serialization: `serialize`, `deserialize`
- JSON: `dumpJSON`, `loadJSON`
- HDF5: `alloc_h5`, `store_h5`, `load_h5`
- TXT: `store_txt`, `load_txt`
- ZIP: `pack_zip`, `unpack_zip`, `zip_write`

### Misc
- `biosppy.stats`: correlation/tests/regression
- `biosppy.timing`: `tic`, `tac`, `clear`, `clear_all`
- `biosppy.synthesizers.ecg.ecg`: synthetic ECG generation

---

## 5) Common Issues and Notes

- Version compatibility: ensure NumPy/SciPy/scikit-learn versions are mutually compatible.
- Plotting in headless environments: disable interactive display (`show=False`) and save to files.
- EEG advanced features: install optional `mne` when required.
- Large files / high sampling rates: prefer batch processing and avoid unnecessary plotting for performance.
- HDF5 storage: confirm `h5py` is installed and file paths are writable.
- Return formats: many functions return tuple-like structures; check field ordering before production integration.
- No built-in CLI detected: this is primarily a Python API-oriented service integration.

---

## 6) Reference Links / Documentation

- GitHub: https://github.com/PIA-Group/BioSPPy
- Project README: https://github.com/PIA-Group/BioSPPy/blob/master/README.md
- Changelog: https://github.com/PIA-Group/BioSPPy/blob/master/CHANGELOG.md
- Source modules (signals): https://github.com/PIA-Group/BioSPPy/tree/master/biosppy/signals
- Examples data: https://github.com/PIA-Group/BioSPPy/tree/master/examples