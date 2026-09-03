"""Artifact identity and integrity primitives."""

from __future__ import annotations

from hashlib import sha256
from pathlib import Path

from .models import ArtifactIdentity, ReasonCode

_CHUNK_SIZE = 1024 * 1024


class ArtifactDigestMismatch(ValueError):
    """Raised when artifact bytes no longer match an approved identity."""

    reason_code = ReasonCode.ARTIFACT_DIGEST_MISMATCH


def hash_artifact(path: str | Path) -> ArtifactIdentity:
    """Calculate immutable SHA-256 identity from the artifact's bytes."""

    artifact_path = Path(path)
    if not artifact_path.is_file():
        raise FileNotFoundError(f"artifact does not exist or is not a file: {artifact_path}")

    digest = sha256()
    size_bytes = 0

    with artifact_path.open("rb") as artifact:
        while chunk := artifact.read(_CHUNK_SIZE):
            digest.update(chunk)
            size_bytes += len(chunk)

    return ArtifactIdentity(
        name=artifact_path.name,
        size_bytes=size_bytes,
        sha256=digest.hexdigest(),
    )


def verify_artifact(path: str | Path, expected: ArtifactIdentity) -> ReasonCode:
    """Verify that a file still represents the exact approved artifact bytes."""

    actual = hash_artifact(path)
    if actual.sha256 != expected.sha256 or actual.size_bytes != expected.size_bytes:
        raise ArtifactDigestMismatch(
            f"artifact digest mismatch: expected {expected.sha256}, got {actual.sha256}"
        )

    return ReasonCode.ARTIFACT_DIGEST_MATCH
