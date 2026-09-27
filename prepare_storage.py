"""Initialize persistent storage once, before starting the Streamlit server."""

import os
from pathlib import Path
import shutil
import tempfile


def prepare_storage(source_dir: Path, storage_dir: str) -> Path:
    source_dir = source_dir.resolve()
    if not storage_dir:
        return source_dir
    root = Path(storage_dir).expanduser()
    if not root.is_absolute():
        raise ValueError("GP_STORAGE_DIR must be an absolute path")
    root = root.resolve()
    if root == source_dir:
        return root
    root.mkdir(parents=True, exist_ok=True)
    marker = root / ".gp-storage-initialized"
    if marker.exists():
        return root

    # Run only from the start command, before the server accepts sessions.
    # Existing files can be restored production data: never overwrite them.
    for folder in ("database", "assets"):
        source = source_dir / folder
        (root / folder).mkdir(parents=True, exist_ok=True)
        if not source.exists():
            continue
        for item in sorted(source.rglob("*")):
            if not item.is_file() or item.is_symlink():
                continue
            target = root / folder / item.relative_to(source)
            if target.exists():
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            # A failed copy never leaves a partially written database.
            with tempfile.NamedTemporaryFile(dir=target.parent, delete=False) as tmp:
                temp_path = Path(tmp.name)
            try:
                shutil.copyfile(item, temp_path)
                temp_path.replace(target)
            finally:
                temp_path.unlink(missing_ok=True)

    # Do not re-seed after restarts: intentional deletions stay deleted.
    marker.write_text("1\n", encoding="utf-8")
    return root


if __name__ == "__main__":
    location = prepare_storage(
        Path(__file__).resolve().parent,
        os.getenv("GP_STORAGE_DIR", ""),
    )
    print(f"Application storage ready: {location}")
