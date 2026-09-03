"""Core domain models shared across deterministic security boundaries."""

from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


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


class ExecutionMode(StrEnum):
    """Supported runtime execution modes."""

    ACTIVE = "active"
    OBSERVE = "observe"
    DEMO = "demo"
    TEST = "test"


class CallerContext(StrEnum):
    """Generic caller contexts for shared Product Cyber integrations."""

    ENGINEERING_CI = "engineering-ci"
    RELEASE_PIPELINE = "release-pipeline"
    FACTORY = "factory"
    OPERATOR = "operator"


class ArtifactType(StrEnum):
    """Generic product artifact categories used by the portfolio demo."""

    FIRMWARE = "firmware"
    SOFTWARE_BINARY = "software-binary"
    INSTALLER = "installer"
    RELEASE_ARTIFACT = "release-artifact"


class Decision(StrEnum):
    """Deterministic security decision."""

    PASS = "PASS"
    FAIL = "FAIL"


class ActionKind(StrEnum):
    """Typed actions that may cross an execution boundary."""

    SIGN_ARTIFACT = "SIGN_ARTIFACT"
    WRITE_AUDIT_RECORD = "WRITE_AUDIT_RECORD"
    GENERATE_ADVISORY = "GENERATE_ADVISORY"


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


class ProductArtifact(BaseModel):
    """Immutable product context composed around an exact artifact identity.

    Product and caller metadata are intentionally generic. They are security-relevant
    inputs to later policy/authorization logic, but they do not grant authority by
    themselves.
    """

    model_config = ConfigDict(frozen=True)

    identity: ArtifactIdentity
    artifact_type: ArtifactType
    product_family: str = Field(min_length=1, max_length=80)
    caller_context: CallerContext

    @field_validator("product_family")
    @classmethod
    def validate_product_family(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized != value:
            raise ValueError("product_family must already be normalized lowercase")
        if any(character not in "abcdefghijklmnopqrstuvwxyz0123456789-_" for character in value):
            raise ValueError(
                "product_family may contain only lowercase letters, numbers, hyphens, and underscores"
            )
        return value


class PlannedAction(BaseModel):
    """An immutable, inspectable action proposed by deterministic logic.

    Planning an action is deliberately separate from executing it. Active,
    observe, demo, and test modes can therefore consume the same plan while
    applying different execution adapters at the system boundary.
    """

    model_config = ConfigDict(frozen=True)

    kind: ActionKind
    consequential: bool = True
    artifact: ArtifactIdentity | None = None
    parameters: dict[str, str] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_action_binding(self) -> "PlannedAction":
        if self.kind is ActionKind.SIGN_ARTIFACT and self.artifact is None:
            raise ValueError("SIGN_ARTIFACT must be bound to an exact artifact identity")
        return self


class DecisionResult(BaseModel):
    """Immutable output of deterministic decision logic before execution."""

    model_config = ConfigDict(frozen=True)

    decision: Decision
    reason_codes: tuple[ReasonCode, ...] = Field(min_length=1)
    planned_actions: tuple[PlannedAction, ...] = ()

    @model_validator(mode="after")
    def validate_failed_decision_actions(self) -> "DecisionResult":
        if self.decision is Decision.FAIL:
            privileged_actions = {
                ActionKind.SIGN_ARTIFACT,
            }
            if any(action.kind in privileged_actions for action in self.planned_actions):
                raise ValueError("failed decisions cannot plan privileged signing actions")
        return self
