# Product Security Automation — Evidence Index

This file maps implemented security claims to executable or inspectable evidence. A capability should not be represented as complete unless the cited evidence exists and supports the claim.

## Artifact identity and integrity

Status: Implemented in first increment

Specification:
- `ai/spec.md` §7.1 Artifact identity and integrity

Architecture:
- `ai/architecture.md` §3 TB-1 Untrusted artifact boundary
- `ai/architecture.md` §4 Tamper path
- `ai/architecture.md` §5 `artifact` component

Implementation:
- `src/product_security_automation/models.py` — immutable `ArtifactIdentity`, SHA-256 validation, stable reason codes
- `src/product_security_automation/artifact.py` — chunked SHA-256 hashing and exact-artifact verification

Executable evidence:
- `tests/test_artifact.py::test_hash_is_deterministic_for_identical_bytes`
- `tests/test_artifact.py::test_verification_accepts_unchanged_artifact`
- `tests/test_artifact.py::test_tampering_changes_digest_and_is_rejected`
- `tests/test_artifact.py::test_missing_artifact_fails_closed`
- `tests/test_models.py::test_artifact_identity_is_immutable`
- `tests/test_models.py::test_artifact_identity_rejects_non_hex_digest`
- `tests/test_models.py::test_artifact_identity_rejects_path_as_name`

## Decision and execution-boundary models

Status: Implemented as architecture foundation; execution adapters are not yet implemented

Specification / platform context:
- `ai/execution-modes.md`
- proposed Engineering Platform Execution Modes Standard at `JonCunninghamDev/engineering-platform` commit `e95e7e0f65bff7ba20aeca4b88182700c0cc2222`

Implementation:
- `ExecutionMode` defines explicit `active`, `observe`, `demo`, and `test` runtime modes.
- `DecisionResult` represents immutable deterministic PASS/FAIL output before execution.
- `PlannedAction` represents inspectable intent separately from side-effect execution.
- `SIGN_ARTIFACT` actions must be bound to an exact immutable `ArtifactIdentity`.
- failed decisions cannot plan privileged signing actions.
- failed decisions may still plan non-privileged evidence/audit actions.

Executable evidence:
- `tests/test_models.py::test_execution_modes_are_explicit_and_stable`
- `tests/test_models.py::test_sign_action_must_bind_exact_artifact_identity`
- `tests/test_models.py::test_decision_result_can_plan_signing_after_pass`
- `tests/test_models.py::test_failed_decision_cannot_plan_signing`
- `tests/test_models.py::test_failed_decision_can_still_plan_audit_evidence`
- `tests/test_models.py::test_decision_result_is_immutable`

Local verification command:

```bash
pytest
```

Current local verification evidence: 13 passing tests.

## Not yet implemented

The following remain specified but should not yet be represented as implemented evidence:

- active/observe/demo/test execution adapters;
- development PKI lifecycle and trust validation;
- deterministic release policy engine;
- signing authorization and Cosign integration;
- independent signature verification;
- audit/provenance persistence;
- Syft/Trivy evidence adapters;
- CI security gates;
- AI advisory layer and deterministic fallback.
