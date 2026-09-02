import pytest
from pydantic import ValidationError

from product_security_automation.models import (
    ActionKind,
    ArtifactIdentity,
    Decision,
    DecisionResult,
    ExecutionMode,
    PlannedAction,
    ReasonCode,
)


def _artifact() -> ArtifactIdentity:
    return ArtifactIdentity(name="release.bin", size_bytes=3, sha256="a" * 64)


def test_artifact_identity_is_immutable() -> None:
    identity = _artifact()

    with pytest.raises(ValidationError):
        identity.sha256 = "b" * 64


def test_artifact_identity_rejects_non_hex_digest() -> None:
    with pytest.raises(ValidationError):
        ArtifactIdentity(name="release.bin", size_bytes=3, sha256="z" * 64)


def test_artifact_identity_rejects_path_as_name() -> None:
    with pytest.raises(ValidationError):
        ArtifactIdentity(name="nested/release.bin", size_bytes=3, sha256="a" * 64)


def test_execution_modes_are_explicit_and_stable() -> None:
    assert {mode.value for mode in ExecutionMode} == {
        "active",
        "observe",
        "demo",
        "test",
    }


def test_sign_action_must_bind_exact_artifact_identity() -> None:
    with pytest.raises(ValidationError):
        PlannedAction(kind=ActionKind.SIGN_ARTIFACT)


def test_decision_result_can_plan_signing_after_pass() -> None:
    action = PlannedAction(kind=ActionKind.SIGN_ARTIFACT, artifact=_artifact())
    result = DecisionResult(
        decision=Decision.PASS,
        reason_codes=(ReasonCode.POLICY_PASS,),
        planned_actions=(action,),
    )

    assert result.decision is Decision.PASS
    assert result.planned_actions[0].artifact == _artifact()


def test_failed_decision_cannot_plan_signing() -> None:
    action = PlannedAction(kind=ActionKind.SIGN_ARTIFACT, artifact=_artifact())

    with pytest.raises(ValidationError):
        DecisionResult(
            decision=Decision.FAIL,
            reason_codes=(ReasonCode.ARTIFACT_DIGEST_MISMATCH,),
            planned_actions=(action,),
        )


def test_failed_decision_can_still_plan_audit_evidence() -> None:
    action = PlannedAction(
        kind=ActionKind.WRITE_AUDIT_RECORD,
        consequential=False,
        parameters={"event": "policy-failed"},
    )
    result = DecisionResult(
        decision=Decision.FAIL,
        reason_codes=(ReasonCode.ARTIFACT_DIGEST_MISMATCH,),
        planned_actions=(action,),
    )

    assert result.planned_actions == (action,)


def test_decision_result_is_immutable() -> None:
    result = DecisionResult(
        decision=Decision.FAIL,
        reason_codes=(ReasonCode.REQUIRED_EVIDENCE_MISSING,),
    )

    with pytest.raises(ValidationError):
        result.decision = Decision.PASS
