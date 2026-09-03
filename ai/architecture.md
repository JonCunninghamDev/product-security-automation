# Product Security Automation Platform — Architecture

Status: Draft v0.2  
Date: 2026-09-03  
Specification: `ai/spec.md`

## 1. Architecture goal

Demonstrate the software-engineering layer around a shared Product Cyber capability: multiple engineering callers submit product artifacts, deterministic controls decide what is permitted, privileged security operations occur behind an isolated boundary, and engineers receive useful evidence when workflows fail.

The project does not simulate a particular employer's internal platform. It uses generic product-security abstractions to demonstrate patterns relevant to Product Cyber engineering and system integration.

Core rule:

> Security decisions and privileged-operation authorization are deterministic, evidence-driven, and bound to an exact artifact identity. AI may explain evidence but cannot change a decision or exercise security authority.

## 2. Logical architecture

```text
 Engineering CI       Release Pipeline       Factory (simulated)
       |                     |                       |
       +---------------------+-----------------------+
                             |
                             v
                  +------------------------+
                  | Product Cyber Service  |
                  | intake + integration   |
                  +-----------+------------+
                              |
                    caller + product context
                    exact artifact identity
                              |
                              v
                  +------------------------+
                  | Evidence Pipeline      |
                  | SBOM / scans / trust   |
                  +-----------+------------+
                              |
                              v
                  +------------------------+
                  | Policy + Authorization |
                  | deterministic          |
                  +-----------+------------+
                              |
                    DecisionResult
                    + PlannedAction[]
                              |
                              v
                  +------------------------+
                  | Execution Adapter      |
                  | active/observe/demo/   |
                  | test                   |
                  +-----------+------------+
                              |
             permitted active | operation
                              v
                  +------------------------+
                  | Privileged Security    |
                  | PKI / Signing Boundary |
                  +-----------+------------+
                              |
                              v
                  +------------------------+
                  | Independent Verify     |
                  +-----------+------------+
                              |
                              v
                  +------------------------+
                  | Audit / Evidence       |
                  | operator-readable      |
                  +-----------+------------+
                              |
                     sanitized read-only
                              v
                  +------------------------+
                  | Advisory AI            |
                  | explain / remediate    |
                  +------------------------+

 Product Cyber Engineer / Operator
        ^               |
        | inspect       | investigate/retry through authorized paths
        +---------------+
```

The operator is not a privileged bypass. Human investigation and recovery still use the same deterministic controls and explicit authorization boundaries.

## 3. Domain context

### Caller contexts

The initial generic caller contexts are:

- `engineering-ci`: automated product build/release integration;
- `release-pipeline`: software release integration;
- `factory`: simulated manufacturing/provisioning integration used to exercise a distinct authorization context;
- `operator`: Product Cyber engineer investigating workflow state.

Caller context is security-relevant evidence, not proof of authorization by itself.

### Product artifacts

The platform should remain neutral across product types. Demo fixtures may represent firmware, software modules/binaries, installers/packages, or generic release artifacts.

A future `ProductArtifact` request model should compose immutable `ArtifactIdentity` with generic context such as `artifact_type`, `product_family`, and `caller_context`. Product names remain fictional.

## 4. Trust boundaries

### TB-1 — Untrusted integration boundary

Artifacts, caller-supplied metadata, product-family identifiers, filenames, manifests, SBOM input, and descriptions are untrusted.

Controls include typed/bounded models, SHA-256 artifact identity, no shell interpolation, authenticated caller identity when an HTTP boundary is introduced, and strict separation between metadata and AI instructions.

### TB-2 — Evidence boundary

Deterministic tools generate evidence that is normalized into explicit internal models. Raw output may be retained for evidence, but policy consumes normalized fields.

### TB-3 — Policy and authorization boundary

The policy engine receives immutable artifact identity, normalized evidence, caller context, and requested action. It produces an immutable `DecisionResult` and zero or more `PlannedAction` values.

No AI output is accepted as policy input.

Privileged actions require both a passing decision and an authorized caller/action relationship. A passing security evaluation alone is not sufficient authority to sign.

### TB-4 — Execution-mode boundary

Execution mode changes how planned actions are handled, not how security decisions are calculated.

- `active`: permitted consequential actions may execute;
- `observe`: the real decision/planning path runs, but consequential side effects are suppressed and recorded;
- `demo`: safe adapters execute deterministic named scenarios with narration/evidence;
- `test`: deterministic doubles/assertions prevent unintended external effects.

