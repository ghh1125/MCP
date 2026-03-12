# Difference Report — `scanpy`

**Generated:** 2026-03-12 14:00:53  
**Repository:** `scanpy`  
**Project Type:** Python library  
**Scope:** Basic functionality  
**Change Intrusiveness:** None  
**Workflow Status:** ✅ Success  
**Test Status:** ❌ Failed  
**Files Changed:** 8 new, 0 modified

---

## 1) Project Overview

This update introduces **8 new files** to the `scanpy` repository without modifying existing files.  
Given the stated low intrusiveness and “basic functionality” scope, the change set appears additive and non-breaking in intent. However, despite successful workflow execution, the test suite currently reports failure, which blocks confidence in release readiness.

---

## 2) Difference Summary

## Change Statistics

| Metric | Value |
|---|---:|
| New files | 8 |
| Modified files | 0 |
| Deleted files | 0 (not reported) |
| Net effect | Additive only |

## High-Level Interpretation

- The update likely adds new modules/resources/tests/config/docs rather than altering current code paths.
- Because no existing files were modified, risk of direct regression from overwritten logic is low.
- **Key concern:** tests failed, indicating either:
  - newly added files introduced unmet dependencies or invalid assumptions, or
  - existing tests now detect issues due to discovery/import/environment effects from new files.

---

## 3) Technical Analysis

## CI/Workflow

- **Workflow:** successful → lint/build/automation pipeline steps likely completed.
- **Tests:** failed → functional correctness not yet validated.

This discrepancy often points to one of:
1. Environment mismatch between workflow steps and test runtime.
2. New files included tests that fail under current fixtures.
3. Packaging/import side effects caused by added modules.
4. Missing test data, optional dependency guards, or version pinning issues.

## Risk Assessment

- **Codebase Stability Risk:** Low–Medium (no direct modifications, but failing tests elevate uncertainty).
- **Release Risk:** High if deployed without resolving test failures.
- **Compatibility Risk:** Unknown until test failures are triaged (could affect Python versions, dependency matrix, or optional backends).

---

## 4) Recommendations & Improvements

1. **Block release until tests pass.**  
   Treat this as a quality gate failure.

2. **Triage failing tests immediately:**
   - Identify exact failing test modules and stack traces.
   - Classify as deterministic failure vs flaky/environmental.
   - Confirm whether failures are only in newly added files or impact existing suites.

3. **Validate packaging/import behavior:**
   - Ensure new files are correctly included/excluded in package metadata.
   - Check for import-time side effects in newly added modules.

4. **Dependency and matrix checks:**
   - Re-run tests across supported Python/dependency versions.
   - Verify optional dependencies are properly guarded (`extras`, lazy imports, skip markers).

5. **Add/adjust tests where needed:**
   - If new functionality was added, ensure complete happy-path + edge-case coverage.
   - If files are non-code assets/configuration, add smoke tests to ensure no unintended test discovery issues.

6. **Improve CI diagnostics:**
   - Publish concise failure summary artifact (failed tests, traceback, environment).
   - Add a fast “import smoke test” stage before full test matrix.

---

## 5) Deployment Information

## Current Deployment Readiness

- **Not ready for production/release** due to failed tests.

## Suggested Deployment Decision

- **Decision:** Hold deployment.
- **Condition to proceed:** 100% pass on required test jobs and no new critical warnings in CI.

## Rollout Strategy (once fixed)

- Use standard staged release (e.g., pre-release or RC tag if applicable).
- Monitor import errors and runtime regressions in downstream environments.
- Prepare quick rollback path (package version pin/revert tag) if post-release issues arise.

---

## 6) Future Planning

1. **Strengthen pre-merge checks**
   - Require passing tests for all required CI jobs.
   - Enforce branch protection against test-failing merges.

2. **Test architecture hardening**
   - Separate unit/integration/e2e markers clearly.
   - Isolate flaky tests and quarantine with tracking tickets.

3. **Change-intent templates**
   - For additive file-only changes, require a checklist:
     - packaging impact reviewed
     - test discovery impact reviewed
     - dependency impact reviewed

4. **Observability for CI quality**
   - Track test pass rate trend, mean time to fix red builds, and flaky-test frequency.

---

## 7) Executive Conclusion

The change set is structurally low-risk (**8 new files, no modifications**), but the **failed test status is a release blocker**.  
Priority should be rapid failure triage and remediation, followed by full CI re-validation. Once tests are green, this update can likely proceed with normal release controls.