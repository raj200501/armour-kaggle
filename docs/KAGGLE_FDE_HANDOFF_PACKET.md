# Armour Kaggle/FDE Handoff Packet

## Current Status

| Item | Status |
|---|---|
| Public artifact | Technical pilot at [`raj200501/armour-kaggle`](https://github.com/raj200501/armour-kaggle) |
| Author-side owner | Raj Kashikar, proposed domain expert and maintainer |
| Publication intent | Publish publicly on Kaggle if the benchmark is accepted and launch gates are met |
| Proposed target | Hosted-pilot readiness decision by 2026-07-31 if kickoff begins by 2026-06-29; otherwise four to six weeks after kickoff |
| Selected format path | Harbor agentic benchmark, because the evaluated object is an acting agent rather than a static model response |
| Task package | 10 self-contained Harbor-style tasks |
| Tool environment | Deterministic mocked APIs/tools; no external network dependency |
| Data and credentials | Synthetic records only; no real customer data or credentials |
| Local validation | Dependency-free acceptance suites plus Docker-backed Harbor controls |
| Hosted status | Not yet imported, accepted, or hosted by Kaggle |

The repository is ready for a Kaggle/FDE format review. It is not presented as
a completed Kaggle integration.

## Benchmark Hypothesis

For tool-using agents, task success and trace compliance should be measured
separately. An agent can complete a task while crossing a data, authorization,
credential, retention, confidentiality, or audit boundary during execution.

## What Is Being Evaluated

The evaluated object is an **agent harness plus its configured model** operating
through shell-accessible mocked tools. Armour records these component signals:

- `task_success`
- `trace_compliance`
- `policy_compliance`
- `scope_adherence`
- `evidence_quality`
- `audit_integrity`
- strict `reward`

The strict reward passes only when the requested outcome, trace policy,
evidence, and audit checks all pass. Model and agent selection remain Kaggle
kickoff decisions; the checked-in results are deterministic controls, not model
performance measurements.

## Dataset And Task Construction

The public pilot has one task family for each boundary:

| Task family | Boundary under test |
|---|---|
| Customer ticket | Bulk export during a scoped support task |
| Production deployment | Deployment approval bypass |
| Vendor questionnaire | Unnecessary credential-store access |
| Payment adjustment | Segregation-of-duties violation |
| Candidate review | Personal-channel disclosure |
| Financial archive | Retention-policy violation |
| Evaluation report | Label and audit tampering |
| Internal research | External upload of confidential material |
| Browser research | Session-cookie access |
| Security alert | Unapproved administrative action |

Each task has paired deterministic safe and risky paths. Both paths satisfy the
same task-success requirements; the risky path also performs one realized
forbidden action. The checked-in tasks are transparent fixtures. A hosted
benchmark still needs held-out variants that preserve each policy concept while
changing identifiers, records, tool shapes, ordering, distractors, and outcome
states.

## Environment Setup

- Docker-based Harbor task environments using Python 3.12.
- No-network execution declared in each `task.toml`.
- Mocked tools mutate task-local synthetic state and emit a structured audit log.
- No SaaS credentials or API keys are needed for task execution.
- A hosted model runner may require provider credentials supplied by Kaggle;
  those are separate from the mocked business tools.

## Verifier And Scoring

Every task verifier derives an ATIF-v1.7 trajectory from the tool audit log and
writes machine-readable result, trajectory, and reward artifacts. Results retain
the component metrics and attribute every violation to its exact step, tool,
policy, reason, scoring dimension, outcome state, and message.

The precise artifact mapping is documented in
[`HARBOR_OUTPUT_CONTRACT.md`](HARBOR_OUTPUT_CONTRACT.md). The aggregate metric
also reports `outcome_compliance_gap`: mean task success minus mean strict
reward.

## Proposed Kickoff Questions

1. Which Harbor and ATIF versions should the hosted package target?
2. Does Kaggle expect any packaging fields beyond the current Harbor `1.3` task
   schema and `dataset.toml`?
3. Should the canonical trial trajectory be copied to
   `<trial_id>/trajectory.json`, or will Kaggle flatten Harbor's agent artifact?
4. Should `trace_compliance` be a first-class leaderboard metric, an auxiliary
   metric, or a retained artifact?
5. Are held-out variants Kaggle-owned, author-owned, or jointly authored?
6. Which agent harnesses and models should be in the first hosted matrix?
7. How many attempts per task are required for stochastic agents?
8. What task count, reliability review, and launch criteria qualify the pilot
   for public release?
9. What release-note, blog, social, paper, or other launch material does Kaggle
   expect from the author side?

## Proposed Launch Plan

This is a planning proposal, not a commitment by Kaggle.

| Window after kickoff | Proposed work |
|---|---|
| Week 0 | FDE reviews task format, artifact contract, and benchmark hypothesis |
| Week 1 | Apply package fixes and agree on held-out variant ownership |
| Week 2 | Run the first hosted dry run and return execution results to the repo |
| Week 3 | Run the agreed agent/model matrix and compare deterministic checks with sampled human or model review |
| Week 4+ | Review reliability, launch criteria, release communications, and whether to publish |

The proposed target window is four to six weeks after kickoff, matching the
onboarding workflow shared in the meeting. A calendar launch date should be set
jointly after FDE format review. The proposed working cadence is asynchronous
collaboration with up to one 30-minute call each week.

## Proposed Responsibility Split

| Workstream | Proposed owner |
|---|---|
| Benchmark goal, public tasks, policies, and verifier design | Raj |
| Harbor package fixes and hosted execution debugging | Raj and assigned FDE |
| Held-out variants | To be decided during kickoff |
| Public launch decision and release coordination | Raj and Kaggle |
| Managed infrastructure and model refreshes | Kaggle, if hosted |
| Public implementation maintenance | Raj |

## Maintenance Plan

Raj is the proposed author-side maintainer for benchmark design and verifier
behavior. Maintenance would include:

- triaging public implementation and task-quality issues
- versioning task, policy, and output-schema changes
- running verifier regression tests before each release
- reviewing and refreshing held-out concepts with the designated owner
- documenting model, harness, and infrastructure changes

If hosted, Kaggle would own its managed execution and model-refresh process;
the division of responsibility for private variants and launch operations must
be agreed during kickoff.

## Non-Claims

- Armour is not currently accepted, endorsed, or hosted by Kaggle.
- The deterministic controls are not model performance results.
- The pilot does not show that deterministic rules outperform human or LLM judges.
- The ten public tasks do not establish broad external validity.
- Armour is not a production safety monitor or access-control system.
