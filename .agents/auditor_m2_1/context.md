# Context: Forensic Auditor M2-1

- Working directory: /Users/pmsanch1/code/FORECAST/.agents/auditor_m2_1
- Role: teamwork_preview_auditor
- Task: Forensic audit of Milestone 2 (DF Module):
  1. Inspect `df/` source code for any hardcoded outputs, checksums, or facades.
  2. Verify authentic streaming batch processing and filter precomputation.
  3. Verify strictly zero concurrency / threading / OpenMP inside `df/`.
  4. Verify Darwin RSS ceiling monitoring and clean exit codes (0, 1, 2, 3).
  5. Verify audit trail in `CHANGELOG.md` and `docs/performance_history.csv`.
  6. Deliver verdict: CLEAN or INTEGRITY VIOLATION.
