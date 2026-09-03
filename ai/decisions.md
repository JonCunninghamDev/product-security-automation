# Architecture and Security Decisions

Use this file for concise records of decisions that materially affect architecture, security boundaries, trust, demo behavior, or reusable engineering patterns.

Each decision should include:

- date;
- status: proposed / accepted / superseded;
- decision;
- rationale;
- alternatives considered;
- evidence or follow-up required.

---

## D-001 — AI remains outside the security authorization path

Date: 2026-09-03
Status: Accepted

### Decision

AI may explain security evidence and recommend remediation, but deterministic code and policy own release approval, certificate operations, signing, verification, and audit history.

### Rationale

Security-critical decisions must remain reproducible, testable, and independent of model availability or model output quality.

### Alternatives considered

- AI directly deciding release approval: rejected because model output is probabilistic and difficult to make authoritative or reproducible.
- AI invoking signing tools: rejected because it expands the trust boundary unnecessarily.

### Evidence required

- tests proving identical security decisions with AI enabled and unavailable;
- explicit tool-permission boundary;
- demo showing AI cannot override a failed deterministic gate.

---

## D-002 — Use established cryptographic tooling; do not implement custom crypto

Date: 2026-09-03  
Status: Accepted

### Decision

Use established cryptographic libraries and/or standard signing tools for PKI and artifact signing operations. The project will not implement cryptographic algorithms itself.

### Rationale

The project exists to demonstrate secure system integration and lifecycle controls, not cryptographic algorithm design. Custom crypto would add risk without adding meaningful portfolio evidence.

### Evidence required

- dependency/tool selection documented when implementation begins;
- tests for signing, verification, trust failure, expiration, and tampering.

---

## D-003 — Local-first demo with optional cloud path

Date: 2026-09-03  
Status: Accepted

### Decision

The core demo must run locally without paid cloud infrastructure or reviewer credentials. AWS-backed components may be added as optional production-oriented implementations where they add meaningful evidence.

### Rationale

A portfolio reviewer should be able to reproduce the core behavior quickly. Cloud-specific implementation should demonstrate architecture rather than become a barrier to evaluation.

### Evidence required

- documented local setup;
- one-command or concise demo path;
- optional cloud architecture clearly separated from required local behavior.

---

## D-004 — Bind signing authorization to an exact artifact digest

Date: 2026-09-03  
Status: Accepted

### Decision

A signing request is authorized only when a current deterministic policy evaluation has passed for the exact SHA-256 digest being signed.

The signer must re-check this binding and fail closed rather than trusting a caller-provided statement that an artifact was approved.

### Rationale

A generic `approved=true` state can be reused accidentally or maliciously after an artifact changes. Binding approval to immutable artifact identity makes post-evaluation tampering observable and prevents a passing result from authorizing a different artifact.

### Alternatives considered

- approve by filename/version only: rejected because mutable identifiers are insufficient evidence of content identity.
- allow the API layer to authorize signing without signer-side validation: rejected because it weakens the signing trust boundary.

### Evidence required

- passing artifact can be signed;
- mutation after evaluation causes signing/verification failure;
- signing request without a matching passing evaluation is rejected.

---

## D-005 — Use Python `cryptography` for the development PKI layer

Date: 2026-09-03  
Status: Accepted for v1

### Decision

Use the established Python `cryptography` package to create and inspect the local development CA and X.509 certificates used to demonstrate issuance, chain/trust behavior, and expiration.

### Rationale

The project needs visible, testable PKI lifecycle behavior in Python without implementing cryptographic primitives. `cryptography` provides established X.509 APIs while keeping the learning/demo layer understandable to a Python reviewer.

### Alternatives considered

- shelling out entirely to OpenSSL: viable but less useful for demonstrating typed Python integration and automated lifecycle tests.
- building certificate primitives ourselves: rejected by D-002.
- running a production-style CA such as Vault or step-ca immediately: deferred because it adds operational surface before the basic trust model is proven.

### Evidence required

- ephemeral development CA creation;
- certificate issuance test;
- valid trust-chain test;
- expired/untrusted certificate rejection tests;
- private key material excluded from Git.

