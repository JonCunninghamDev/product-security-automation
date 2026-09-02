# Product Security Automation Platform — Specification

Status: Draft v0.2  
Owner: Jon Cunningham  
Purpose: Portfolio-grade product security, PKI, SSDLC, automation, system integration, and controlled AI demonstration

## 1. Purpose

Build a small, production-minded Product Cyber automation platform that demonstrates how engineering and product-delivery workflows can safely consume centralized security capabilities.

The platform centers on software engineering around security services: artifact identity, deterministic authorization, PKI-aware integration, controlled signing, independent verification, auditability, failure handling, and advisory AI.

The project should be understandable in a short demo while still showing evidence of sound engineering judgment. It is intentionally employer-neutral and must not imitate or claim knowledge of any specific employer's proprietary architecture, certificate hierarchy, manufacturing process, or internal integrations.

## 2. Portfolio objective

The repository should provide concrete evidence that the author can:

- build reliable Python services and automation;
- integrate engineering systems with centralized security capabilities;
- learn and correctly apply Product Security and PKI concepts without claiming to be a production PKI architect;
- integrate security controls into an SSDLC and CI/CD lifecycle;
- design deterministic authorization gates around artifact integrity and trust;
- separate privileged security operations from normal application and AI boundaries;
- use observe/demo/test modes to introduce higher-risk integrations safely;
- produce actionable, auditable failure evidence for engineers operating the service;
- use AI as an advisory troubleshooting tool without placing it in the authorization or signing path;
- work from requirements, tests, architectural decisions, and documented evidence rather than ad hoc implementation.

## 3. Shared engineering platform

This repository adopts the shared engineering standards and agent operating model defined in `JonCunninghamDev/engineering-platform`.

Before implementation work, an agent must verify the published platform release and use it as the source of truth for shared engineering mechanics. Product-specific architecture, acceptance criteria, threat model, security boundaries, demo requirements, and explicit exceptions remain authoritative in this repository.

Initial adopted published platform release:

- tag: `v0.1.0`
- release commit: `1b09e08b2f6a771bc6b8e0c5359dfb2b8a5b71db`

The project also evaluates the proposed Execution Modes Standard from commit `e95e7e0f65bff7ba20aeca4b88182700c0cc2222`. That proposal is not part of published `v0.1.0` and must not be represented as released platform steering.

The project must remain independently understandable and testable even if the shared engineering-platform repository is unavailable.

## 4. Working rule: specification before implementation

No substantive feature implementation should begin until the relevant behavior is represented in this specification or an explicitly linked architectural decision.

Changes to product behavior should update the specification first or in the same pull request as the implementation.

## 5. Evidence-driven development

Every major capability should have evidence that maps back to a requirement. Evidence may include automated tests, demo scenarios, architectural/security decisions, generated audit/provenance output, CI evidence, and authoritative external references where relevant.

A feature is not considered complete merely because code exists.

## 6. Product Cyber service model

The platform is modeled as a shared Product Cyber service consumed by multiple kinds of engineering workflows. These are generic portfolio abstractions, not representations of a particular company's systems.

Initial caller contexts:

- `engineering-ci` — an automated product build/release pipeline;
- `release-pipeline` — a software release workflow requesting security evaluation/signing;
- `factory` — a simulated manufacturing/provisioning caller used only to demonstrate a distinct authorization context;
- `operator` — a Product Cyber engineer investigating or recovering a workflow.

Initial artifact types may include:

- firmware image;
- software binary/module;
- installer/package;
- generic release artifact.

A caller context is security-relevant input. Different callers may have different permissions, but caller type alone never authorizes a privileged operation.

## 7. Core user stories

### 7.1 Engineering workflow

A product engineering workflow produces an artifact and submits it to the Product Cyber service.

The platform should:

