# PsychoPy MCP (Model Context Protocol) Service README

## 1) Project Introduction

This MCP (Model Context Protocol) service provides a practical integration layer over key PsychoPy runtime capabilities, focused on:

- Service lifecycle and discovery (via PsychoPy’s service system)
- Experiment component loading for Builder/Coder workflows
- Hardware device inventory/open/close operations
- Non-GUI experiment compilation and execution helpers

Primary integration targets in PsychoPy include:

- `psychopy.services` (core service discovery/load APIs)
- `psychopy.experiment.services` (service component bridging)
- `psychopy.hardware.manager` (device management)
- `psychopy.session` (runtime orchestration)
- `psychopy.scripts.psyexpCompile` (Builder `.psyexp` compilation)

---

## 2) Installation Method

### Requirements

- Python 3.8+ (recommended: 3.10+)
- Core dependencies:
  - numpy
  - scipy
  - packaging
  - requests
  - json_tricks

Optional (feature-dependent): wxPython, PyQt/PySide, pyglet, pygame, psychtoolbox, sounddevice, pyo, opencv-python, python-vlc, eyetracker SDKs, vendor hardware drivers.

### Install

- Install PsychoPy:
  - `pip install psychopy`
- Or install from source repository:
  - `pip install .`

For headless/server use, prefer minimal optional GUI/media dependencies unless needed by your MCP (Model Context Protocol) tools.

---

## 3) Quick Start

### A. Validate PsychoPy import

- `python -c "import psychopy; print(psychopy.__version__)"`

### B. Launch app entry (optional)

- `python -m psychopy.app`

### C. Compile Builder experiment (non-GUI-friendly)

- `psyexpCompile /path/to/experiment.psyexp`

### D. Typical MCP (Model Context Protocol) flow

1. Discover/load services (`psychopy.services`)
2. Load experiment service components (`psychopy.experiment.services`)
3. Query/open required hardware (`psychopy.hardware.manager`)
4. Start/stop runtime session (`psychopy.session`)

---

## 4) Available Tools and Endpoints List

Recommended MCP (Model Context Protocol) endpoints for this service layer:

- `services.list`
  - List available PsychoPy services
  - Maps to: `listServices`, discovery APIs

- `services.discover`
  - Trigger rescan/discovery of installed services
  - Maps to: `discoverServices`

- `services.load`
  - Load/activate a specific service by name
  - Maps to: `loadService`, activation APIs

- `experiment.services.load_components`
  - Load Builder/Coder components contributed by services
  - Maps to: `psychopy.experiment.services.loadServiceComponents`

- `hardware.list_devices`
  - Enumerate available devices and metadata
  - Maps to: `DeviceManager.getAvailableDevices`

- `hardware.open_device`
  - Open/init device handle for runtime use
  - Maps to: `DeviceManager.openDevice`

- `hardware.close_device`
  - Close/release device handle
  - Maps to: `DeviceManager.closeDevice`

- `session.start`
  - Start a PsychoPy runtime session context
  - Maps to: `Session.start`

- `session.stop`
  - Stop/cleanup a session
  - Maps to: `Session.stop`

- `experiment.compile`
  - Compile `.psyexp` into runnable scripts
  - Maps to: `psychopy.scripts.psyexpCompile`

---

## 5) Common Issues and Notes

- Environment complexity is high:
  - PsychoPy supports many optional backends and hardware integrations.
  - Keep MCP (Model Context Protocol) deployments profile-based (minimal vs full-featured).

- GUI vs headless:
  - Some features require display/audio backends.
  - For server environments, prefer compile/session/device endpoints that do not require full desktop UI.

- Hardware reliability:
  - Device access depends on OS permissions, vendor SDKs, and drivers.
  - Implement retry/timeouts and explicit close semantics in MCP (Model Context Protocol) tools.

- Version compatibility:
  - Pin PsychoPy and key dependency versions for stable MCP (Model Context Protocol) behavior.
  - Validate service/component loading in CI before deployment.

- Performance:
  - Initial import/discovery can be non-trivial.
  - Cache discovery results where safe, and lazy-load heavy modules.

---

## 6) Reference Links / Documentation

- Repository: https://github.com/psychopy/psychopy
- Main docs: https://www.psychopy.org/
- Contributing guide: https://github.com/psychopy/psychopy/blob/master/CONTRIBUTING.md
- Tests reference: `psychopy/tests/README.md`
- CLI entry modules:
  - `python -m psychopy.app`
  - `psychopy.scripts.psyexpCompile`
  - `psychopy.scripts.psychopy-pkgutil`