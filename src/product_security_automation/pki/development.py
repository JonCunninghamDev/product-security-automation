"""Ephemeral PKI primitives for local development and portfolio demonstrations.

This module deliberately models only a one-level chain: one self-signed development
CA and leaf certificates issued directly by it. It is not a production CA.
"""

from __future__ import annotations

import os
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from pathlib import Path

from cryptography import x509
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID


class CertificatePurpose(StrEnum):
    """Leaf identities supported by the bounded development CA."""

    SIGNER = "signer"
    SERVICE = "service"


class ValidationReason(StrEnum):
    """Stable, machine-readable certificate rejection reasons."""

    CERTIFICATE_EXPIRED = "CERTIFICATE_EXPIRED"
    CERTIFICATE_NOT_YET_VALID = "CERTIFICATE_NOT_YET_VALID"
    CERTIFICATE_UNTRUSTED = "CERTIFICATE_UNTRUSTED"
    CERTIFICATE_INVALID_SIGNATURE = "CERTIFICATE_INVALID_SIGNATURE"
    CERTIFICATE_INVALID_CA = "CERTIFICATE_INVALID_CA"


class TrustValidationError(ValueError):
    """A fail-closed certificate validation result."""

    def __init__(self, reason: ValidationReason, message: str) -> None:
        super().__init__(message)
        self.reason = reason


@dataclass(frozen=True)
class CertificateMetadata:
    """A secret-free projection suitable for evidence and audit records."""

    subject: str
    issuer: str
    serial_number: str
    not_valid_before: datetime
    not_valid_after: datetime
    sha256_fingerprint: str
    is_ca: bool
    purposes: tuple[str, ...]


@dataclass(frozen=True)
class IssuedCertificate:
    """An issued certificate and its in-memory private key.

    The key has no implicit persistence path. Call ``write_encrypted_private_key``
    explicitly if a local tool needs a file, and always provide a password.
    """

    certificate: x509.Certificate
    _private_key: ec.EllipticCurvePrivateKey

    @property
    def metadata(self) -> CertificateMetadata:
        return inspect_certificate(self.certificate)

    def certificate_pem(self) -> bytes:
        return self.certificate.public_bytes(serialization.Encoding.PEM)

    def encrypted_private_key_pem(self, password: bytes) -> bytes:
        if not password:
            raise ValueError("A non-empty password is required for private-key export")
        return self._private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.BestAvailableEncryption(password),
        )

    def write_encrypted_private_key(self, path: Path, password: bytes) -> None:
        """Persist an encrypted key with owner-only directory and file permissions."""

        path = Path(path)
        path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        os.chmod(path.parent, 0o700)
        flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        descriptor = os.open(path, flags, 0o600)
        try:
            with os.fdopen(descriptor, "wb") as private_key_file:
                private_key_file.write(self.encrypted_private_key_pem(password))
        except BaseException:
            try:
                os.close(descriptor)
            except OSError:
                pass
            raise
        os.chmod(path, 0o600)


@dataclass(frozen=True)
class DevelopmentCertificateAuthority:
    """A process-local development CA whose key is generated in memory."""

    certificate: x509.Certificate
    _private_key: ec.EllipticCurvePrivateKey

    @classmethod
    def create(
        cls,
        common_name: str = "Product Security Automation Development CA",
        *,
        now: datetime | None = None,
        validity: timedelta = timedelta(days=7),
    ) -> DevelopmentCertificateAuthority:
        if validity <= timedelta(0):
            raise ValueError("CA validity must be positive")
        effective_now = _as_utc(now or datetime.now(UTC))
        private_key = ec.generate_private_key(ec.SECP256R1())
        name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, common_name)])
        certificate = (
            x509.CertificateBuilder()
            .subject_name(name)
            .issuer_name(name)
            .public_key(private_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(effective_now - timedelta(minutes=1))
            .not_valid_after(effective_now + validity)
            .add_extension(x509.BasicConstraints(ca=True, path_length=0), critical=True)
            .add_extension(
                x509.KeyUsage(
                    digital_signature=True,
                    content_commitment=False,
                    key_encipherment=False,
                    data_encipherment=False,
                    key_agreement=False,
                    key_cert_sign=True,
                    crl_sign=True,
                    encipher_only=False,
                    decipher_only=False,
                ),
                critical=True,
            )
            .add_extension(
                x509.SubjectKeyIdentifier.from_public_key(private_key.public_key()), False
            )
            .add_extension(
                x509.AuthorityKeyIdentifier.from_issuer_public_key(private_key.public_key()), False
            )
            .sign(private_key, hashes.SHA256())
        )
        return cls(certificate=certificate, _private_key=private_key)

    @property
    def metadata(self) -> CertificateMetadata:
        return inspect_certificate(self.certificate)

    def certificate_pem(self) -> bytes:
        return self.certificate.public_bytes(serialization.Encoding.PEM)

    def issue_certificate(
        self,
        common_name: str,
        purpose: CertificatePurpose,
        *,
        now: datetime | None = None,
        validity: timedelta = timedelta(hours=8),
    ) -> IssuedCertificate:
        if not common_name.strip():
            raise ValueError("Certificate common name must not be blank")
        effective_now = _as_utc(now or datetime.now(UTC))
        not_valid_before = effective_now - timedelta(minutes=1)
        not_valid_after = effective_now + validity
        if not_valid_after > self.certificate.not_valid_after_utc:
            raise ValueError("Leaf certificate validity cannot exceed CA validity")

        private_key = ec.generate_private_key(ec.SECP256R1())
        extended_usage = (
            ExtendedKeyUsageOID.CODE_SIGNING
            if purpose is CertificatePurpose.SIGNER
            else ExtendedKeyUsageOID.SERVER_AUTH
        )
        builder = (
            x509.CertificateBuilder()
            .subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, common_name)]))
            .issuer_name(self.certificate.subject)
            .public_key(private_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(not_valid_before)
            .not_valid_after(not_valid_after)
            .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
            .add_extension(
                x509.KeyUsage(
                    digital_signature=True,
                    content_commitment=False,
                    key_encipherment=False,
                    data_encipherment=False,
                    key_agreement=False,
                    key_cert_sign=False,
                    crl_sign=False,
                    encipher_only=False,
                    decipher_only=False,
                ),
                critical=True,
            )
            .add_extension(x509.ExtendedKeyUsage([extended_usage]), critical=False)
            .add_extension(
                x509.SubjectKeyIdentifier.from_public_key(private_key.public_key()), False
            )
            .add_extension(
                x509.AuthorityKeyIdentifier.from_issuer_public_key(self._private_key.public_key()),
                False,
            )
        )
        if purpose is CertificatePurpose.SERVICE:
            builder = builder.add_extension(
                x509.SubjectAlternativeName([x509.DNSName(common_name)]), critical=False
            )
        certificate = builder.sign(self._private_key, hashes.SHA256())
        return IssuedCertificate(certificate=certificate, _private_key=private_key)


