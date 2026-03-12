# Difference Report — PySDM

**Project:** PySDM  
**Project type:** Python library  
**Scope:** Basic functionality  
**Generated at:** 2026-03-12 09:26:26  
**Intrusiveness:** None  
**Workflow status:** ✅ Success  
**Test status:** ❌ Failed  

---

## 1) Project Overview

This change set introduces **8 new files** with **no modifications to existing files**, indicating an additive update pattern with low direct risk to existing code paths.  
Although CI/workflow execution succeeded, the **test suite failed**, which is currently the primary blocker for release readiness.

---

## 2) Change Summary

| Metric | Value |
|---|---:|
| New files | 8 |
| Modified files | 0 |
| Deleted files | 0 *(not reported)* |
| Intrusiveness | None |
| Workflow | Success |
| Tests | Failed |

### Interpretation
- The update appears structurally safe (no edits to existing files), but integration validity is not confirmed due to failing tests.
- Since no modified files are reported, failures may stem from:
  - New tests introduced with failing assertions
  - Environment/dependency issues triggered by new files
  - Discovery/import path side effects from added modules

---

## 3) Difference Analysis

## 3.1 File-level Impact
- **Additive-only diff**: 8 files added.
- **No regressions via direct edits** to legacy modules are expected.
- Potential indirect effects:
  - Package discovery/import behavior
  - New default configurations/data loaded at runtime
  - New test cases or fixtures affecting global test outcomes

## 3.2 Functional Impact
Given “Basic functionality” scope, likely impact areas:
- Core API surface expansion (new modules/classes/functions)
- Supplemental utilities or examples
- New test or validation logic

Without modified files, this likely represents **feature extension rather than refactor**.

---

## 4) Technical Analysis

## 4.1 CI vs Test Discrepancy
- **Workflow success** means pipeline steps executed correctly (lint/build/package stages likely okay).
- **Test failure** indicates logical/runtime mismatch:
  - Failing unit/integration assertions
  - Missing optional runtime dependencies
  - Non-deterministic tests (seed/time/platform sensitivity)
  - Version pinning drift in CI test environment

## 4.2 Risk Assessment

| Risk Area | Level | Notes |
|---|---|---|
| Backward compatibility | Low–Medium | No modified files, but imports/package init can still affect users |
| Runtime stability | Medium | New files may be loaded dynamically |
| Release readiness | High risk | Blocked by test failures |
| Rollback complexity | Low | Additive change is easy to isolate/revert |

---

## 5) Recommendations & Improvements

1. **Prioritize test triage (P0)**
   - Extract failing test list and stack traces.
   - Classify by root cause: product defect vs test defect vs env issue.
   - Re-run failures locally with identical dependency lockfile/container.

2. **Validate package boundaries**
   - Confirm new files are intentionally included/excluded in distribution (`pyproject.toml` / `MANIFEST.in`).
   - Check import side effects in `__init__.py` and module-level code.

3. **Harden reproducibility**
   - Pin critical dependency