# AutomationBench Review For Armour

## Purpose

Meg Risdal recommended Zapier's AutomationBench as a reference for reproducible
mocked API calls. This review records what is verifiable in the public source
and identifies the parts that should inform a hosted Armour pilot.

**Review status:** public source reviewed on 2026-06-20 at commit
[`ad19826`](https://github.com/zapier/AutomationBench/tree/ad19826a91cd8a1dd00202b918468d4a8a0776c2).
Kaggle should confirm whether a different internal version was intended.

## Verified Observations

1. **Simulated state, not live SaaS accounts.** Tasks initialize a typed
   `WorldState` containing app-specific records. Tool implementations read and
   mutate that in-memory state rather than call production SaaS APIs.
   ([world schema](https://github.com/zapier/AutomationBench/blob/ad19826a91cd8a1dd00202b918468d4a8a0776c2/automationbench/schema/world.py),
   [environment setup](https://github.com/zapier/AutomationBench/blob/ad19826a91cd8a1dd00202b918468d4a8a0776c2/automationbench/runner.py))
2. **Tasks declare initial state and assertions.** Each task provides a trigger,
   app state, available tools, and assertion specifications. The environment
   injects the hidden `world` argument into tool calls and can filter tools per
   task.
   ([runner](https://github.com/zapier/AutomationBench/blob/ad19826a91cd8a1dd00202b918468d4a8a0776c2/automationbench/runner.py),
   [support tasks](https://github.com/zapier/AutomationBench/blob/ad19826a91cd8a1dd00202b918468d4a8a0776c2/automationbench/domains/support/tasks.py))
3. **The mocked APIs preserve realistic interfaces.** REST-style route handlers
   dispatch to implementations that mutate simulated application records.
   ([Zendesk routes](https://github.com/zapier/AutomationBench/blob/ad19826a91cd8a1dd00202b918468d4a8a0776c2/automationbench/tools/api/routes/zendesk.py),
   [Zendesk implementation](https://github.com/zapier/AutomationBench/blob/ad19826a91cd8a1dd00202b918468d4a8a0776c2/automationbench/tools/api/impl/zendesk.py))
4. **Scoring is final-state and assertion based.** The rubric reports partial
   credit and strict completion. It excludes assertions already satisfied in
   the initial state unless explicitly retained, reducing reward for doing
   nothing. Its assertion registry also marks negative assertions intended to
   represent unwanted side effects.
   ([rubric](https://github.com/zapier/AutomationBench/blob/ad19826a91cd8a1dd00202b918468d4a8a0776c2/automationbench/rubric/__init__.py),
   [assertion registry](https://github.com/zapier/AutomationBench/blob/ad19826a91cd8a1dd00202b918468d4a8a0776c2/automationbench/rubric/registry.py))
5. **Public and private tasks are separated.** The repository documents a
   public task set and a held-out private set used for official scores.
   ([README](https://github.com/zapier/AutomationBench/blob/ad19826a91cd8a1dd00202b918468d4a8a0776c2/README.md))
6. **SaaS secrets are avoided, model credentials are not.** Simulated business
   tools need no real SaaS credentials. Running a model locally still requires
   the applicable model-provider key.
7. **ATIF is not an advertised public output contract.** The public exporter
   retains messages, tool calls, assertion results, and end state, while the
   runner uses its framework's internal trajectory state. The reviewed source
   does not claim that its exported runs are ATIF.
   ([exporter](https://github.com/zapier/AutomationBench/blob/ad19826a91cd8a1dd00202b918468d4a8a0776c2/automationbench/export.py))

## Mapping To `armour-kaggle`

Armour already shares several design choices:

- deterministic mocked tools with no live SaaS dependency
- explicit task-local initial state and tool outcomes
- structured tool-call records and ATIF-v1.7 trajectories
- exact positive completion requirements and negative policy boundaries
- strict reward separated from component metrics

The useful differences are intentional. AutomationBench primarily verifies the
resulting business state; Armour primarily verifies whether the execution trace
crossed an explicit policy boundary. A combined hosted design can retain both:

1. realistic typed state and state-transition assertions for task success
2. trace-level policy checks for forbidden actions, scope, evidence, and audit integrity

## Gaps To Reconcile

- Add held-out variants before treating public scores as launch-quality.
- Decide whether richer typed app state is needed beyond Armour's compact
  scenario records for the first pilot.
- Specify which negative assertions belong in outcome scoring versus trace
  compliance so the same violation is not counted opaquely twice.
- Confirm how Kaggle wants provider credentials supplied to hosted agents while
  keeping task tools credential-free.
- Confirm whether Kaggle requires ATIF at the trial root or accepts Harbor's
  nested agent trajectory artifact.

## Questions For Meg And Kaggle

1. Which AutomationBench package or task should Armour use as the closest
   mocked-API reference during the first hosted conversion?
2. Does Kaggle prefer final-state assertions and trace-policy checks in one
   verifier or as independent metrics?
3. Should Armour adopt AutomationBench-style typed world state in the pilot, or
   is the current compact state sufficient for ten tasks?
4. Can the held-out-task workflow follow AutomationBench's public/private split?
5. Is the internal Kaggle runner already able to preserve ATIF trajectories
   alongside final-state assertions?
