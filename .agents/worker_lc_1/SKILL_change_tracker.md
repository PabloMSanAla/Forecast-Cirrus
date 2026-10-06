---
title: Change Tracker & Documentation
description: Maintain a complete, human-readable audit trail of every modification made to the FORECAST pipeline, including the rationale, implementation details, and measured impact.
---

# Agent: Change Tracker & Documentation

## Goal
Maintain a complete, human-readable audit trail of every modification made to the FORECAST pipeline, including the rationale, implementation details, and measured impact.

## Core Skills

### 1. Structured Changelog Management
- Append entries to `CHANGELOG.md` with the following format:

```
[YYYY-MM-DD HH:MM] Agent: <Name>
Module: <lc/df/dc/igm>

Action: <e.g., Added OpenMP to particle loop>

Rationale: <Why this was needed>

Performance Delta: <Before: Xs, After: Ys>

RAM Delta: <Before: X MB, After: Y MB>

```

### 2. Git Integration
- Stage all changed files (`git add .`).
- Generate a commit message that summarizes the agent's work.
- Tag commits with performance metrics (e.g., `git tag perf-v1.1-30pct`).

### 3. Impact Quantification
- Before applying changes, query the `test_validator` for baseline metrics.
- After changes, query again for optimized metrics.
- Calculate and log the exact deltas (speedup percentage, memory saved).

### 4. Decision Logging
- Record trade-offs: e.g., "Chose OpenMP static scheduling over dynamic to reduce overhead, as particle counts are uniform per snapshot."

## Files to Create or Modify
- `CHANGELOG.md` – Append new entries.
- `docs/performance_history.csv` – Maintain a machine-readable log of benchmarks.
- `.git/hooks/pre-commit` – Ensure that tests pass before allowing commits.

## Success Criteria
- Every code change has a corresponding changelog entry.
- A reviewer can understand the "why" behind each modification without reading the code.
- Performance trends are trackable over time.
