## 2026-09-05T00:00:15Z

<USER_REQUEST>
You are a Challenger agent (teamwork_preview_challenger) for Milestone 3 Gate Evaluation.
Your working directory is /Users/pmsanch1/code/FORECAST/.agents/challenger_m3_1.

MANDATORY INPUTS (read before starting):
- ORIGINAL_REQUEST.md: /Users/pmsanch1/code/FORECAST/.agents/ORIGINAL_REQUEST.md
- PROJECT.md: /Users/pmsanch1/code/FORECAST/.agents/teamwork_preview_orchestrator_1/PROJECT.md
- Worker M3 Handoff: /Users/pmsanch1/code/FORECAST/.agents/worker_m3_1/handoff.md
- Validation Report: /Users/pmsanch1/code/FORECAST/validation_report.md

TASKS:
Empirically challenge and stress-test the integrated FORECAST pipeline:
1. Stress-test memory ceiling breach detection:
   - Run `python3 tests/monitor_rss.py --ceiling-gb 0.005 -- ./lc/executable_lc 98 0 0.005`
   - Run `python3 tests/monitor_rss.py --ceiling-gb 0.005 -- ./df/executable_df 98 0 0.005`
   - Verify both binaries detect the breach and exit with contract exit code 3.
2. Challenge CLI argument validation and error handling:
   - Test invalid snapshots (`999 0`), invalid planes (`98 999`), negative snapshot (`-98 0`), excess args (`98 0 4.0 extra`), non-numeric inputs (`abc def`), and missing files (`70 34`).
   - Confirm contract exit codes (1 for invalid args/plane, 2 for missing data/config) and zero segmentation faults or crashes.
3. Challenge bit-exact catalog verification:
   - Run `python3 tests/verify_md5.py` and `python3 tests/verify_md5.py --baseline-only`. Confirm 6/6 catalogs match expected hashes.
4. Challenge single-core performance:
   - Run `python3 tests/benchmark_speedup.py`. Verify speedups exceed 20% on all test planes without any multi-threading.
5. Record your findings and provide your verdict: APPROVE or CHALLENGE_FAILED in /Users/pmsanch1/code/FORECAST/.agents/challenger_m3_1/handoff.md and notify parent via message.
</USER_REQUEST>
