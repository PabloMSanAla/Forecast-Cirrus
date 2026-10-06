## 2026-09-04T18:36:44Z

<USER_REQUEST>
You are a Challenger agent (teamwork_preview_challenger).
Your working directory is /Users/pmsanch1/code/FORECAST/.agents/challenger_m1_1.

MANDATORY INPUTS (read before starting):
- ORIGINAL_REQUEST.md: /Users/pmsanch1/code/FORECAST/.agents/ORIGINAL_REQUEST.md
- PROJECT.md: /Users/pmsanch1/code/FORECAST/.agents/teamwork_preview_orchestrator_1/PROJECT.md
- Scope Document: /Users/pmsanch1/code/FORECAST/.agents/sub_orch_m1_1/SCOPE.md
- Worker Handoff: /Users/pmsanch1/code/FORECAST/.agents/worker_lc_1/handoff.md

TASKS:
Empirically challenge and stress-test the LC module implementation:
1. Re-compile and execute test planes (Rows 1, 2, 4: Snap 98, planes 0, 1, 3) under 4GB ceiling.
2. Verify 100% bit-exact MD5 match against `/Volumes/PMSAdrive/pmsa/storage/TNG/output_baseline/lc/`.
3. Challenge CLI argument handling with adversarial/edge inputs:
   - Missing arguments (`./lc/executable_lc`)
   - Non-numeric inputs (`./lc/executable_lc abc def`)
   - Negative numbers (`./lc/executable_lc 98 -1`)
   - Out of bounds plane index (`./lc/executable_lc 98 9999`)
   - Mismatched snapshot (`./lc/executable_lc 99 1`)
   - Verify that all invalid inputs exit with non-zero code and descriptive error without segfaulting.
4. Challenge memory ceiling enforcer:
   - Run with deliberately low ceiling (e.g. 0.01 GB) to verify it detects limit breach and exits cleanly with code 3.
5. Record your findings and provide verdict (APPROVE or CHALLENGE_FAILED) in /Users/pmsanch1/code/FORECAST/.agents/challenger_m1_1/handoff.md.
</USER_REQUEST>