Mode must be explicit and observable. Mode confusion must fail safely.

### TB-5 — Privileged PKI/signing boundary

The privileged security adapter may act only on a valid planned action generated for a current passing evaluation, authorized caller/action combination, and exact artifact digest.

Private key material is inaccessible to normal application code and AI. The local demo uses ephemeral/development material only.

### TB-6 — Independent verification boundary

A signed artifact is not release-ready until independent verification proves artifact identity, signature validity, trusted signing identity, and applicable certificate validity.

### TB-7 — Audit/operations boundary

Audit evidence records what the system decided, planned, executed/suppressed, and verified. It is designed to support troubleshooting and incident/recovery conversations without exposing credentials or private keys.

An operator may inspect evidence and initiate explicitly authorized retry/recovery workflows, but cannot edit historical decisions into success.

### TB-8 — AI boundary

AI receives a sanitized, read-only evidence projection. It can explain failures and suggest investigation steps. It cannot invoke signing/PKI operations, issue/revoke certificates, alter policy, rewrite audit history, change execution mode, or access credentials/private keys.

## 5. Representative workflows

### Engineering happy path

1. `engineering-ci` submits a fictional product artifact.
2. Intake records caller/product context and computes exact SHA-256 identity.
3. Evidence generation produces normalized security evidence.
4. Policy/authorization returns `PASS` and a signing `PlannedAction` bound to that digest.
5. In `active` mode, the execution adapter presents that authorized plan to the privileged signer.
6. Independent verification validates the result.
7. Audit records caller, artifact, decision, planned/executed action, signer metadata, and verification.
8. Advisory AI produces a short release-readiness explanation from sanitized evidence.

### Observe-mode integration rollout

1. A new engineering integration submits realistic inputs in `observe` mode.
2. The same intake/evidence/policy path runs.
3. The system produces the same decision and planned signing action it would produce in active mode.
4. The execution adapter suppresses the signing side effect.
5. Audit explicitly records `executed=false`, mode=`observe`, and why the action was suppressed.
6. A Product Cyber engineer compares expected behavior before enabling active execution.

This scenario is a primary demonstration of safe integration engineering.

### Tamper path

A previously evaluated artifact changes. Its digest no longer matches the approved identity, so verification/policy fails and no signing plan is authorized.

### Unauthorized caller path

A caller requests a privileged signing action it is not permitted to request. The deterministic authorization layer rejects it, no signing action executes, and the attempt becomes security-relevant audit evidence.

### Expired/untrusted certificate operational path

1. An otherwise valid workflow reaches a certificate/trust check.
2. Deterministic validation returns an explicit reason such as `CERTIFICATE_EXPIRED` or `CERTIFICATE_UNTRUSTED`.
3. Signing/release remains blocked as required by policy.
4. Audit identifies the certificate metadata and failed control without exposing private material.
5. Advisory AI may explain the failure and suggest investigation/renewal/trust-store checks.
6. The operator cannot override the failed deterministic control through AI or audit interfaces.

This is the primary Product Cyber engineer troubleshooting scenario.

## 6. Component model

### `artifact`
Calculates SHA-256, models immutable identity, validates metadata, and prevents digest substitution.

### `integration`
Models caller/product/artifact context and eventually provides API/CLI boundaries for engineering consumers. It translates external requests into typed internal commands without granting authority merely because a caller requested an action.

### `evidence`
Normalizes tests, scanners, SBOM, certificate, and verification results into stable policy inputs.

### `policy`
Owns deterministic release/security rules and reason codes.

### `authorization`
Determines whether a caller may request a particular privileged operation after required policy conditions pass. This remains deterministic and separate from AI.

### `execution`
Consumes `DecisionResult + PlannedAction[]` and dispatches through active/observe/demo/test adapters. Observe mode must preserve planned-action evidence while suppressing consequential side effects.

### `pki`
Provides a local learning/demo trust environment: development CA, signer/service certificate issuance, metadata inspection, trust/expiry validation, and documented invalidation behavior. It is not a production CA.

### `signing`
Enforces exact-digest authorization and calls established signing tooling behind the privileged boundary.

### `verification`
Independently verifies artifact identity, signature, trust, and certificate validity.

### `audit`
Records evaluation, caller/product context, policy, planned action, execution mode/outcome, signer metadata, verification, timestamps, and evidence references without secrets.

### `assistant`
Consumes sanitized evidence only and generates advisory troubleshooting/release-readiness output with deterministic fallback.

## 7. PKI scope for this project

