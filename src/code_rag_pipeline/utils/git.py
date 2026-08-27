import logging
import shutil
import subprocess
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)


def _is_url(value: str) -> bool:
    return value.startswith(("https://", "http://", "git@"))


def _project_name_from_url(url: str) -> str:
    name = url.rstrip("/").rsplit("/", 1)[-1]
    if name.endswith(".git"):
        name = name[:-4]
    return name


def _clone_to_temp(url: str) -> Path:
    dest = Path(tempfile.mkdtemp(prefix="code-rag-"))
    logger.info("Cloning %s into %s", url, dest)

    result = subprocess.run(
        ["git", "clone", "--depth", "1", url, str(dest)],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        shutil.rmtree(dest, ignore_errors=True)
        raise RuntimeError(f"git clone failed: {result.stderr.strip()}")

    return dest


def cleanup_temp(path: Path) -> None:
    shutil.rmtree(path, ignore_errors=True)
    logger.info("Cleaned up %s", path)


def resolve_project_path(path_str: str) -> tuple[str, Path, Path | None]:
    if _is_url(path_str):
        name = _project_name_from_url(path_str)
        path = _clone_to_temp(path_str)
        return name, path, path

    path = Path(path_str).expanduser().resolve()
    return path.name, path, None
