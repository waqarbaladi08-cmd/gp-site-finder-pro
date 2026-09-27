"""Administrator credentials, including an owner-controlled private reset.

GP_ADMIN_PASSWORD is configured only in the hosting account's secrets. It is
never written to the repository, the database, a backup, or a browser response.
"""

from dataclasses import dataclass
import hashlib
import hmac
import json
from pathlib import Path
import re


@dataclass(frozen=True)
class AdminCredentials:
    username: str
    verifier: str
    managed_in_secrets: bool = False

    @property
    def revision(self) -> str:
        value = f"{self.username}\0{self.verifier}\0{self.managed_in_secrets}"
        return hashlib.sha256(value.encode("utf-8")).hexdigest()


def load_admin_credentials(path: Path, private_password=None):
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(record, dict):
            record = {}
    except (OSError, ValueError):
        record = {}
    username = record.get("username") or "admin"
    if not isinstance(username, str):
        return None

    if private_password is not None:
        # Invalid owner configuration must never fall back to the old password.
        if not isinstance(private_password, str) or len(private_password) < 12:
            return None
        return AdminCredentials(
            username,
            hashlib.sha256(private_password.encode("utf-8")).hexdigest(),
            managed_in_secrets=True,
        )

    verifier = record.get("password_hash", "")
    if not isinstance(verifier, str) or not re.fullmatch(r"[a-fA-F0-9]{64}", verifier):
        return None
    return AdminCredentials(username, verifier.lower())


def verify_admin(credentials, username: str, password: str) -> bool:
    if credentials is None:
        return False
    verifier = hashlib.sha256(password.encode("utf-8")).hexdigest()
    password_matches = hmac.compare_digest(verifier, credentials.verifier)
    username_matches = hmac.compare_digest(
        username.encode("utf-8"), credentials.username.encode("utf-8")
    )
    return password_matches and username_matches


def admin_session_valid(state, credentials) -> bool:
    return bool(
        credentials
        and state.get("admin_logged_in", False)
        and state.get("admin_auth_revision") == credentials.revision
    )
