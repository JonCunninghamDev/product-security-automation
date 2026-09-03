# Product Security Automation — Execution Modes

Status: Draft v0.1

This project adopts the proposed `engineering-platform` Execution Modes Standard from branch `agent/execution-modes-standard`, commit `e95e7e0f65bff7ba20aeca4b88182700c0cc2222`.

This proposal is not yet part of the published `engineering-platform` `v0.1.0` release. The published platform release remains the baseline for shared steering; this file documents an explicit project-level adoption of the proposed standard for validation through concrete use.

## Core rule

Product security decisions are mode-independent.

The same artifact identity, evidence normalization, policy logic, reason codes, authorization rules, and security invariants must be used regardless of execution mode.

Modes may alter side-effect execution, external adapters, fixtures, narration, persistence destinations, and user interaction. They must not weaken or replace the rules used to make a release/security decision.

The intended flow is:

```text
artifact/input
  -> normalization
  -> deterministic security decision
  -> planned actions
  -> execution boundary
       active  -> perform authorized side effects
       observe -> suppress side effects and record intent
       demo    -> safe scenario adapters plus narration/evidence
       test    -> deterministic fixtures and assertions
```

## Active mode

Active mode performs the real local workflow authorized by deterministic policy.

Expected v1 behaviors:

- calculate artifact identity;
- generate required evidence;
- evaluate deterministic release policy;
- create development PKI material when explicitly requested;
- sign only an artifact with a valid passing evaluation bound to the exact artifact digest;
- independently verify signature and trust;
- write authoritative local audit evidence;
- optionally invoke the advisory AI layer after the deterministic security result exists.

Active mode must fail closed when authorization, trust, required evidence, signing material, or verification is invalid.

## Observe mode

Observe mode follows the same input, evidence, policy, and authorization path as active mode while suppressing consequential side effects.

For this project, observe mode must not:

- generate persistent signing keys or certificates;
- invoke a real signing operation;
- write an authoritative release/signing audit event;
- invoke external notification or cloud actions;
- allow AI or user interaction to promote a planned action into execution.

Observe mode should calculate and record what active mode would have attempted, including:

- artifact digest;
- policy decision and reason codes;
- planned signing action;
- planned signing identity;
- planned verification action;
- planned audit event;
- whether each action was suppressed;
- suppression reason.

Example:

```json
{
  "mode": "observe",
  "artifact_sha256": "...",
  "decision": "PASS",
  "planned_actions": [
    {
      "action": "SIGN_ARTIFACT",
      "executed": false,
      "reason": "side effects suppressed by observe mode"
    }
  ]
}
```

Observe-mode decisions must be comparable with active-mode decisions for identical inputs.

## Demo mode

Demo mode is the primary portfolio/reviewer experience.

It must use the same core product-security logic as active mode while providing safe, deterministic scenarios, readable narration, and optional user interaction.

Initial named demo scenarios:

1. `happy-path`
   - valid artifact;
   - required evidence present;
   - deterministic policy passes;
   - safe local demo signing/verification path succeeds;
   - audit evidence is displayed;
   - advisory explanation is shown if available.

2. `tampered-artifact`
   - artifact identity is established;
   - bytes are changed;
   - digest/verification fails;
   - release/signing path remains blocked.

3. `unauthorized-signing`
   - signing is requested without a valid passing evaluation for the exact artifact digest;
   - signing boundary rejects the action;
   - rejection evidence is displayed.

4. `expired-or-untrusted-certificate`
   - certificate validation fails deterministically;
   - the artifact is not release-ready.

5. `ai-unavailable`
   - deterministic decision still completes correctly;
   - advisory layer degrades to deterministic fallback text;
   - security outcome is unchanged.

Demo mode may support prompts such as stepping through evidence, choosing a failure scenario, or intentionally tampering with a sample artifact. Interaction must not create an alternate business/security rule path.

Where practical, each demo scenario should have a non-interactive form suitable for CI and should share scenario setup and assertions with integration tests.

## Test mode

Test mode provides deterministic automated evidence for the security invariants demonstrated above.

Initial expectations:

- no persistent external side effects;
- ephemeral keys/material only inside temporary test directories when PKI tests are added;
- deterministic fixtures;
- explicit assertions for decisions, reason codes, planned actions, executed/suppressed actions, and evidence output;
- unit tests for pure policy/domain behavior;
- integration tests for complete scenario flows using safe adapters.

The current artifact-identity increment is the first test-mode evidence: deterministic hashing, unchanged-artifact verification, tamper rejection, missing-artifact failure, immutable identity, and model validation.

## Promotion model

For new high-risk capabilities, this project should prefer:

```text
test -> demo -> observe -> active
```

Examples:

- artifact identity begins in test/demo because it has no consequential external side effect;
- signing authorization must have tests and demo failure cases before active signing is enabled;
- any future AWS/KMS or external integration should prove deterministic behavior locally, then run observe-only where practical before active use.

Promotion is evidence-based. A capability is not promoted merely because a mode implementation exists.

## Evidence requirements

Each substantial workflow should expose enough structured information to answer:

- what input was evaluated;
- what deterministic decision was reached;
- why that decision was reached;
- what actions were planned;
- which actions were executed;
- which actions were suppressed;
- why an action was suppressed or rejected;
- which mode was active;
- what scenario/evaluation ID correlates the evidence.

Mode must be present in structured logs and audit/demo evidence.

## Implementation consequences

Future application services should separate planning from execution. A preferred shape is:

```text
DecisionResult
  + PlannedAction[]
        -> ExecutionAdapter
```

The policy engine must never branch on mode to produce a weaker decision.

Execution adapters may branch on mode to perform, suppress, simulate safely, or assert actions.

This separation should be established before privileged signing or external integrations are implemented.