Reference: https://cryptography.io/

---

## D-006 — Use Sigstore Cosign for artifact/blob signing and verification

Date: 2026-09-03  
Status: Accepted for v1

### Decision

Use Sigstore Cosign as the artifact signing and independent verification integration rather than inventing a project-specific signature format.

The local demo will use a reproducible local/self-managed-key path where necessary. Identity-backed/keyless or KMS-backed signing may be demonstrated separately in CI/cloud extensions.

### Rationale

Cosign is purpose-built for software artifact signing and verification, supports blobs/files as well as container images, and supports verification bundles and multiple key-management models. That makes it a stronger software-supply-chain demonstration than a bespoke signature wrapper.

### Alternatives considered

- directly signing artifact bytes through `cryptography`: technically valid but would demonstrate less familiarity with modern software supply-chain tooling.
- GPG-based signing: mature, but less aligned to current artifact/provenance workflows.
- keyless-only signing for the core demo: deferred because the local demo must not require reviewer identity/provider access.

### Evidence required

- valid blob signature verifies;
- tampered blob fails verification;
- signature/bundle metadata is retained as evidence;
- signing adapter cannot be reached from the AI assistant;
- optional identity/KMS extension is isolated from the local-first path.

References:

- https://docs.sigstore.dev/cosign/signing/signing_with_blobs/
- https://docs.sigstore.dev/cosign/verifying/verify/

---

## D-007 — Generate SBOMs with Syft and scan normalized evidence with Trivy

Date: 2026-09-03  
Status: Accepted for v1

### Decision

Use Syft to generate a machine-readable SBOM and Trivy to provide vulnerability evidence for the deterministic policy engine.

The policy engine will consume normalized fields produced by an adapter rather than depend on parsing human-oriented terminal output.

### Rationale

This separates software inventory from policy and keeps the security gate replaceable/testable. Syft supports standard SBOM output such as SPDX and CycloneDX, while Trivy can scan SBOM inputs for vulnerability evidence.

### Alternatives considered

- custom dependency inventory: rejected because it duplicates mature tooling and weakens supply-chain evidence.
- Trivy alone for both generation and scanning: possible, but using Syft explicitly demonstrates an independent SBOM artifact that can be inspected outside the scanner.
- scanner console text as policy input: rejected because human-readable output is a fragile machine interface.

### Evidence required

- generated SBOM committed only as demo/build evidence where appropriate, not as a hand-maintained source of truth;
- adapter tests normalize scanner output into stable policy inputs;
- policy threshold tests run independently from the scanner executable;
- CI demonstrates a blocked policy scenario.

References:

- https://github.com/anchore/syft
- https://trivy.dev/docs/dev/target/sbom/

---

## D-008 — Bound the development PKI to ephemeral direct-chain trust

Date: 2026-09-03
Status: Accepted for v1

### Decision

The development PKI uses one ephemeral, self-signed root CA and leaf certificates
issued directly by that root. Trust anchors are configured explicitly and matched by
certificate fingerprint. Removing the root from the trust set invalidates all leaves;
rotation creates a new ephemeral root and new leaves.

Private keys remain in process memory by default. An explicit local export must be
encrypted and owner-readable only. CRLs, OCSP, intermediate CAs, and persistent CA
key custody are outside this bounded increment.

### Rationale

This scope visibly demonstrates creation, issuance, inspection, signature validation,
trust, expiry, and key-handling boundaries without implying that a small portfolio
service is a production CA. Whole-root invalidation is deterministic and sufficient
for short-lived development identities.

### Alternatives considered

- CRL or OCSP support: deferred until persistent identity and revocation services are
  justified by a later product requirement.
- persistent unencrypted development keys: rejected because it creates avoidable
  secret-handling risk and weakens the demo boundary.
- intermediate CA hierarchy: deferred because the initial lifecycle requires only a
  direct chain.

### Evidence required

- runtime-generated CA and leaf certificates;
- signer and service certificate metadata tests;
- trusted-chain success and expired/untrusted rejection tests;
- encrypted key-export and filesystem-permission tests;
- repository secret/key scan before review.
