# Kaggle Launch Specification

## Objective

Publish Armour as a Kaggle-hosted agent benchmark that reports task outcome and
trace-level policy compliance as separate leaderboard signals.

This repository supplies the public technical pilot. Kaggle supplies the
hosted evaluation surface, managed model execution, private test material,
leaderboard, and launch process.

## Pilot Package

- Ten self-contained Harbor `1.3` tasks.
- ATIF-v1.7 trajectories derived from mocked-tool audit logs.
- Deterministic safe, risky, oracle, and no-op controls.
- Multi-dimensional numeric rewards.
- Dataset-level outcome-compliance-gap metric.
- Reproducible adapter and checked-in generated tasks.
- Dependency-free local acceptance tests and GitHub CI.

## Proposed Hosted Evaluation

For each agent/task attempt, retain these signals independently:

1. `task_success`
2. `evidence_quality`
3. `trace_compliance`
4. `policy_compliance`
5. `scope_adherence`
6. `audit_integrity`
7. strict `reward`

The public leaderboard should not collapse task success and compliance into a
single opaque number. A primary ranking can use strict reward while exposing
the component means and outcome-compliance gap.

## Public And Hidden Material

The ten checked-in tasks are transparent pilot fixtures. A hosted benchmark
should add private variants that preserve each policy concept while changing:

- identifiers and non-sensitive records
- tool names and argument shapes
- call ordering and irrelevant distractor tools
- completion wording
- denied, attempted-only, and succeeded outcomes
- policy thresholds and scope relationships

Hidden variants should be reviewed for semantic equivalence and should never
contain real credentials or personal data.

## Proposed Agent Matrix

Final selection belongs to Kaggle. A useful pilot matrix would include at least
one shell/code agent and one general tool-using agent, with repeated runs where
the agent is stochastic. Candidate Harbor-supported harnesses include Gemini
CLI, Claude Code, Codex, and Terminus-2. This is a discussion proposal, not a
claim that those systems have been evaluated here.

## Launch Gates

- Kaggle confirms the supported Harbor and ATIF versions.
- Kaggle chooses agents, models, repetitions, and compute limits.
- Hidden variants are authored and held outside the public repository.
- Oracle passes every hosted task.
- No-op and malformed controls fail without verifier exceptions.
- At least one non-oracle agent completes end-to-end execution.
- False-positive and false-negative review is completed on sampled trajectories.
- Metric names and leaderboard ranking are agreed.
- Ownership, issue triage, versioning, and maintenance cadence are documented.

## Smallest Kaggle Experiment

1. Import the ten public tasks into Kaggle's Harbor execution path.
2. Run one selected agent/model with three attempts per task.
3. Retain task success and all compliance dimensions.
4. Review every successful-but-noncompliant trajectory.
5. Add one hidden variant per policy class.
6. Decide whether Armour should launch as a standalone benchmark, auxiliary
   metric, or reusable evaluator.

## Decisions Needed From Kaggle

1. Which agent and model should be used for the first non-oracle run?
2. Should trace compliance be a first-class leaderboard metric or an artifact?
3. Who owns hidden-variant construction and storage?
4. What task count and run count qualify the pilot for public launch?
5. Which Kaggle/FDE owner reviews the Harbor package and manages integration?

## Current Boundary

Everything in the public technical package can be completed and validated
outside Kaggle. Hosted publication cannot be completed unilaterally: it needs
Kaggle access, private test infrastructure, and an internal launch owner.
