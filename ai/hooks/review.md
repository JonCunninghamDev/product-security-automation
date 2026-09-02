# Review Hook

Use this checklist before treating a change as complete.

1. Map the implementation back to specific requirements in `ai/spec.md`.
2. Confirm acceptance evidence exists and is reproducible.
3. Confirm tests cover the important security invariants and failure paths, not only the happy path.
4. Confirm secrets, private keys, credentials, and sensitive values are absent from source and generated evidence.
5. Confirm deterministic policy remains authoritative for security decisions.
6. Confirm AI functionality is advisory, permission-bounded, and non-critical to correct security behavior.
7. Confirm audit/provenance output explains why the decision occurred without exposing secret material.
8. Confirm new architecture or security decisions are recorded in `ai/decisions.md` when appropriate.
9. Confirm README/demo claims do not exceed what the repository evidence proves.
10. Confirm shared engineering mechanics remain consistent with the adopted engineering-platform release or document an explicit exception.

A change is complete only when the code, evidence, and documentation agree.
