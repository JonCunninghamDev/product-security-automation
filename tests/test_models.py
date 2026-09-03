import pytest
from pydantic import ValidationError

from product_security_automation.models import (
    ActionKind,
    ArtifactIdentity,
    ArtifactType,
    CallerContext,
    Decision,
    DecisionResult,
    ExecutionMode,
    PlannedAction,
    ProductArtifact,
    ReasonCode,
)


def _artifact() -> ArtifactIdentity:
    return ArtifactIdentity(name="release.bin", size_bytes=3, sha256="a" * 64)


def _product_artifact() -> ProductArtifact:
    return ProductArtifact(
        identity=_artifact(),
        artifact_type=ArtifactType.FIRMWARE,
        product_family="demo-controller",
        caller_context=CallerContext.ENGINEERING_CI,
    )


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


def test_caller_contexts_are_generic_and_explicit() -> None:
    assert {caller.value for caller in CallerContext} == {
        "engineering-ci",
        "release-pipeline",
        "factory",
        "operator",
    }


def test_artifact_types_are_generic_and_explicit() -> None:
    assert {artifact_type.value for artifact_type in ArtifactType} == {
        "firmware",
        "software-binary",
        "installer",
        "release-artifact",
    }


def test_product_artifact_composes_exact_identity_with_context() -> None:
    product_artifact = _product_artifact()

    assert product_artifact.identity == _artifact()
    assert product_artifact.artifact_type is ArtifactType.FIRMWARE
    assert product_artifact.product_family == "demo-controller"
    assert product_artifact.caller_context is CallerContext.ENGINEERING_CI


def test_product_artifact_is_immutable() -> None:
    product_artifact = _product_artifact()

    with pytest.raises(ValidationError):
        product_artifact.caller_context = CallerContext.OPERATOR


def test_product_family_must_be_normalized_safe_identifier() -> None:
    with pytest.raises(ValidationError):
        ProductArtifact(
            identity=_artifact(),
            artifact_type=ArtifactType.FIRMWARE,
            product_family="Demo Controller",
            caller_context=CallerContext.ENGINEERING_CI,
        )

    with pytest.raises(ValidationError):
        ProductArtifact(
            identity=_artifact(),
            artifact_type=ArtifactType.FIRMWARE,
            product_family="../demo-controller",
            caller_context=CallerContext.ENGINEERING_CI,
        )


def test_caller_context_does_not_modify_artifact_identity() -> None:
    engineering = _product_artifact()
    factory = ProductArtifact(
        identity=engineering.identity,
        artifact_type=engineering.artifact_type,
        product_family=engineering.product_family,
        caller_context=CallerContext.FACTORY,
    )

    assert engineering.identity == factory.identity
    assert engineering.caller_context is not factory.caller_context


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
