#!/usr/bin/env python3
"""Read a Streamlit data directory or its backup ZIP; never modify the source.

Usage: python scripts/export_legacy.py ../ private/legacy.json
       python scripts/export_legacy.py /path/to/streamlit-backup.zip private/legacy.json
Passwords, API keys and sessions are deliberately excluded.
"""
import base64
import json
import mimetypes
import pathlib
import sqlite3
import sys
import tempfile
import zipfile

DATABASES = {
    'local_sites.db': ['sites', 'favorites', 'deleted_sites', 'reseller_settings'],
    'web_private_contacts.db': ['contacts'],
    'contact_us.db': ['contact_messages'],
    'team_profiles.db': ['team_members'],
    'reseller_private.db': ['reseller_private'],
    'sheet_structure.db': ['sheet_structure'],
    'outreach_pipeline.db': ['outreach_pipeline'],
    'admin_private_contacts.db': ['admin_private_contacts'],
}

def export(source, output):
    source, output = pathlib.Path(source).resolve(), pathlib.Path(output).resolve()
    with tempfile.TemporaryDirectory() as temp:
        root = source
        if source.is_file():
            root = pathlib.Path(temp)
            with zipfile.ZipFile(source) as archive:
                total = 0
                for info in archive.infolist():
                    path = pathlib.PurePosixPath(info.filename)
                    allowed = (len(path.parts) == 2 and path.parts[0] == 'database' and
                               (path.name in DATABASES or path.name == 'profile_settings.json'))
                    allowed |= path.parts[:1] == ('assets',) and path.suffix.lower() in {'.png', '.jpg', '.jpeg', '.webp'}
                    if not allowed or path.is_absolute() or '..' in path.parts:
                        continue
                    total += info.file_size
                    if info.file_size > 100 * 1024 * 1024 or total > 200 * 1024 * 1024:
                        raise ValueError('Backup is too large.')
                    dest = root.joinpath(*path.parts)
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.write_bytes(archive.read(info))
        data = {'format': 'gp-streamlit-export', 'tables': {}, 'media': []}
        for filename, tables in DATABASES.items():
            file = root / 'database' / filename
            if not file.exists():
                continue
            with sqlite3.connect(file.as_uri() + '?mode=ro', uri=True) as conn:
                conn.row_factory = sqlite3.Row
                present = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
                conn.execute('BEGIN')
                for table in tables:
                    if table in present:
                        data['tables'][table] = [dict(r) for r in conn.execute(f'SELECT * FROM {table}')]
        profile = root / 'database' / 'profile_settings.json'
        data['profile'] = json.loads(profile.read_text()) if profile.exists() else {'brand_name': 'GP Site Finder Pro'}
        for image in (root / 'assets').rglob('*') if (root / 'assets').exists() else []:
            if image.is_file() and image.suffix.lower() in {'.png', '.jpg', '.jpeg', '.webp'}:
                if image.stat().st_size > 1024 * 1024:
                    raise ValueError(f'Image exceeds 1 MB: {image.name}')
                key = image.relative_to(root).as_posix()
                data['media'].append({'key': key, 'content_type': mimetypes.guess_type(image.name)[0],
                                      'data': base64.b64encode(image.read_bytes()).decode()})
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(data, ensure_ascii=False))
        output.chmod(0o600)
        print(json.dumps({'exported': {k: len(v) for k, v in data['tables'].items()},
                          'photos': len(data['media']), 'credentials_exported': False}))

if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit('Usage: export_legacy.py DATA_DIRECTORY_OR_BACKUP_ZIP OUTPUT_JSON')
    export(*sys.argv[1:])
