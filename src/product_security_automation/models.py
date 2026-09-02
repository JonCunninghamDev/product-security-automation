"""Core domain models shared across deterministic security boundaries."""

from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, field_validator


class DigestAlgorithm(StrEnum):
    """Supported artifact digest algorithms."""

    SHA256 = "sha256"


class ReasonCode(StrEnum):
    """Stable machine-readable security decision reasons."""

    ARTIFACT_DIGEST_MATCH = "ARTIFACT_DIGEST_MATCH"
    ARTIFACT_DIGEST_MISMATCH = "ARTIFACT_DIGEST_MISMATCH"
    REQUIRED_EVIDENCE_MISSING = "REQUIRED_EVIDENCE_MISSING"
    VULNERABILITY_THRESHOLD_EXCEEDED = "VULNERABILITY_THRESHOLD_EXCEEDED"
    CERTIFICATE_UNTRUSTED = "CERTIFICATE_UNTRUSTED"
    CERTIFICATE_EXPIRED = "CERTIFICATE_EXPIRED"
    SIGNATURE_INVALID = "SIGNATURE_INVALID"
    POLICY_PASS = "POLICY_PASS"


class ArtifactIdentity(BaseModel):
    """Immutable identity for one exact artifact byte sequence."""

    model_config = ConfigDict(frozen=True)

    name: str = Field(min_length=1, max_length=255)
    size_bytes: int = Field(ge=0)
    digest_algorithm: DigestAlgorithm = DigestAlgorithm.SHA256
    sha256: str = Field(min_length=64, max_length=64)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        # Keep identity portable and prevent callers from smuggling a path into
        # a human-readable artifact name.
        if Path(value).name != value:
            raise ValueError("artifact name must be a basename, not a path")
        return value

    @field_validator("sha256")
    @classmethod
    def validate_sha256(cls, value: str) -> str:
        normalized = value.lower()
        if any(character not in "0123456789abcdef" for character in normalized):
            raise ValueError("sha256 must contain only hexadecimal characters")
        return normalized
