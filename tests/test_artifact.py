from pathlib import Path

import pytest

from product_security_automation.artifact import (
    ArtifactDigestMismatch,
    hash_artifact,
    verify_artifact,
)
from product_security_automation.models import ReasonCode


def test_hash_is_deterministic_for_identical_bytes(tmp_path: Path) -> None:
    artifact = tmp_path / "release.bin"
    artifact.write_bytes(b"trusted-release-payload")

    first = hash_artifact(artifact)
    second = hash_artifact(artifact)

    assert first == second
    assert first.name == "release.bin"
    assert first.size_bytes == len(b"trusted-release-payload")
    assert len(first.sha256) == 64


def test_verification_accepts_unchanged_artifact(tmp_path: Path) -> None:
    artifact = tmp_path / "release.bin"
    artifact.write_bytes(b"trusted-release-payload")
    identity = hash_artifact(artifact)

    result = verify_artifact(artifact, identity)

    assert result is ReasonCode.ARTIFACT_DIGEST_MATCH


def test_tampering_changes_digest_and_is_rejected(tmp_path: Path) -> None:
    artifact = tmp_path / "release.bin"
    artifact.write_bytes(b"trusted-release-payload")
    approved = hash_artifact(artifact)

    artifact.write_bytes(b"tampered-release-payload")
    tampered = hash_artifact(artifact)

    assert tampered.sha256 != approved.sha256
    with pytest.raises(ArtifactDigestMismatch) as error:
        verify_artifact(artifact, approved)

    assert error.value.reason_code is ReasonCode.ARTIFACT_DIGEST_MISMATCH


def test_missing_artifact_fails_closed(tmp_path: Path) -> None:
    missing = tmp_path / "missing.bin"

    with pytest.raises(FileNotFoundError):
        hash_artifact(missing)
