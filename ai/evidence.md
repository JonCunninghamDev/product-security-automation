# Product Security Automation — Evidence Index

This file maps implemented security claims to executable or inspectable evidence. A capability should not be represented as complete unless the cited evidence exists and supports the claim.

## Artifact identity and integrity

Status: Implemented in first increment

Specification:
- `ai/spec.md` §8.1 Artifact identity and product context

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

## Product and caller context

Status: Implemented as typed domain foundation; authorization rules are not yet implemented

Specification / architecture:
- `ai/spec.md` §6 Product Cyber service model
- `ai/spec.md` §7 Core user stories
- `ai/architecture.md` §3 Domain context

Implementation:
- `CallerContext` explicitly models `engineering-ci`, `release-pipeline`, `factory`, and `operator` as generic portfolio caller contexts.
- `ArtifactType` explicitly models firmware, software binary, installer, and generic release artifact categories.
- `ProductArtifact` composes immutable artifact identity with artifact type, normalized fictional product-family identifier, and caller context.
- changing caller context does not change or replace the exact underlying artifact identity.
- caller/product context is modeled as security-relevant input only; no current code grants signing authority based on caller type.

Executable evidence:
- `tests/test_models.py::test_caller_contexts_are_generic_and_explicit`
- `tests/test_models.py::test_artifact_types_are_generic_and_explicit`
- `tests/test_models.py::test_product_artifact_composes_exact_identity_with_context`
- `tests/test_models.py::test_product_artifact_is_immutable`
- `tests/test_models.py::test_product_family_must_be_normalized_safe_identifier`
- `tests/test_models.py::test_caller_context_does_not_modify_artifact_identity`

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

Integrated verification after the Product Cyber context and development PKI increments:
27 passing tests.

## Bounded development PKI

Status: Implemented for the local development/demo trust model

Specification / architecture:
- `ai/spec.md` §7.2 PKI fundamentals
- `ai/architecture.md` §6 `pki` and §7 PKI scope
- `ai/decisions.md` D-005 and D-008

Implementation:
- `src/product_security_automation/pki/development.py` creates an ephemeral P-256
  development CA and directly issued signer/service certificates.
- certificate inspection produces a secret-free metadata projection.
- validation checks certificate time bounds, direct issuer relationship, CA
  constraints, exact trusted-root fingerprint, root self-signature, and leaf
  signature.
- private-key export is explicit, encrypted, owner-only, and refuses symbolic-link
  targets where the platform provides `O_NOFOLLOW`.
- invalidation removes the ephemeral root from the configured trust set; rotation
  replaces the root and its leaves.

Executable evidence:
- `tests/pki/test_development.py::test_ephemeral_ca_issues_signer_and_service_certificates_with_metadata`
- `tests/pki/test_development.py::test_certificate_from_trusted_development_ca_validates`
- `tests/pki/test_development.py::test_expired_certificate_is_rejected_with_stable_reason`
- `tests/pki/test_development.py::test_certificate_from_untrusted_ca_is_rejected`
- `tests/pki/test_development.py::test_private_key_export_requires_encryption_and_owner_only_permissions`
- `tests/pki/test_development.py::test_private_key_export_does_not_follow_symbolic_links`
- `tests/pki/test_development.py::test_inspection_projection_is_json_serializable_and_secret_free`
- `tests/pki/test_development.py::test_leaf_validity_cannot_outlive_ca`

## Not yet implemented

The following remain specified but should not yet be represented as implemented evidence:

- caller/action authorization policy;
- active/observe/demo/test execution adapters;
- deterministic release policy engine;
- signing authorization and Cosign integration;
- independent signature verification;
- audit/provenance persistence;
- Syft/Trivy evidence adapters;
- CI security gates;
- AI advisory layer and deterministic fallback.
