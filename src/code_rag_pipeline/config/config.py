import tomllib
from importlib.metadata import version
from importlib.resources import files
from pathlib import Path

VERSION: str = version("code-rag-pipeline")

_cfg = tomllib.loads((files("code_rag_pipeline.config") / "config.toml").read_text())

OLLAMA_HOST: str = _cfg["default"]["ollama_host"]
LLM_MODEL: str = _cfg["default"]["llm_model"]
EMBED_MODEL: str = _cfg["default"]["embed_model"]
DATA_DIR: Path = Path(_cfg["default"]["data_dir"]).expanduser()
SUPPORTED_EXTENSIONS: list[str] = _cfg["default"]["supported_extensions"]
EXCLUDE_PATHS: list[str] = _cfg["default"]["exclude_paths"]
EXT_MAP: dict[str, str] = {f".{k}": v for k, v in _cfg["default"]["ext_map"].items()}
SYSTEM_PROMPT: str = _cfg["default"].get("system_prompt",
                                         "You are a code assistant. Answer based on the code context.\n\nContext:\n{context_str}\n\nQuestion: {query_str}\n\nAnswer:")
