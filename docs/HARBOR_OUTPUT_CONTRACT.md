# Harbor Output Contract

This document describes Armour's implemented artifacts and the proposed mapping
to the trial layout shown in the Kaggle benchmark material. The exact hosted
contract remains a Kaggle/FDE kickoff decision.

## Local Acceptance Outputs

Running `bash tests/test.sh` inside a generated task writes:

| Artifact | Purpose |
|---|---|
| `outputs/generated_safe_trajectory.json` | ATIF trajectory generated from the compliant mocked-tool path |
| `outputs/generated_risky_trajectory.json` | ATIF trajectory generated from the successful forbidden-action path |
| `outputs/safe_result.json` | Component scores and findings for the safe trajectory |
| `outputs/risky_result.json` | Component scores and exact violation for the risky trajectory |
| `outputs/safe_trajectory.json` | Evaluator-retained safe ATIF artifact |
| `outputs/risky_trajectory.json` | Evaluator-retained risky ATIF artifact |
| `outputs/combined_results.json` | Side-by-side safe/risky comparison |
| `outputs/reward.json` | Numeric acceptance-suite reward fields |

These files are local deterministic fixtures. They are ignored by Git and are
not model results.

## Harbor Runtime Outputs

Inside a Harbor task run, Armour uses the standard logs mount:

| Runtime path | Producer | Contents |
|---|---|---|
| `/logs/agent/trajectory.json` | Verifier from mocked-tool audit log | Canonical agent ATIF trajectory |
| `/logs/verifier/result.json` | Trace evaluator | Full multi-dimensional result and violations |
| `/logs/verifier/trajectory.json` | Trace evaluator | Retained ATIF trajectory used for scoring |
| `/logs/verifier/reward.json` | Trace evaluator | Numeric rewards consumed by Harbor |

Harbor then captures these artifacts under the trial result directory. In local
Harbor `0.14.0` validation, the top-level trial has `result.json`, while the
trajectory artifacts are retained under the agent and verifier subdirectories.

## Proposed Kaggle Trial Export

The format shown in the meeting material uses:

```text
<trial_id>/
├── result.json
├── trajectory.json
└── ... optional artifacts
```

The proposed mapping is:

- `<trial_id>/result.json`: Harbor trial result plus Armour component rewards
- `<trial_id>/trajectory.json`: canonical copy of the ATIF agent trajectory
- optional artifacts: full verifier result, reward components, logs, and
  environment metadata

Kaggle/FDEs should confirm whether their ingestion layer performs this flattening
or whether Armour should add a post-run adapter.

## Armour Result Fields

`/logs/verifier/result.json` requires:

- `schema_version`
- `task_id`
- `trace_id`
- `task_success`
- `trace_compliance`
- `policy_compliance`
- `scope_adherence`
- `evidence_quality`
- `audit_integrity`
- `outcome_state`
- `violations`
- `trajectory`

Each violation requires:

- `step`
- `tool`
- `policy`
- `reason`
- `dimension`
- `outcome_state`
- `message`

`/logs/verifier/reward.json` contains numeric values for `reward` and every
component metric so Harbor can aggregate them without parsing prose.

## Armour ATIF Fields

Armour-generated trajectories use `ATIF-v1.7` and require:

- `schema_version`
- `session_id`
- `agent` with `name`, `version`, and `model_name`
- ordered `steps`
- `final_metrics`
- `extra` task metadata

Each step requires a sequential `step_id`, `source`, and `message`. Tool steps
also include `tool_calls` with a stable call ID, function name, arguments, and
outcome state, plus linked `observation.results` entries using
`source_call_id`.

## Known Uncertainty

Armour's runtime artifacts are valid and sufficient for local Harbor execution.
The exact Kaggle/FDE trial-root layout, supported Harbor version, required
metadata, and artifact-retention policy must be confirmed before hosted launch.
