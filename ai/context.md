# AI Project Context

This directory contains project-local context for evidence-driven, agent-assisted engineering.

## Operating principle

Specification comes before substantive implementation.

Agents should use `ai/spec.md` as the product requirements source and the adopted `JonCunninghamDev/engineering-platform` release as the shared engineering-policy source.

## Authority order

For this repository:

1. Explicit human instructions for the active task.
2. Product-specific requirements in `ai/spec.md`.
3. Recorded product decisions in `ai/decisions.md`.
4. Local repository instructions and accepted implementation evidence.
5. Shared engineering-platform guidance for reusable engineering mechanics.

If a local product requirement conflicts with shared engineering guidance, do not silently choose one. Record the conflict and resolve it explicitly.

## Current project goal

Build a portfolio-grade Product Security Automation Platform demonstrating:

- Python software engineering;
- PKI fundamentals;
- artifact signing and verification;
- secure software supply-chain controls;
- SSDLC / DevSecOps automation;
- deterministic security policy;
- auditability and provenance;
- controlled, advisory AI integration.

## Engineering platform adoption

Initial verified platform release:

- repository: `JonCunninghamDev/engineering-platform`
- tag: `v0.1.0`
- commit: `1b09e08b2f6a771bc6b8e0c5359dfb2b8a5b71db`

Before implementation, agents should verify that the declared release remains valid rather than assuming this file is current forever.

## Evidence standard

Claims in README, resume material, demos, or interviews should be supported by code, tests, CI output, generated evidence, or documented decisions in this repository.

Do not claim production scale, security certification, employer-specific knowledge, or security expertise beyond what the project actually demonstrates.
