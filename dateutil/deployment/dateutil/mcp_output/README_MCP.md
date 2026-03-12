# dateutil MCP (Model Context Protocol) Service README

## 1) Project Introduction

This service wraps the `python-dateutil` library as an MCP (Model Context Protocol) service for robust date/time handling in LLM workflows.

Main capabilities:
- Parse flexible human-readable datetime strings
- Parse strict ISO-8601 datetime strings
- Perform calendar-aware arithmetic (`relativedelta`)
- Generate recurring schedules (`rrule` / `rruleset`)
- Handle time zones, DST ambiguity, and imaginary times
- Provide utility helpers (today, default tz assignment, delta comparisons)
- Compute Easter dates

Repository analyzed: `https://github.com/dateutil/dateutil`

---

## 2) Installation Method

### Requirements
- Python 3.x
- `python-dateutil`
- `six` (runtime dependency used by dateutil)

### Install
pip install python-dateutil

If you are implementing this as an MCP (Model Context Protocol) server, also install your MCP runtime/framework (depends on your stack), then add `python-dateutil` to the same environment.

---

## 3) Quick Start

Typical service actions your MCP (Model Context Protocol) server can expose:

- Parse free-form datetime:
  - Input: `"next Friday 5pm"`
  - Backend: `dateutil.parser.parse(...)`

- Parse ISO datetime:
  - Input: `"2026-03-12T10:30:00+00:00"`
  - Backend: `dateutil.parser.isoparser`

- Date arithmetic:
  - Add one month, set weekday rules, etc.
  - Backend: `dateutil.relativedelta.relativedelta`

- Recurrence generation:
  - Build schedules like “every Tuesday at 09:00”
  - Backend: `dateutil.rrule`

- Time zone normalization:
  - Detect ambiguous/non-existent local times around DST transitions
  - Backend: `dateutil.tz.datetime_ambiguous`, `datetime_exists`, `resolve_imaginary`

- Utility checks:
  - `within_delta`, `today`, `default_tzinfo`

---

## 4) Available Tools and Endpoints List

Recommended MCP (Model Context Protocol) service endpoint design:

1. `datetime.parse`
- Purpose: Parse natural-language or mixed-format datetime strings
- Core module: `dateutil.parser._parser.parse`
- Notes: Powerful but permissive; validate inputs for production workflows

2. `datetime.parse_iso`
- Purpose: Strict ISO-8601 parsing
- Core module: `dateutil.parser.isoparser`
- Notes: Prefer when deterministic format validation is required

3. `datetime.add_relativedelta`
- Purpose: Calendar-aware arithmetic (months/years/weekday semantics)
- Core module: `dateutil.relativedelta.relativedelta`

4. `datetime.recurrence.generate`
- Purpose: Generate repeated datetime sequences
- Core module: `dateutil.rrule.rrule`, `rruleset`, `rrulestr`
- Notes: Supports RFC 5545-style recurrence logic

5. `timezone.convert_or_resolve`
- Purpose: Apply/convert time zones and handle DST edge cases
- Core module: `dateutil.tz.tz*`, `datetime_exists`, `datetime_ambiguous`, `resolve_imaginary`, `enfold`

6. `calendar.easter`
- Purpose: Compute Easter date by year
- Core module: `dateutil.easter.easter`

7. `datetime.utils`
- Purpose: Small helpers (`today`, `default_tzinfo`, `within_delta`)
- Core module: `dateutil.utils`

---

## 5) Common Issues and Notes

- Ambiguous or non-existent local times:
  - DST transitions can produce duplicate or invalid local timestamps.
  - Use `datetime_ambiguous`, `datetime_exists`, and `resolve_imaginary`.

- Parsing ambiguity:
  - Free-form parsing may infer unintended day/month ordering.
  - Prefer strict ISO endpoint for critical pipelines.

- Time zone data differences:
  - Platform behavior may vary (especially Windows-specific timezone handling via `tzwin`).

- Performance:
  - Large recurrence expansions can be expensive.
  - Require range limits (`start`, `end`, `count`) in endpoint contracts.

- Testing/dev dependencies:
  - `pytest`, `hypothesis`, and Sphinx tooling are for tests/docs, not required at runtime.

---

## 6) Reference Links / Documentation

- Upstream repository: https://github.com/dateutil/dateutil
- Official docs: https://dateutil.readthedocs.io/
- PyPI package: https://pypi.org/project/python-dateutil/
- RFC 5545 recurrence background: https://datatracker.ietf.org/doc/html/rfc5545

If needed, I can also generate a production-ready `mcp_server.py` endpoint skeleton aligned to the tool list above.