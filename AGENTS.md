# AGENTS.md

Local RAG pipeline (LlamaIndex + LanceDB + Ollama) that indexes and queries codebases. src-layout, managed with `uv`, Python >=3.12.

## Commands

- Typecheck: `uv run mypy src/` — this is also the only pre-commit hook (runs on all of `src/`, ignores staged files).
- No test suite exists. Verification = mypy + running the app against a live Ollama.
- Install: `uv sync --extra dev` (project uses dependency-groups, not `dev` extra — `uv sync` already covers it).

## Running

Requires Ollama reachable at `http://localhost:11434` (override via `OLLAMA_HOST`).

- `docker compose up -d ollama` — start server
- `docker compose --profile init up` — pull models into the shared volume (`nomic-embed-text` + `qwen2.5-coder:7b`)
- `uv run code-rag` — interactive CLI: index projects, chat with indexed codebases.
- `uv run code-rag -v` — same but with debug logging enabled.

Models must be pulled before the pipeline runs; a missing model fails at the live connectivity check.

## Architecture

- `config/config.py` — reads `[tool.code-rag]` from `pyproject.toml` via `tomllib` (stdlib). Source of truth for all defaults: `OLLAMA_HOST`, `LLM_MODEL`, `EMBED_MODEL`, `DATA_DIR`, `SUPPORTED_EXTENSIONS`, `EXCLUDE_PATHS`, `EXT_MAP`, `SYSTEM_PROMPT`.
- `config/ollama_settings.py` — `setup_llama_settings()` mutates LlamaIndex global `Settings` (LLM + embedding). Values come from `config/config.py`.
- `config/lancedb_settings.py` — `LANCEDB_URI`, `INDEX_DIR` paths. Derived from `DATA_DIR` in `config/config.py`.
- `core/loaders/document_loader.py` — `SimpleDirectoryReader` restricted to `SUPPORTED_EXTENSIONS`, recursive, hidden files excluded, `EXCLUDE_PATHS` applied. Enriches document metadata with `language` field via `EXT_MAP`.
- `core/parsers/` — `CodeParserOrchestrator` (factory.py) routes documents by file extension to a parser; `.py` → `PythonCodeParser` (AST-based `CodeSplitter`), `.json/.toml/.yaml` → `ConfigParser` (small 128-token chunks), everything else / parse failures → `FallbackParser` (token splitter). Add a new language by registering in `_parser_map` in `factory.py`.
- `storage/vector_index.py` — `index_nodes()` embeds BaseNodes via global `Settings.embed_model` into a `LanceDBVectorStore` (default `data/lancedb`, one table per project, `mode="overwrite"`) and persists the docstore to `data/index/{project}`. `list_projects()` reads project names from `INDEX_DIR`.
- `cli/app.py` — interactive CLI. `@app.callback()` with `invoke_without_command=True` shows a menu (Chat/Index). Uses `questionary` for arrow-key selectors, `rich` for formatting. Responses rendered in panels with spinner during query.
- Public API is re-exported through package `__init__.py` files (`config`, `core`, `utils`); import from those namespaces, not deep module paths.
- `config/logging.py` `setup_logging()` must run before other imports trigger loggers; it also silences noisy third-party loggers.

## Configuration

All settings are in `pyproject.toml` under `[tool.code-rag]`. No env vars needed — TOML is the single source of truth. See `config/config.py` for the full list of keys and defaults.

## Gotchas

- `data/` (incl. LanceDB output) is gitignored — generated artifacts, never commit.
- `README.md` has project overview; this file is the source of truth for internals.
- CLI uses `@app.callback()` for the interactive menu — don't add subcommands back.
- `pyproject.toml` is indexed alongside code (`.toml` is in `SUPPORTED_EXTENSIONS`), so the LLM can see config values if the right chunks are retrieved.
- Reindex after changing parsers or metadata enrichment — old LanceDB tables have the previous schema.
