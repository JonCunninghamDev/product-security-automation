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