1. identify the caller and artifact context;
2. calculate immutable artifact identity;
3. collect or generate relevant security evidence;
4. evaluate deterministic security policy and authorization;
5. represent any permitted privileged operation as a planned action bound to the exact artifact digest;
6. execute or suppress the action according to execution mode;
7. independently verify the resulting security state;
8. store an auditable record of the decision, evidence, caller, and action;
9. expose a human-readable result explaining why the workflow passed or failed;
10. optionally use an AI assistant to summarize findings and suggest remediation without allowing AI to approve, sign, issue/revoke certificates, or alter policy.

### 7.2 Product Cyber engineer / operator

A Product Cyber engineer needs to understand and safely resolve a failed integration or signing workflow.

The platform should provide enough structured evidence to answer:

- Which caller and product/artifact requested the operation?
- What exact artifact digest was evaluated?
- Which deterministic control passed or failed?
- Was a privileged action planned, suppressed, attempted, or rejected?
- What certificate/signing identity was involved, without exposing secret material?
- What should the engineer investigate next?

AI may turn this evidence into concise troubleshooting guidance, but deterministic evidence remains authoritative.

## 8. Initial capabilities

### 8.1 Artifact identity and product context

The system must calculate a cryptographic digest for submitted artifacts and use that digest as immutable identity through the workflow.

Artifact requests should eventually carry generic product context such as artifact type, product-family identifier, and caller context. Product metadata is untrusted and must not influence AI as instructions.

Acceptance evidence:

- deterministic hash tests;
- tampered artifact produces a different digest;
- verification rejects changed content;
- caller/artifact context uses explicit typed models.

### 8.2 PKI-aware integration fundamentals

The system must demonstrate enough PKI lifecycle behavior for a software engineer integrating with a certificate/signing service:

- development CA creation;
- signer/service certificate issuance;
- certificate-chain validation;
- certificate expiration handling;
- trust-store behavior;
- documented invalidation/revocation strategy;
- safe handling of private key material.

The objective is correct integration with PKI concepts, not production CA administration or enterprise HSM design.

Private keys must never be committed.

Acceptance evidence:

- valid chain test;
- expired certificate rejection;
- untrusted issuer rejection;
- documented key-handling model;
- reproducible local setup;
- tests prove private signing operations remain behind a privileged boundary.

### 8.3 Privileged signing and independent verification

The system must support signing a sample product artifact and independently verifying it before it is considered releasable.

Signing authorization must require a current passing deterministic evaluation for the exact artifact identity and an authorized caller/action combination.

The signing component must be isolated from AI functionality.

Acceptance evidence:

- valid artifact verifies successfully;
- altered artifact fails verification;
- unauthorized caller/signing attempt is rejected;
- failed evaluation cannot plan signing;
- audit record identifies caller, signer/key identity metadata, and artifact digest without secret material.

### 8.4 SSDLC and system integration

GitHub Actions should demonstrate a realistic engineering consumer of the Product Cyber service.

Initial gates should include, where practical:

- automated tests;
- dependency/vulnerability scanning;
- secret scanning;
- static analysis;
- SBOM generation;
- artifact integrity/signature verification;
- deterministic policy gate preventing release when required checks fail.

The integration should expose structured failure information suitable for an engineer to troubleshoot rather than only raw terminal prose.

### 8.5 Deterministic policy and authorization

Release and privileged-operation decisions must be deterministic and machine-readable. AI output must never determine authorization.

Policy inputs may include required evidence, artifact identity, caller context, requested action, certificate/signature state, provenance fields, and vulnerability thresholds.

Acceptance evidence:

- policy unit tests;
- explicit pass/fail reasons;
- stable behavior for identical inputs;
- unauthorized caller/action combinations fail closed.

### 8.6 Audit, observability, and recovery evidence

Every evaluation must produce evidence sufficient to reconstruct why a decision occurred.

The record should include artifact digest, generic product context, caller context, evaluation timestamp/ID, policy version, checks/results, planned action, execution mode, whether a side effect was executed or suppressed, signing/verification identity metadata, and final deterministic decision.

The design should make failure states useful for incident response and integration troubleshooting. Audit records must not contain private keys, credentials, or tokens.

### 8.7 Advisory AI for Product Cyber operations

The AI assistant may consume a sanitized, read-only evidence projection to provide:

