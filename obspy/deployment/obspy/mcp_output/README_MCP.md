# ObsPy MCP (Model Context Protocol) Service README

## 1) Project Introduction

This service exposes practical ObsPy capabilities through MCP (Model Context Protocol) for seismic workflows, including:

- Waveform reading/processing (`Stream`, `Trace`, `read`)
- Remote data retrieval via FDSN (`Client.get_waveforms`, `get_stations`, `get_events`)
- MiniSEED interoperability (read/write)
- Signal filtering (`bandpass`, `highpass`, `lowpass`, `bandstop`)
- Travel-time modeling (`TauPyModel`)
- Geodetic calculations (`gps2dist_azimuth`, `locations2degrees`)

Best suited for developer-facing automation, analysis assistants, and data-access tooling.

---

## 2) Installation Method

### Prerequisites
- Python 3.9+ recommended
- System build tools for scientific Python packages

### Core dependencies
- Required: `numpy`, `scipy`, `matplotlib`, `lxml`, `setuptools`
- Optional (feature-dependent): `cartopy`, `requests`, `sqlalchemy`, `geographiclib`, `pyproj`

### Install
- `pip install obspy`
- For optional geospatial/network/database features:
  - `pip install requests sqlalchemy geographiclib pyproj cartopy`

### Verify
- `python -c "import obspy; print(obspy.__version__)"`

---

## 3) Quick Start

### Read waveform and basic processing
from obspy import read  
st = read("example.mseed")  
st.filter("bandpass", freqmin=1.0, freqmax=20.0)  
print(st)

### Retrieve data from FDSN
from obspy.clients.fdsn import Client  
client = Client("IRIS")  
st = client.get_waveforms("IU", "ANMO", "00", "BHZ", "2020-01-01T00:00:00", "2020-01-01T00:10:00")  
print(st)

### Travel-time modeling
from obspy.taup import TauPyModel  
model = TauPyModel(model="iasp91")  
arrivals = model.get_travel_times(source_depth_in_km=10, distance_in_degree=30)  
print(arrivals[:3])

### Geodetic helpers
from obspy.geodetics import gps2dist_azimuth  
dist_m, az, baz = gps2dist_azimuth(48.1, 11.6, 40.7, -74.0)  
print(dist_m, az, baz)

---

## 4) Available Tools and Endpoints List

Recommended MCP (Model Context Protocol) service endpoints:

- `read_waveform`
  - Load local seismic files (MiniSEED and other ObsPy-supported formats).
- `filter_waveform`
  - Apply standard filters (`bandpass`, `highpass`, `lowpass`, `bandstop`) to traces/streams.
- `fdsn_get_waveforms`
  - Download waveform windows from FDSN providers.
- `fdsn_get_stations`
  - Fetch station/instrument metadata.
- `fdsn_get_events`
  - Query earthquake event catalogs.
- `mseed_read_write`
  - Explicit MiniSEED import/export operations.
- `taup_travel_times`
  - Compute phase arrivals from source depth and epicentral distance.
- `geodetic_distance_azimuth`
  - Compute distance/azimuth/back-azimuth from coordinate pairs.
- `cli_obspy_print`
  - Inspect waveform/event metadata from files.
- `cli_obspy_flinn_engdahl`
  - Resolve Flinn–Engdahl region for coordinates.
- `cli_obspy_reftek_rescue`
  - Recover Reftek data from partial/raw media.
- `cli_obspy_sds_report`
  - Generate SDS archive coverage/quality HTML reports.

---

## 5) Common Issues and Notes

- Some functionality needs optional packages (`cartopy`, `pyproj`, etc.).
- FDSN access depends on network availability and provider limits/timeouts.
- Large waveform windows can be memory-heavy; prefer chunked downloads.
- Plotting/imaging features may require GUI/backend configuration in headless environments.
- MiniSEED handling is robust, but format edge cases vary by source archives.
- Repository analysis indicates low intrusiveness risk and medium integration complexity.

---

## 6) Reference Links or Documentation

- Repository: https://github.com/obspy/obspy
- Main documentation: https://docs.obspy.org/
- FDSN client module: https://docs.obspy.org/packages/obspy.clients.fdsn.html
- TauP module: https://docs.obspy.org/packages/obspy.taup.html
- Signal processing: https://docs.obspy.org/packages/obspy.signal.html
- Geodetics: https://docs.obspy.org/packages/obspy.geodetics.html