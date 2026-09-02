# Product Security Automation Platform — Specification

Status: Draft v0.1  
Owner: Jon Cunningham  
Purpose: Portfolio-grade product security, PKI, SSDLC, automation, and controlled AI demonstration

## 1. Purpose

Build a small, production-minded product security automation platform that demonstrates how software engineering, automation, secure delivery, PKI, artifact integrity, and controlled AI can work together in a modern SSDLC.

The project should be understandable in a short demo while still showing evidence of sound engineering judgment. It is not intended to imitate a specific employer's proprietary systems or processes.

## 2. Portfolio objective

The repository should provide concrete evidence that the author can:

- build reliable Python services and automation;
- learn and apply product-security and PKI concepts;
- integrate security controls into a software delivery lifecycle;
- design deterministic security gates around artifact integrity and trust;
- use AI as an advisory tool without placing it in the authorization or signing path;
- produce auditable evidence showing why a release passed or failed;
- work from requirements, tests, architectural decisions, and documented evidence rather than ad hoc implementation.

## 3. Shared engineering platform

This repository adopts the shared engineering standards and agent operating model defined in `JonCunninghamDev/engineering-platform`.

Before implementation work, an agent must:

1. Verify access to the engineering-platform repository.
2. Read its README and VERSION.
3. Verify the latest published non-draft, non-prerelease release.
4. Confirm that the release tag matches VERSION.
5. Use the verified release as the source of truth for shared engineering mechanics including Git workflow, testing, CI/CD, security standards, observability, dependency management, delivery, and agent operating conventions.
6. Treat this repository as authoritative for product-specific architecture, acceptance criteria, threat model, security boundaries, demo requirements, and explicit exceptions.

Initial adopted platform release:

- tag: `v0.1.0`
- release commit: `1b09e08b2f6a771bc6b8e0c5359dfb2b8a5b71db`

The project must remain independently understandable and testable even if the shared engineering-platform repository is unavailable.

## 4. Working rule: specification before implementation

No substantive feature implementation should begin until the relevant behavior is represented in this specification or an explicitly linked architectural decision.

Changes to product behavior should update the specification first or in the same pull request as the implementation.

Implementation details that do not affect requirements, trust boundaries, acceptance criteria, or externally visible behavior do not need to be encoded in this file.

## 5. Evidence-driven development

Every major capability should have evidence that maps back to a requirement. Evidence may include:

- automated tests;
- a demo scenario;
- an architecture or security decision record;
- generated audit/provenance output;
- CI evidence;
- an external standard or authoritative reference when relevant.

A feature is not considered complete merely because code exists.

## 6. Core user story

A developer produces a software artifact and submits it to the product security workflow.

The platform should:

1. identify and hash the artifact;
2. collect or generate relevant software-supply-chain metadata;
3. evaluate deterministic security policy;
4. sign an approved artifact using a controlled signing path;
5. verify the resulting signature and trust chain;
6. store an auditable record of the decision and evidence;
7. expose a human-readable result explaining why the artifact passed or failed;
8. optionally use an AI assistant to summarize findings and suggest remediation without allowing the AI to approve, sign, revoke, or alter policy.

## 7. Initial capabilities

### 7.1 Artifact identity and integrity

The system must calculate a cryptographic digest for submitted artifacts and use that digest as the immutable identity of the artifact through the workflow.

Acceptance evidence:

- deterministic hash tests;
- tampered artifact produces a different digest;
- verification rejects an artifact whose content no longer matches its recorded digest.

### 7.2 PKI fundamentals

The system must demonstrate a minimal PKI lifecycle suitable for a local development/demo environment:

- root or development CA creation;
- certificate issuance;
- certificate-chain validation;
- certificate expiration handling;
- a documented revocation or invalidation strategy.

Private keys must never be committed to the repository.

Acceptance evidence:

- valid certificate-chain test;
- expired or untrusted certificate rejection test;
- documented key-handling model;
- reproducible local demo setup.

### 7.3 Artifact signing and verification

The system must support signing a sample artifact and independently verifying the signature before the artifact is considered releasable.

The signing component must be isolated from AI functionality.

Acceptance evidence:

- valid artifact verifies successfully;
- altered artifact fails verification;
- unauthorized signing attempt is rejected;
- audit record identifies signer/key identity and artifact digest without exposing secret material.

### 7.4 SSDLC and CI security gates

GitHub Actions should demonstrate security controls integrated into delivery.

Initial gates should include, where practical:

- automated tests;
- dependency or vulnerability scanning;
- secret scanning;
- static analysis;
- SBOM generation;
- artifact integrity/signature verification;
- policy gate preventing release when required checks fail.

The CI pipeline must include at least one intentionally failing demo scenario proving that unsafe or invalid artifacts are blocked.

### 7.5 Policy evaluation

Release decisions must be deterministic and machine-readable.

AI output must never determine whether an artifact is approved.

