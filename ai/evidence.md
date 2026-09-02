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

Local verification command:

```bash
pytest
```

Expected evidence for this increment: 7 passing tests.

## Not yet implemented

The following remain specified but should not yet be represented as implemented evidence:

- development PKI lifecycle and trust validation;
- deterministic release policy engine;
- signing authorization and Cosign integration;
- independent signature verification;
- audit/provenance records;
- Syft/Trivy evidence adapters;
- CI security gates;
- AI advisory layer and deterministic fallback.
