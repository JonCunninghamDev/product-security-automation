import pytest
from pydantic import ValidationError

from product_security_automation.models import ArtifactIdentity


def test_artifact_identity_is_immutable() -> None:
    identity = ArtifactIdentity(name="release.bin", size_bytes=3, sha256="a" * 64)

    with pytest.raises(ValidationError):
        identity.sha256 = "b" * 64


def test_artifact_identity_rejects_non_hex_digest() -> None:
    with pytest.raises(ValidationError):
        ArtifactIdentity(name="release.bin", size_bytes=3, sha256="z" * 64)


def test_artifact_identity_rejects_path_as_name() -> None:
    with pytest.raises(ValidationError):
        ArtifactIdentity(name="nested/release.bin", size_bytes=3, sha256="a" * 64)
