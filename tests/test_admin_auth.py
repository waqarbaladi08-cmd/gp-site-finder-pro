import hashlib
import json
from pathlib import Path

from admin_auth import load_admin_credentials, verify_admin, admin_session_valid


def legacy_file(tmp_path: Path):
    path = tmp_path / "web_admin.json"
    path.write_text(json.dumps({
        "username": "admin",
        "password_hash": hashlib.sha256(b"old-test-password").hexdigest(),
    }))
    return path


def test_existing_login_keeps_working_without_owner_override(tmp_path):
    credentials = load_admin_credentials(legacy_file(tmp_path))
    assert verify_admin(credentials, "admin", "old-test-password")
    assert not verify_admin(credentials, "other", "old-test-password")
    assert not verify_admin(credentials, "admin", "wrong-password")
    assert not credentials.managed_in_secrets


def test_private_reset_replaces_old_password_without_modifying_files(tmp_path):
    path = legacy_file(tmp_path)
    original = path.read_bytes()
    credentials = load_admin_credentials(path, "new-test-private-password")
    assert verify_admin(credentials, "admin", "new-test-private-password")
    assert not verify_admin(credentials, "admin", "old-test-password")
    assert credentials.managed_in_secrets
    assert "new-test-private-password" not in repr(credentials)
    assert path.read_bytes() == original


def test_invalid_secret_never_restores_the_old_password(tmp_path):
    path = legacy_file(tmp_path)
    for value in ["", "short", 123456789012, False, []]:
        credentials = load_admin_credentials(path, value)
        assert credentials is None
        assert not verify_admin(credentials, "admin", "old-test-password")


def test_reset_revokes_existing_admin_sessions(tmp_path):
    path = legacy_file(tmp_path)
    old = load_admin_credentials(path)
    session = {"admin_logged_in": True, "admin_auth_revision": old.revision}
    assert admin_session_valid(session, old)
    changed = load_admin_credentials(path, "new-test-private-password")
    assert not admin_session_valid(session, changed)
    assert not admin_session_valid({"admin_logged_in": True}, changed)
    assert not admin_session_valid(session, None)


def test_missing_or_invalid_auth_has_no_factory_password(tmp_path):
    path = tmp_path / "web_admin.json"
    for content in [None, "{}", "[]", "invalid-json", '{"password_hash":""}']:
        if content is not None:
            path.write_text(content)
        assert load_admin_credentials(path) is None
        assert not verify_admin(load_admin_credentials(path), "admin", "admin123")
        reset = load_admin_credentials(path, "new-test-private-password")
        assert verify_admin(reset, "admin", "new-test-private-password")
