# Astroquery MCP (Model Context Protocol) Service README

## 1) Project Introduction

This project provides an MCP (Model Context Protocol) service layer over `astroquery`, exposing astronomy data access as LLM-friendly tools without modifying upstream provider logic.

### Purpose
- Offer a thin adapter for popular astronomy services (SIMBAD, VizieR, MAST first).
- Normalize `astropy`/table-like outputs into JSON-safe MCP (Model Context Protocol) responses.
- Add centralized controls for timeout, row limits, retries, and error mapping.

### Main Functions
- Object/name resolution and catalog queries.
- Observation/product search and retrieval metadata.
- Optional TAP/ADQL async workflows (phase 2+).
- Unified error and response schemas across heterogeneous providers.

---

## 2) Installation Method

### Requirements
- Python `>=3.10`
- Core dependencies:
  - `astropy`, `numpy`, `requests`, `beautifulsoup4`, `html5lib`, `keyring`, `pyvo`
- Optional (feature-dependent):
  - `regions`, `Pillow`, `lxml`, `pandas`, `matplotlib`

### Install
- Install astroquery stack:
  - `pip install astroquery astropy pyvo requests beautifulsoup4 html5lib keyring numpy`
- If your MCP (Model Context Protocol) runtime is separate, install your server framework in the same environment.
- Keep service wrappers external to `astroquery` source (composition-based integration).

---

## 3) Quick Start

### Typical startup flow
1. Initialize MCP (Model Context Protocol) service server.
2. Create wrapped clients (e.g., `SimbadClass`, `VizierClass`, `ObservationsClass`).
3. Register tools/endpoints.
4. Apply global guards (timeout, max rows, polling interval).
5. Return normalized JSON-safe payloads.

### Example usage flow
- Call `simbad.resolve_object` with object name (e.g., “M31”) → get canonical ID + coordinates.
- Call `vizier.query_catalog` with catalog + constraints → get tabular rows/columns.
- Call `mast.search_observations` with target/position/mission filters → get observation/product summaries.

---

## 4) Available Tools and Endpoints List

Recommended phased exposure:

### Phase 1 (read-only, low risk)
- `simbad.resolve_object`
  - Resolve target names and fetch basic metadata.
- `simbad.query_region`
  - Region-based lookup around coordinates/radius.
- `vizier.query_catalog`
  - Query specific catalogs with constraints and row limits.
- `vizier.find_catalogs`
  - Discover catalogs by keyword/topic.
- `mast.search_observations`
  - Search observation records (mission/instrument filters).
- `mast.list_products`
  - List downloadable product metadata for selected observations.

### Phase 2 (TAP/ADQL, async lifecycle)
- `tap.submit_job`
  - Submit ADQL query jobs (async).
- `tap.get_job_status`
  - Poll current status for submitted jobs.
- `tap.fetch_results`
  - Retrieve completed TAP results.
- `tap.cancel_job`
  - Cancel running TAP jobs.
- `gaia.launch_adql`
  - Gaia-specific ADQL query helper.

### Phase 3 (specialized astronomy domains)
- `sdss.query_region`
  - Imaging/spectra access for SDSS region queries.
- `sdss.get_spectra`
  - Retrieve spectrum references/metadata.
- `horizons.ephemerides`
  - Ephemerides for moving solar-system targets.
- `horizons.vectors`
  - State vectors for dynamics workflows.
- `horizons.elements`
  - Orbital elements access.

---

## 5) Common Issues and Notes

- No built-in CLI entry points in upstream repo: prefer import-based service wrappers.
- Keep wrappers thin: do not fork or patch provider internals.
- Normalize `astropy.table.Table`, quantities, and time objects before returning MCP (Model Context Protocol) responses.
- Use strict defaults:
  - max rows
  - request timeout
  - async polling interval
  - total runtime budget
- Authentication-required providers should be opt-in and gated by environment secrets.
- Reuse astroquery caching; add MCP (Model Context Protocol)-level cache keys only for deterministic read tools.
- Map provider-specific exceptions to stable service error codes (`INVALID_INPUT`, `UPSTREAM_TIMEOUT`, `AUTH_REQUIRED`, `NOT_FOUND`, etc.).
- Remote services may rate-limit or be intermittently unavailable; implement retries/backoff.

---

## 6) Reference Links / Documentation

- Astroquery repository: https://github.com/astropy/astroquery
- Astroquery docs: https://astroquery.readthedocs.io/
- Astropy docs: https://docs.astropy.org/
- PyVO docs (for TAP/VO workflows): https://pyvo.readthedocs.io/

If you want, I can also generate a production-ready `README.md` variant with environment variables, JSON schemas for each endpoint, and a minimal testing checklist.