import tomllib
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]

_TOML = tomllib.loads((PROJECT_ROOT / "pyproject.toml").read_text())
_CONFIG: dict = _TOML.get("tool", {}).get("code-rag", {})

OLLAMA_HOST: str = _CONFIG.get("ollama_host", "http://localhost:11434")
LLM_MODEL: str = _CONFIG.get("llm_model", "qwen2.5-coder:7b")
EMBED_MODEL: str = _CONFIG.get("embed_model", "nomic-embed-text")
DATA_DIR: Path = PROJECT_ROOT / _CONFIG.get("data_dir", "data")