PKI implementation is deliberately bounded to what a software engineer integrating a Product Cyber service should demonstrate:

- understand root/intermediate or signer trust relationships;
- issue a development signer/service certificate using established `cryptography` primitives;
- inspect subject/issuer/serial/validity/key usage metadata;
- validate chain/trust and expiry;
- reject untrusted/expired material;
- keep private keys out of Git and normal logs;
- understand that production keys should live behind managed/HSM-backed services;
- consume PKI outcomes through explicit typed interfaces.

The project does not attempt enterprise CA governance, certificate-policy design, production revocation infrastructure, HSM administration, or cryptographic protocol invention.

Artifact signing remains planned around established tooling such as Sigstore Cosign; a future AWS extension may map privileged signing to KMS.

## 8. Operational evidence model

A useful audit record should evolve toward:

```json
{
  "evaluation_id": "...",
  "caller": "engineering-ci",
  "product_family": "demo-controller",
  "artifact_type": "firmware",
  "artifact": {
    "name": "controller-firmware-2.4.1.bin",
    "sha256": "..."
  },
  "policy_version": "v1",
  "decision": "PASS",
  "planned_actions": ["SIGN_ARTIFACT"],
  "execution": {
    "mode": "observe",
    "executed": false,
    "reason": "side effects suppressed by observe mode"
  },
  "signing_identity": "demo-product-signer",
  "verification": null,
  "created_at": "..."
}
```

This record should answer both security questions and operator questions without requiring a reviewer to infer state from console output.

## 9. API/integration boundary

FastAPI should be introduced when it makes the integration and authorization boundaries easier to demonstrate.

Likely v1 endpoints:

- `POST /evaluations` — submit/reference an artifact with generic caller/product context;
- `GET /evaluations/{id}` — inspect decision/evidence/action state;
- `POST /evaluations/{id}/sign` — request privileged signing, re-validating authorization and exact digest;
- `POST /verify` — independently verify artifact/signature material;
- `GET /evaluations/{id}/advisory` — read-only advisory explanation.

A CLI/demo runner should exercise the same application services so HTTP is not the source of security policy.

## 10. Three-minute demo narrative

The demo should be a conversation piece for software/security engineers rather than a cryptography tutorial.

1. Show a fictional firmware/software artifact submitted by `engineering-ci`.
2. Show its immutable identity and deterministic evidence.
3. Run the workflow in `observe` mode: policy passes and `SIGN_ARTIFACT` is planned, but signing is visibly suppressed.
4. Run the authorized happy path in safe demo mode and show signing + independent verification.
5. Tamper with the artifact and show deterministic rejection.
6. Run an expired/untrusted certificate scenario and show operator-readable evidence.
7. Ask the advisory AI/fallback layer to explain what failed and what an engineer should inspect.
8. Show that AI has no tool/capability to approve or sign.

The desired engineering discussion is about trust boundaries, integration rollout, failure handling, authorization, evidence, and how the design would map to real managed PKI/signing infrastructure.

## 11. Implementation sequence

1. domain models/reason codes and artifact hashing — implemented in current increment;
2. generic `CallerContext`, `ArtifactType`, and `ProductArtifact` context models;
3. development PKI lifecycle and trust/expiry tests;
4. deterministic policy + caller/action authorization;
5. execution adapters, beginning with observe/test behavior;
6. established signing/verification adapter integration;
7. audit/operator evidence records;
8. Syft/Trivy evidence adapters and CI gates;
9. advisory AI + deterministic fallback;
10. three-minute demo/evidence index.

Each increment must leave executable evidence for the invariant it introduces.

## 12. Production-oriented extension path

After the local portfolio release works, an optional AWS path may demonstrate KMS asymmetric signing, least-privilege IAM, S3 object/digest correlation, DynamoDB/immutable-object audit metadata, EventBridge/SQS workflow separation, and Bedrock advisory explanation using the same read-only evidence projection.

The local deterministic interfaces remain unchanged so cloud services are adapters, not sources of product policy.

## 13. Architecture acceptance criteria

Architecture is ready for the next increment when:

- shared Product Cyber service and caller contexts are explicit;
- operator troubleshooting is represented without creating a bypass;
- AI cannot reach signing/authorization;
- signer authorization is bound to caller + passing decision + exact artifact digest;
- execution mode changes side effects, never the decision;
- independent verification remains mandatory after signing;
- PKI scope is clearly integration-focused rather than production-CA imitation;
- audit evidence is useful for security and operational troubleshooting;
- product names/workflows remain fictional and employer-neutral.