Initial policy examples may include:

- required checks present;
- artifact digest matches recorded digest;
- certificate/signature valid;
- no disallowed severity threshold exceeded;
- required provenance fields present.

Acceptance evidence:

- policy unit tests;
- explicit pass/fail reasons;
- stable behavior for identical inputs.

### 7.6 Audit and provenance

Every evaluation must produce an audit record sufficient to reconstruct why a decision occurred.

The record should include at minimum:

- artifact digest;
- evaluation timestamp;
- policy version;
- checks performed;
- check results;
- signing/verification identity metadata;
- final deterministic decision;
- correlation or evaluation ID.

Audit records must not contain private keys, credentials, tokens, or other secret values.

### 7.7 AI security assistant

The project may include an AI assistant that reads security evidence and produces:

- concise explanations of failed checks;
- remediation suggestions;
- summaries of certificate/signature state;
- release-readiness summaries.

AI must be advisory only.

The AI component must not be able to:

- approve releases;
- alter security policy;
- sign artifacts;
- issue or revoke certificates;
- modify audit history;
- access private signing keys.

The system must continue to make correct security decisions when the AI provider is unavailable.

Acceptance evidence:

- deterministic fallback behavior;
- tests proving the security decision is independent of AI output;
- tool permissions documented explicitly;
- AI-generated text labeled as advisory.

## 8. Threat model and trust boundaries

The first implementation must explicitly model at least these threats:

- artifact tampering after build;
- unauthorized signing attempts;
- leaked or mishandled signing keys;
- untrusted or expired certificates;
- malicious or malformed input;
- CI credential exposure;
- dependency compromise;
- forged or altered audit data;
- prompt injection or malicious artifact metadata influencing the AI assistant;
- AI hallucination producing unsafe remediation advice.

Trust boundaries must be documented before the signing workflow is considered complete.

## 9. Architecture constraints

Initial preferred implementation stack:

- Python 3.x;
- FastAPI for a small service/API where an HTTP boundary adds demo value;
- Pydantic for explicit request, policy, and evidence models;
- pytest for automated tests;
- GitHub Actions for SSDLC automation;
- containerized local execution where useful;
- cryptographic libraries or established signing tooling rather than custom cryptographic algorithms.

AWS may be represented through local abstractions or optional deployable infrastructure. A costly always-on cloud deployment is not required for the first portfolio release.

If AWS is added, prefer managed primitives and least-privilege IAM. AWS KMS is a natural optional production-grade signing/key-management path, but the local demo must remain reproducible without requiring reviewers to possess an AWS account.

Do not implement custom cryptographic primitives.

## 10. Security principles

The design must follow these principles:

- deterministic security decisions;
- least privilege;
- separation of duties;
- immutable artifact identity;
- secrets never committed to source control;
- explicit trust boundaries;
- fail closed for signing and release authorization;
- auditable decisions;
- AI outside the critical authorization path;
- reproducible local tests and demo behavior.

## 11. Demo requirements

A reviewer should be able to understand the project in approximately three minutes.

The primary demo should show:

1. a valid sample artifact entering the workflow;
2. security evidence being generated;
3. deterministic policy evaluation;
4. signing and verification;
5. a clear audit record;
6. an AI-generated advisory explanation;
7. a tampered or policy-violating artifact being rejected;
8. the AI being unable to override that rejection.

The README must eventually include a concise demo command or script.

## 12. Initial non-goals

The first release will not attempt to provide:

- production certificate authority operations;
- enterprise-scale HSM orchestration;
- a full vulnerability-management platform;
- endpoint or network security monitoring;
- proprietary Honeywell workflows, architecture, or integrations;
- a generic chatbot;
- autonomous AI authorization;
- a custom cryptographic implementation;
- a large frontend application unless a minimal UI materially improves the demo.

## 13. Definition of done for the first portfolio release

The first portfolio release is complete when:

- the primary happy-path demo works locally from documented commands;
- a tampered artifact is deterministically rejected;
- an unauthorized signing path is deterministically rejected;
- PKI trust/expiration behavior has automated tests;
- signing and independent verification work;
- CI runs tests and meaningful security checks;
- an SBOM or equivalent software-supply-chain artifact is produced;
- policy decisions produce human-readable and machine-readable reasons;
- audit evidence is generated without secrets;
- the AI assistant is demonstrably advisory and has a deterministic fallback;
- threat model and architecture are documented;
- automated tests cover the major security invariants;
- README includes architecture, trust boundaries, setup, demo, and evidence links.

## 14. Spec evolution

This document is expected to evolve as implementation produces new evidence.

When a design choice is materially debatable, security-sensitive, or reusable, record the decision in `ai/decisions.md` before silently baking it into implementation.

When implementation reveals a reusable engineering need rather than a product-specific need, propose the improvement upstream to `JonCunninghamDev/engineering-platform` instead of embedding a one-off shared convention here.
