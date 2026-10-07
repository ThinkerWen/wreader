import os
import shutil
import sys
from pathlib import Path

from app.config.settings import settings

TEMPLATES = Path(__file__).resolve().parents[1]


def data_dir() -> Path:
    configured = os.getenv("WREADER_DATA_DIR")
    base = (
        Path(configured).expanduser()
        if configured
        else (
            Path.home() / "Library/Application Support/wreader"
            if sys.platform == "darwin"
            else Path(os.getenv("XDG_DATA_HOME", Path.home() / ".local/share")) / "wreader"
        )
    )
    return base.resolve()


def prepare_data() -> Path:
    root = data_dir()
    sources = root / "sources"
    first_run = not root.exists() or (root.is_dir() and not any(root.iterdir()))
    if not root.exists():
        root.mkdir(parents=True, mode=0o700)
    root.chmod(0o700)
    if first_run:
        sources.mkdir(mode=0o700)
        shutil.copy2(TEMPLATES / "_configurations/source_config.yaml", sources / "source_config.yaml")
        for template in (TEMPLATES / "_sources").glob("*.json"):
            shutil.copy2(template, sources / template.name)
    if sources.is_dir():
        sources.chmod(0o700)
    if not sources.is_dir() or not (sources / "source_config.yaml").is_file():
        raise RuntimeError(f"书源配置不存在: {sources}")
    if not os.access(root, os.R_OK | os.W_OK):
        raise RuntimeError(f"数据目录不可读写: {root}")
    settings.APP_PATH = TEMPLATES
    settings.SOURCE_PATH = sources
    settings.CONFIGURATION_PATH = sources
    return root
