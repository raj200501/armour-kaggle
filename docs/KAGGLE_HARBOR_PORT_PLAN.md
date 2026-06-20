# Kaggle/Harbor Port Plan

## Why This Port Exists

Armour began as a custom Python evaluator for structured agent traces. The
Kaggle/Harbor port tests whether its central signal can live inside a standard
agent benchmark: task outcome remains separate from trace-level policy
compliance.

The port is now a ten-task Harbor dataset rather than a copy of the broader
prototype. This keeps the integration surface small enough to review while
covering distinct operational boundaries.

## Preserved Properties

- Safe and risky paths can produce the same successful outcome.
- Mocked tools make every action reproducible without external accounts or keys.
- Each violation points to the exact step, tool, policy, reason, dimension, and outcome state.
- `succeeded`, `denied`, and `attempted_only` remain distinct outcomes.
- Deterministic policy checks remain separate from future human or LLM judges.
- ATIF trajectories are retained as first-class artifacts.

## Implemented Dataset

The checked-in [`benchmark/`](../benchmark) directory contains ten Harbor tasks
covering customer data scope, deployment approval, credentials, payments, HR
confidentiality, retention, evaluation integrity, research confidentiality,
browser sessions, and security autonomy.

Each task contains:

- an explicit instruction and policy boundary
- a no-network Docker environment
- executable mocked tools
- a compliant oracle solution
- a Harbor verifier and numeric reward file
- safe/risky local behavior paths
- seven task-level acceptance tests

The adapter catalog and templates generate all tasks reproducibly. Repository
CI verifies generated-file consistency and runs the full local suite.

## Harbor Mapping

- Task schema: `1.3`
- Trajectory schema: `ATIF-v1.7`
- Agent artifact: `/logs/agent/trajectory.json`
- Verifier rewards: `/logs/verifier/reward.json`
- Local dataset manifest: `benchmark/dataset.toml`
- Aggregate metric: `benchmark/metric.py`

The aggregate metric exposes component means and the outcome-compliance gap.

## Remaining Kaggle Integration

The public repository can prove format compatibility and deterministic task
behavior. Kaggle must still select the hosted agent/model matrix, create or
approve hidden variants, run managed evaluation, configure the leaderboard,
and assign launch and maintenance ownership.

The concrete handoff and launch gates are in
[`KAGGLE_LAUNCH_SPEC.md`](KAGGLE_LAUNCH_SPEC.md).

## Deliberate Non-Claims

- This is not yet a Kaggle-hosted benchmark.
- The ten tasks are a pilot slice, not comprehensive safety coverage.
- Oracle and control validation are not model performance results.
- Explicit task rules do not replace human or LLM review for ambiguous policy.
- No affiliation, endorsement, or production readiness is claimed.

Current Harbor references:

- [Tasks](https://harborframework.com/docs/tasks)
- [Datasets](https://harborframework.com/docs/datasets)
- [Metrics](https://harborframework.com/docs/datasets/metrics)
- [Agent Trajectory Interchange Format](https://harborframework.com/docs/agents/trajectory-format)
