# Product Security Automation Platform

A small, employer-neutral demonstration of deterministic product-security controls,
PKI, artifact integrity, secure delivery, and advisory-only AI integration.

## Current capability: bounded development PKI

The first implementation increment provides a local-only PKI lifecycle:

- an ephemeral P-256 development CA generated in process memory;
- purpose-specific artifact-signer and service certificates;
- secret-free certificate metadata for audit evidence;
- direct-chain signature, trust-anchor, and validity checks;
- fail-closed expired, not-yet-valid, untrusted, and invalid-chain outcomes;
- explicit encrypted private-key export with owner-only filesystem permissions.

This is a learning and demonstration CA, not a production certificate authority. It
supports one self-signed root and directly issued leaves. The authoritative product
requirements and boundaries are in [`ai/spec.md`](ai/spec.md) and
[`ai/architecture.md`](ai/architecture.md).

## Run the evidence

Use Python 3.11 or newer:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[dev]'
pytest
```

The tests create all keys and certificates at runtime. No private key or fixed secret
is included in the repository.
