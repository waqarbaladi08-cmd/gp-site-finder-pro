from pathlib import Path
import shutil
import sqlite3
import pandas as pd
import pytest
import streamlit as st
from streamlit.testing.v1 import AppTest
import hashlib
import json


@pytest.fixture
def app(tmp_path, monkeypatch):
    source = Path(__file__).resolve().parents[1]
    for name in ('app.py', 'workspace_helpers.py', 'admin_auth.py'):
        shutil.copy(source / name, tmp_path / name)
    monkeypatch.syspath_prepend(str(tmp_path))
    for key in ('SUPABASE_URL', 'SUPABASE_SERVICE_ROLE_KEY', 'SUPABASE_KEY', 'AHREFS_API_KEY', 'GP_ADMIN_PASSWORD'):
        monkeypatch.delenv(key, raising=False)
    st.cache_data.clear()
    at = AppTest.from_file(str(tmp_path / 'app.py'), default_timeout=30).run()
    assert not at.exception
    with sqlite3.connect(tmp_path / 'database/local_sites.db') as db:
        for i in range(61):
            country = 'Pakistan' if i == 0 else ('USA' if i % 2 else 'United State')
            db.execute('INSERT INTO sites(site,country,dr,general_price,type,link_type,favorite,source_file,sheet_name,created_at) VALUES(?,?,?,?,?,?,?,?,?,?)',
                       (f'site-{i}.example', country, None if i % 3 == 0 else 60, '150', 'Technology', 'Dofollow', 0, 'example.csv', 'CSV', '2026-09-25T00:00:00'))
    st.cache_data.clear()
    return at.run(), tmp_path


def test_primary_navigation_search_and_narrowed_pagination(app):
    at, path = app
    assert [button.label for button in at.sidebar.button][:4] == ['Home', 'Search', 'Saved sites', 'Outreach']
    assert [(metric.label, metric.value) for metric in at.metric][:1] == [('Publisher records', '61')]
    at.sidebar.button(key='nav_Search Websites').click().run()
    assert not at.exception
    assert 'USA' not in at.selectbox(key='fast_filter_country').options
    assert 'United States' in at.selectbox(key='fast_filter_country').options
    assert len(at.dataframe[0].value) == 25
    at.number_input(key='fast_page_number').set_value(3).run()
    at.selectbox(key='fast_filter_country').select('Pakistan').run()
    assert not at.exception
    assert at.number_input(key='fast_page_number').value == 1
    assert len(at.dataframe[0].value) == 1
    at.button(key='fast_quick_favorite').click().run()
    at.sidebar.button(key='nav_Favorites').click().run()
    assert not at.exception
    assert len(at.dataframe[0].value) == 1
    with sqlite3.connect(path / 'database/local_sites.db') as db:
        assert db.execute('SELECT count(*) FROM sites WHERE favorite=1').fetchone()[0] == 1


def test_outreach_regeneration_and_admin_guard(app):
    at, _ = app
    at.sidebar.button(key='nav_Outreach Generator').click().run()
    at.text_input(key='outreach_gen_url').set_value('first.example')
    next(b for b in at.button if b.label == 'Generate Outreach Messages').click().run()
    assert not at.exception
    assert 'first.example' in at.text_area(key='generated_cold_email').value
    at.text_input(key='outreach_gen_url').set_value('second.example')
    next(b for b in at.button if b.label == 'Generate Outreach Messages').click().run()
    assert 'second.example' in at.text_area(key='generated_cold_email').value
    at.sidebar.selectbox(key='more_tool').select('Private Contacts').run()
    assert not at.exception
    assert not at.session_state['admin_logged_in']
    assert any('admin' in warning.value.lower() for warning in at.warning)


def test_private_password_reset_login_and_session_revocation(app, monkeypatch):
    at, path = app
    auth_path = path / 'database/web_admin.json'
    auth_path.write_text(json.dumps({
        'username': 'admin',
        'password_hash': hashlib.sha256(b'old-test-password').hexdigest(),
    }))
    with sqlite3.connect(path / 'database/local_sites.db') as db:
        before = db.execute('SELECT * FROM sites ORDER BY id').fetchall()
    monkeypatch.setenv('GP_ADMIN_PASSWORD', 'new-test-private-password')
    at.sidebar.selectbox(key='more_tool').select('Admin Login').run()
    next(t for t in at.text_input if t.label == 'Password').set_value('old-test-password')
    next(b for b in at.button if b.label == '🔓 Login').click().run()
    assert not at.exception
    assert not at.session_state['admin_logged_in']
    next(t for t in at.text_input if t.label == 'Password').set_value('new-test-private-password')
    next(b for b in at.button if b.label == '🔓 Login').click().run()
    assert not at.exception
    assert at.session_state['admin_logged_in']
    at.sidebar.selectbox(key='more_tool').select('Backup & Restore').run()
    assert not at.exception
    assert any('Backup & Restore' == h.value for h in at.header)
    assert not any('Admin Login required' in w.value for w in at.warning)
    at.sidebar.selectbox(key='more_tool').select('Settings').run()
    assert not at.exception
    assert not any(t.label == 'Current Password' for t in at.text_input)
    assert any('GP_ADMIN_PASSWORD' in i.value for i in at.info)
    monkeypatch.setenv('GP_ADMIN_PASSWORD', 'rotated-test-private-password')
    at.run()
    assert not at.exception
    assert not at.session_state['admin_logged_in']
    at.sidebar.selectbox(key='more_tool').select('Backup & Restore').run()
    assert any('Admin Login required' in w.value for w in at.warning)
    with sqlite3.connect(path / 'database/local_sites.db') as db:
        assert db.execute('SELECT * FROM sites ORDER BY id').fetchall() == before
    assert 'new-test-private-password' not in auth_path.read_text()
