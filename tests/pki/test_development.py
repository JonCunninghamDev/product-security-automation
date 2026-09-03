from __future__ import annotations

import json
import stat
from dataclasses import asdict
from datetime import UTC, datetime, timedelta

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import serialization

from product_security_automation.pki import (
    CertificatePurpose,
    DevelopmentCertificateAuthority,
    TrustValidationError,
    ValidationReason,
    validate_certificate,
)

NOW = datetime(2026, 9, 3, 12, 0, tzinfo=UTC)


def test_ephemeral_ca_issues_signer_and_service_certificates_with_metadata() -> None:
    authority = DevelopmentCertificateAuthority.create(now=NOW)

    signer = authority.issue_certificate(
        "development-artifact-signer", CertificatePurpose.SIGNER, now=NOW
    )
    service = authority.issue_certificate(
        "signing-service.local", CertificatePurpose.SERVICE, now=NOW
    )

    assert authority.metadata.is_ca is True
    assert signer.metadata.purposes == ("signer",)
    assert service.metadata.purposes == ("service",)
    assert signer.metadata.issuer == authority.metadata.subject
    alternative_names = service.certificate.extensions.get_extension_for_class(
        x509.SubjectAlternativeName
    ).value
    assert alternative_names.get_values_for_type(x509.DNSName) == ["signing-service.local"]


def test_certificate_from_trusted_development_ca_validates() -> None:
    authority = DevelopmentCertificateAuthority.create(now=NOW)
    signer = authority.issue_certificate("development-signer", CertificatePurpose.SIGNER, now=NOW)

    metadata = validate_certificate(
        signer.certificate, authority.certificate, [authority.certificate], at_time=NOW
    )

    assert metadata.sha256_fingerprint == signer.metadata.sha256_fingerprint


def test_expired_certificate_is_rejected_with_stable_reason() -> None:
    authority = DevelopmentCertificateAuthority.create(now=NOW)
    signer = authority.issue_certificate(
        "short-lived-signer",
        CertificatePurpose.SIGNER,
        now=NOW,
        validity=timedelta(minutes=1),
    )

    with pytest.raises(TrustValidationError) as error:
        validate_certificate(
            signer.certificate,
            authority.certificate,
            [authority.certificate],
            at_time=NOW + timedelta(minutes=2),
        )

    assert error.value.reason is ValidationReason.CERTIFICATE_EXPIRED


def test_certificate_from_untrusted_ca_is_rejected() -> None:
    trusted_authority = DevelopmentCertificateAuthority.create("Trusted Dev CA", now=NOW)
    untrusted_authority = DevelopmentCertificateAuthority.create("Untrusted Dev CA", now=NOW)
    signer = untrusted_authority.issue_certificate(
        "untrusted-signer", CertificatePurpose.SIGNER, now=NOW
    )

    with pytest.raises(TrustValidationError) as error:
        validate_certificate(
            signer.certificate,
            untrusted_authority.certificate,
            [trusted_authority.certificate],
            at_time=NOW,
        )

    assert error.value.reason is ValidationReason.CERTIFICATE_UNTRUSTED


def test_private_key_export_requires_encryption_and_owner_only_permissions(tmp_path) -> None:
    authority = DevelopmentCertificateAuthority.create(now=NOW)
    signer = authority.issue_certificate("development-signer", CertificatePurpose.SIGNER, now=NOW)
    key_path = tmp_path / ".pki" / "signer.key.pem"

    with pytest.raises(ValueError, match="non-empty password"):
        signer.encrypted_private_key_pem(b"")

    signer.write_encrypted_private_key(key_path, b"development-only-password")
    key_bytes = key_path.read_bytes()

    assert b"ENCRYPTED PRIVATE KEY" in key_bytes
    assert stat.S_IMODE(key_path.stat().st_mode) == 0o600
    assert stat.S_IMODE(key_path.parent.stat().st_mode) == 0o700
    with pytest.raises((TypeError, ValueError)):
        serialization.load_pem_private_key(key_bytes, password=None)
    loaded_key = serialization.load_pem_private_key(
        key_bytes, password=b"development-only-password"
    )
    assert (
        loaded_key.public_key().public_numbers()
        == signer._private_key.public_key().public_numbers()
    )


def test_private_key_export_does_not_follow_symbolic_links(tmp_path) -> None:
    authority = DevelopmentCertificateAuthority.create(now=NOW)
    signer = authority.issue_certificate("development-signer", CertificatePurpose.SIGNER, now=NOW)
    target = tmp_path / "existing-file"
    target.write_text("must remain unchanged")
    key_directory = tmp_path / ".pki"
    key_directory.mkdir()
    key_path = key_directory / "signer.key.pem"
    key_path.symlink_to(target)

    with pytest.raises(OSError):
        signer.write_encrypted_private_key(key_path, b"development-only-password")

    assert target.read_text() == "must remain unchanged"


def test_inspection_projection_is_json_serializable_and_secret_free() -> None:
    authority = DevelopmentCertificateAuthority.create(now=NOW)
    signer = authority.issue_certificate("development-signer", CertificatePurpose.SIGNER, now=NOW)

    evidence = json.dumps(asdict(signer.metadata), default=str)

    assert "PRIVATE KEY" not in evidence
    assert "private_key" not in evidence
    assert signer.metadata.sha256_fingerprint in evidence


def test_leaf_validity_cannot_outlive_ca() -> None:
    authority = DevelopmentCertificateAuthority.create(now=NOW, validity=timedelta(hours=1))

    with pytest.raises(ValueError, match="cannot exceed CA validity"):
        authority.issue_certificate(
            "overlong-signer",
            CertificatePurpose.SIGNER,
            now=NOW,
            validity=timedelta(hours=2),
        )
