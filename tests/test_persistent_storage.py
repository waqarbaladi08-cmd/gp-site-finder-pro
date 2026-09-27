import sqlite3
from pathlib import Path
import shutil

import pytest

from prepare_storage import prepare_storage


def test_restart_preserves_saved_records_and_deleted_uploads(tmp_path):
    source = tmp_path / "source"
    (source / "database").mkdir(parents=True)
    (source / "assets" / "team").mkdir(parents=True)
    with sqlite3.connect(source / "database" / "local_sites.db") as db:
        db.execute("CREATE TABLE sites (site TEXT)")
        db.execute("INSERT INTO sites VALUES ('seed.example')")
    (source / "assets" / "team" / "photo.png").write_bytes(b"seed-image")
    root = prepare_storage(source, str(tmp_path / "disk"))
    with sqlite3.connect(root / "database" / "local_sites.db") as db:
        db.execute("INSERT INTO sites VALUES ('saved.example')")
    (root / "assets" / "team" / "photo.png").unlink()
    prepare_storage(source, str(root))
    with sqlite3.connect(root / "database" / "local_sites.db") as db:
        assert db.execute("SELECT site FROM sites ORDER BY rowid").fetchall() == [
            ("seed.example",), ("saved.example",)
        ]
    assert not (root / "assets" / "team" / "photo.png").exists()


def test_first_start_preserves_previously_restored_data(tmp_path):
    source = tmp_path / "source"
    target = tmp_path / "disk"
    for base in (source, target):
        (base / "database").mkdir(parents=True)
    (source / "database" / "profile_settings.json").write_text("seed")
    (target / "database" / "profile_settings.json").write_text("restored")
    prepare_storage(source, str(target))
    assert (target / "database" / "profile_settings.json").read_text() == "restored"


def test_default_and_relative_storage_locations(tmp_path):
    assert prepare_storage(tmp_path, "") == tmp_path.resolve()
    with pytest.raises(ValueError, match="absolute"):
        prepare_storage(tmp_path, "relative-data")


def test_app_uses_disk_and_keeps_saved_site_after_new_session(tmp_path, monkeypatch):
    import streamlit as st
    from streamlit.testing.v1 import AppTest

    source = tmp_path / "code"
    source.mkdir()
    project = Path(__file__).resolve().parents[1]
    for name in ("app.py", "workspace_helpers.py"):
        shutil.copy2(project / name, source / name)
    disk = tmp_path / "persistent"
    monkeypatch.setenv("GP_STORAGE_DIR", str(disk))
    monkeypatch.syspath_prepend(str(source))
    for key in ("SUPABASE_URL", "SUPABASE_SECRET_KEY", "AHREFS_API_KEY"):
        monkeypatch.delenv(key, raising=False)
    prepare_storage(source, str(disk))
    st.cache_data.clear()
    at = AppTest.from_file(str(source / "app.py"), default_timeout=30).run()
    assert not at.exception
    assert not (source / "database").exists()
    with sqlite3.connect(disk / "database" / "local_sites.db") as db:
        db.execute(
            "INSERT INTO sites(site,country,dr,general_price,type,link_type,"
            "favorite,source_file,sheet_name,created_at) VALUES(?,?,?,?,?,?,?,?,?,?)",
            ("durable.example", "Pakistan", "55", "100", "Technology", "Dofollow",
             0, "test.csv", "CSV", "2026-09-27T00:00:00"),
        )
    st.cache_data.clear()
    at.sidebar.button(key="nav_Search Websites").click().run()
    at.button(key="fast_quick_favorite").click().run()
    assert not at.exception

    # Simulate the next server startup and a new browser session.
    prepare_storage(source, str(disk))
    st.cache_data.clear()
    restarted = AppTest.from_file(str(source / "app.py"), default_timeout=30).run()
    restarted.sidebar.button(key="nav_Favorites").click().run()
    assert not restarted.exception
    assert len(restarted.dataframe[0].value) == 1
    with sqlite3.connect(disk / "database" / "local_sites.db") as db:
        assert db.execute("SELECT site, favorite FROM sites").fetchall() == [
            ("durable.example", 1)
        ]
