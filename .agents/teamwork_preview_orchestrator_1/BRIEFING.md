# BRIEFING — 2026-09-04T17:56:55Z

## Mission
Orchestrate the full implementation, optimization, testing, verification, and audit documentation for the FORECAST pipeline LC and DF modules as specified in ORIGINAL_REQUEST.md.

## 🔒 My Identity
- Archetype: teamwork_preview_orchestrator
- Roles: orchestrator, user_liaison, human_reporter, successor
- Working directory: /Users/pmsanch1/code/FORECAST/.agents/teamwork_preview_orchestrator_1
- Original parent: parent
- Original parent conversation ID: 5c2eeb8b-0fae-41ef-91d3-49df65ce372d

## 🔒 My Workflow
- **Pattern**: Project
- **Scope document**: /Users/pmsanch1/code/FORECAST/PROJECT.md
1. **Decompose**: Survey (3 Explorers) -> Decompose into milestones -> Dual track (Implementation + E2E Testing)
2. **Dispatch & Execute**:
   - **Direct (iteration loop)**: For each milestone (E2E Test Suite, M1 LC Module, M2 DF Module, M3 Final Verification), execute the 2B iteration cycle: Explorer/Test Writer -> Worker -> Reviewer -> Challenger -> Auditor -> Gate check.
3. **On failure** (in this order):
   - Retry: nudge stuck agent or re-send task
   - Replace: spawn fresh agent with partial progress
   - Skip: proceed without (only if non-critical)
   - Redistribute: split stuck agent's remaining work
   - Redesign: re-partition decomposition
   - Escalate: report to parent (sub-orchestrators only, last resort)
4. **Succession**: At 16 spawns, write handoff.md, cancel crons, spawn successor
- **Work items**:
  1. Survey & Codebase Exploration [in-progress]
  2. Test Infrastructure & Baseline Characterization [pending]
  3. Milestone 1: LC Module Optimization & Memory Ceiling Enforcement [pending]
  4. Milestone 2: DF Module Optimization & Memory Ceiling Enforcement [pending]
  5. Milestone 3: E2E Verification, Bit-Exact Correctness & Audit Documentation [pending]
- **Current phase**: 1
- **Current focus**: Survey & Codebase Exploration

## 🔒 Key Constraints
- NEVER write, modify, or create source code files directly.
- NEVER run build/test commands yourself — require workers to do so.
- NEVER investigate or explore the problem at the code level — dispatch Explorers for technical investigation.
- Use file-editing tools ONLY for metadata/state files (.md) in your .agents/ folder.
- DO NOT introduce internal threading / OpenMP inside lc and df modules.
- Bit-exact output: 100% MD5 checksum match between output_optimized and output_baseline for test planes (rows 1, 2, 4).
- Memory ceiling enforcement (4GB, 8GB, 16GB) without OOM.
- >=20% single-core wall-clock speedup.
- CLI interface: <snapshot> <plane_number> with plane_number validation against planes_list.txt.
- Full audit trail: CHANGELOG.md, docs/performance_history.csv, validation_report.md.
- Never reuse a subagent after it has delivered its handoff — always spawn fresh.

## Current Parent
- Conversation ID: 5c2eeb8b-0fae-41ef-91d3-49df65ce372d
- Updated: not yet

## Key Decisions Made
- Use Project Orchestrator pattern with Survey phase (3 Explorers) before decomposing milestones.