- concise explanations of failed controls;
- remediation/investigation suggestions;
- certificate/signature state summaries;
- release-readiness summaries;
- operator-oriented troubleshooting guidance.

AI cannot approve releases, alter policy, sign artifacts, issue/revoke certificates, modify authoritative audit history, access private keys, or cause an execution-mode transition.

The system must remain correct when AI is unavailable.

## 9. Execution modes

The project supports the architecture defined in `ai/execution-modes.md`:

`input -> deterministic decision -> DecisionResult + PlannedAction[] -> execution adapter`

For higher-risk integrations the preferred progression is:

`test -> demo -> observe -> active`

Observe mode is especially important for demonstrating how a Product Cyber engineer can validate a new integration against realistic inputs while suppressing consequential side effects such as signing.

## 10. Threat model and trust boundaries

The implementation must explicitly model at least:

- artifact tampering after build;
- unauthorized caller or signing attempt;
- leaked/mishandled signing keys;
- untrusted or expired certificates;
- malformed/untrusted product metadata;
- CI credential exposure;
- dependency compromise;
- forged/altered audit data;
- mode confusion causing unintended side effects;
- prompt injection through artifact/product metadata;
- AI hallucination producing unsafe remediation advice.

## 11. Architecture constraints

Preferred implementation stack:

- Python 3.x;
- FastAPI where an HTTP/integration boundary adds demo value;
- Pydantic for explicit request, policy, action, and evidence models;
- pytest;
- GitHub Actions;
- containerized local execution where useful;
- established cryptographic/signing tooling rather than custom algorithms.

AWS may be represented through optional adapters. KMS is a natural production-oriented signing/key-management path, but the local demo must be reproducible without AWS.

Do not implement custom cryptographic primitives.

## 12. Demo requirements

A reviewer should be able to understand the project in approximately three minutes.

The primary demo should tell the story of an engineering team consuming a shared Product Cyber service:

1. `engineering-ci` submits a simulated firmware or software artifact;
2. immutable artifact identity and security evidence are generated;
3. deterministic policy/authorization produces a decision and planned action;
4. signing and independent verification succeed on the happy path;
5. an auditable operator-friendly record is produced;
6. a tampered or unauthorized request is rejected;
7. observe mode shows what would happen without performing the signing side effect;
8. advisory AI explains a failure and suggests investigation steps;
9. AI is visibly unable to override the decision or invoke signing.

At least one failure scenario should resemble an operational integration problem such as expired/untrusted certificate, artifact mismatch, missing evidence, or unauthorized caller.

## 13. Initial non-goals

The first release will not attempt to provide:

- production CA operations;
- enterprise-scale HSM orchestration;
- a full vulnerability-management platform;
- endpoint/network monitoring;
- a manufacturing-system simulator;
- proprietary employer workflows, architecture, product names, certificate hierarchy, or integrations;
- a generic chatbot;
- autonomous AI authorization;
- custom cryptography;
- a large frontend unless it materially improves the demo.

## 14. Definition of done for first portfolio release

The first portfolio release is complete when:

- the primary engineering-consumer happy path works locally;
- caller/product/artifact context is explicitly modeled;
- tampered artifact is rejected;
- unauthorized signing is rejected;
- PKI trust/expiration behavior has automated tests;
- signing and independent verification work;
- observe mode suppresses signing while preserving the same deterministic decision/planned action;
- CI runs meaningful tests/security checks;
- an SBOM or equivalent supply-chain artifact is produced;
- decisions produce human- and machine-readable reasons;
- audit evidence supports operator troubleshooting without secrets;
- AI is demonstrably advisory with deterministic fallback;
- threat model and architecture are documented;
- README includes architecture, trust boundaries, setup, demo, and evidence links.

## 15. Spec evolution

When a design choice is materially debatable, security-sensitive, or reusable, record it in `ai/decisions.md`.

When implementation reveals a reusable engineering need rather than a product-specific need, propose it upstream to `JonCunninghamDev/engineering-platform` rather than embedding a one-off shared convention here.
