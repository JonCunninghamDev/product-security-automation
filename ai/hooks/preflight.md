# Preflight Hook

Run this checklist before substantive implementation work.

1. Read `ai/spec.md` and identify the requirement(s) being changed.
2. Read `ai/decisions.md` for relevant accepted decisions.
3. Verify the adopted `JonCunninghamDev/engineering-platform` release and read the shared guidance relevant to the task.
4. Confirm the change does not weaken a documented trust boundary or move AI into an authorization path.
5. Identify the evidence that will prove completion: tests, demo output, audit/provenance evidence, CI, or a decision record.
6. If the requested behavior is absent from the spec, update the spec before or with implementation.
7. If the task exposes a reusable engineering-platform concern, record it for upstream treatment rather than creating an unexplained local convention.
8. Do not introduce credentials, private keys, tokens, or secret values into the repository.

A task is ready to implement only when its expected behavior and completion evidence are clear.