def inspect_certificate(certificate: x509.Certificate) -> CertificateMetadata:
    """Return stable certificate metadata without any private-key material."""

    try:
        basic_constraints = certificate.extensions.get_extension_for_class(
            x509.BasicConstraints
        ).value
    except x509.ExtensionNotFound:
        basic_constraints = x509.BasicConstraints(ca=False, path_length=None)

    purposes: tuple[str, ...] = ()
    try:
        extended_key_usage = certificate.extensions.get_extension_for_class(
            x509.ExtendedKeyUsage
        ).value
        known_purposes = {
            ExtendedKeyUsageOID.CODE_SIGNING: CertificatePurpose.SIGNER.value,
            ExtendedKeyUsageOID.SERVER_AUTH: CertificatePurpose.SERVICE.value,
        }
        purposes = tuple(known_purposes.get(oid, oid.dotted_string) for oid in extended_key_usage)
    except x509.ExtensionNotFound:
        pass

    return CertificateMetadata(
        subject=certificate.subject.rfc4514_string(),
        issuer=certificate.issuer.rfc4514_string(),
        serial_number=f"{certificate.serial_number:X}",
        not_valid_before=certificate.not_valid_before_utc,
        not_valid_after=certificate.not_valid_after_utc,
        sha256_fingerprint=certificate.fingerprint(hashes.SHA256()).hex(),
        is_ca=basic_constraints.ca,
        purposes=purposes,
    )


def validate_certificate(
    certificate: x509.Certificate,
    issuer: x509.Certificate,
    trusted_roots: Iterable[x509.Certificate],
    *,
    at_time: datetime | None = None,
) -> CertificateMetadata:
    """Validate a direct leaf-to-development-CA chain and return safe metadata.

    Validation fails closed and intentionally accepts no intermediate CAs. Trust is
    anchored by an exact SHA-256 certificate fingerprint match.
    """

    effective_time = _as_utc(at_time or datetime.now(UTC))
    _validate_time(certificate, effective_time)
    _validate_time(issuer, effective_time)

    if certificate.issuer != issuer.subject:
        raise TrustValidationError(
            ValidationReason.CERTIFICATE_UNTRUSTED,
            "Leaf issuer does not match the supplied development CA",
        )
    if issuer.issuer != issuer.subject:
        raise TrustValidationError(
            ValidationReason.CERTIFICATE_INVALID_CA,
            "The trust anchor is not self-issued",
        )
    try:
        constraints = issuer.extensions.get_extension_for_class(x509.BasicConstraints).value
        key_usage = issuer.extensions.get_extension_for_class(x509.KeyUsage).value
    except x509.ExtensionNotFound as error:
        raise TrustValidationError(
            ValidationReason.CERTIFICATE_INVALID_CA,
            "The trust anchor lacks required CA extensions",
        ) from error
    if not constraints.ca or not key_usage.key_cert_sign:
        raise TrustValidationError(
            ValidationReason.CERTIFICATE_INVALID_CA,
            "The trust anchor is not permitted to sign certificates",
        )

    trusted_fingerprints = {root.fingerprint(hashes.SHA256()) for root in trusted_roots}
    if issuer.fingerprint(hashes.SHA256()) not in trusted_fingerprints:
        raise TrustValidationError(
            ValidationReason.CERTIFICATE_UNTRUSTED,
            "The issuing development CA is not in the configured trust store",
        )

    try:
        issuer.public_key().verify(
            issuer.signature,
            issuer.tbs_certificate_bytes,
            ec.ECDSA(issuer.signature_hash_algorithm),
        )
        issuer.public_key().verify(
            certificate.signature,
            certificate.tbs_certificate_bytes,
            ec.ECDSA(certificate.signature_hash_algorithm),
        )
    except (InvalidSignature, TypeError, ValueError) as error:
        raise TrustValidationError(
            ValidationReason.CERTIFICATE_INVALID_SIGNATURE,
            "Certificate signature validation failed",
        ) from error

    return inspect_certificate(certificate)


def _validate_time(certificate: x509.Certificate, at_time: datetime) -> None:
    if at_time < certificate.not_valid_before_utc:
        raise TrustValidationError(
            ValidationReason.CERTIFICATE_NOT_YET_VALID,
            "Certificate is not yet valid",
        )
    if at_time > certificate.not_valid_after_utc:
        raise TrustValidationError(
            ValidationReason.CERTIFICATE_EXPIRED,
            "Certificate has expired",
        )


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        raise ValueError("Datetime values must be timezone-aware")
    return value.astimezone(UTC)