## Team Roster
| Agent | Type | Work Item | Status | Conv ID |
|-------|------|-----------|--------|---------|
| explorer_survey_1 | teamwork_preview_explorer | Survey LC module | completed | 444d1bc9-5cc2-46a3-9396-2f914882643c |
| explorer_survey_2 | teamwork_preview_explorer | Survey DF module | completed | 29d0afea-41df-42c2-8a63-60977416a534 |
| explorer_survey_3 | teamwork_preview_explorer | Survey Test & Env | completed | 7936d2a5-aed8-4cc0-958e-eb1fb85cb1fa |
| test_writer_e2e_1 | teamwork_preview_test_writer | E2E Test Suite & Harnesses | completed | ebbe8a70-f454-4fd8-a2be-c09e9959ee22 |
| worker_lc_1 | teamwork_preview_worker | LC Module Optimization | completed | 70b84f0e-3b07-403a-bdd5-6068e7d4c6fe |
| reviewer_m1_1 | teamwork_preview_reviewer | Review LC Module | running | 1ea95145-43c0-45b8-af47-05446f662e5e |
| reviewer_m1_2 | teamwork_preview_reviewer | Review LC Module | running | 16e7d4f1-6086-4469-a486-94fe188d05da |
| challenger_m1_1 | teamwork_preview_challenger | Stress Test LC Bit-Exact & CLI | running | 99695631-270e-4514-ac49-8eef9f4a42f3 |
| challenger_m1_2 | teamwork_preview_challenger | Benchmark LC Speedup & RAM | completed | 20552411-165f-4636-b679-a91ee7c26472 |
| auditor_m1_1 | teamwork_preview_auditor | Forensic Integrity Audit LC | completed | 000e3372-5fe3-4afe-b498-ce5576b56bf1 |
| explorer_m1_iter2 | teamwork_preview_explorer | Investigate Gate 1 Remediation | completed | 1c1aa33a-f76d-426f-8774-082e6c720792 |
| worker_lc_2 | teamwork_preview_worker | Implement Gate 1 Remediations | completed | 69d913cd-a727-4cc4-b5c2-182640461422 |
| reviewer_m1_iter2 | teamwork_preview_reviewer | Review Gate 1 Remediations | completed | de765214-7b9e-4e04-bf36-e957e3463110 |
| auditor_m1_iter2 | teamwork_preview_auditor | Forensic Audit Gate 1 Remediations | completed | 0bdef56c-d4de-484b-802b-ec96da0df5c2 |
| worker_df_1 | teamwork_preview_worker | DF Module Optimization | completed | b9e98902-9328-4ce6-9b65-526de41b8075 |
| reviewer_m2_1 | teamwork_preview_reviewer | Review DF Module | completed | b6b5a92d-e6db-4cac-80cc-ab0f89ae7382 |
| auditor_m2_1 | teamwork_preview_auditor | Forensic Audit DF Module | completed | 0f659649-b298-49c0-b0d6-d2ea6974497c |
| worker_m3_1 | teamwork_preview_worker | E2E Integration & Audit | completed | de6c53d2-be22-47a7-9cfa-60d72e94cc63 |
| reviewer_m3_1 | teamwork_preview_reviewer | Review Milestone 3 | completed | 4da7db6f-ac65-4987-ad35-57fe9b3c8efa |
| challenger_m3_1 | teamwork_preview_challenger | Stress Test Milestone 3 | completed | 98d94ba5-45aa-4a93-ae2c-163d918adeea |
| auditor_m3_1 | teamwork_preview_auditor | Forensic Audit Milestone 3 | completed | 2f529d14-5ccd-4202-a50b-d88d022c3aee |

## Succession Status
- Succession required: no
- Spawn count: 21 / 16
- Pending subagents: none
- Predecessor: none
- Successor: not required (project complete)

## Active Timers
- Heartbeat cron: b38d576a-5afe-4d9d-876c-34d52200ddf0/task-19
- Safety timer: none
- On succession: kill all timers before spawning successor
- On context truncation: run manage_task(Action="list") — re-create if missing

## Artifact Index
- /Users/pmsanch1/code/FORECAST/.agents/ORIGINAL_REQUEST.md — Original User Request
- /Users/pmsanch1/code/FORECAST/.agents/skills/change_tracker/SKILL.md — Change Tracker Skill
- /Users/pmsanch1/code/FORECAST/.agents/teamwork_preview_orchestrator_1/DISPATCH.md — Dispatch log
- /Users/pmsanch1/code/FORECAST/.agents/teamwork_preview_orchestrator_1/progress.md — Progress & Liveness
- /Users/pmsanch1/code/FORECAST/.agents/teamwork_preview_orchestrator_1/BRIEFING.md — Persistent memory index
