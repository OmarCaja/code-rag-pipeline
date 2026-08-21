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
- `uv run python -m code_rag_pipeline` — smoke test: checks LLM + embedding endpoints, then loads/parses files from `src/` into nodes.

Models must be pulled before the pipeline runs; a missing model fails at the live connectivity check.

## Architecture

- `config/settings.py` — `setup_llama_settings()` mutates LlamaIndex global `Settings` (LLM + embedding). Reads env vars: `OLLAMA_HOST`, `LLM_MODEL`, `EMBED_MODEL`.
- `core/loaders/document_loader.py` — `SimpleDirectoryReader` restricted to `SUPPORTED_EXTENSIONS` (`.py .js .ts .less .css .json .md`), recursive, hidden files excluded.
- `core/parsers/` — `CodeParserOrchestrator` (factory.py) routes documents by file extension to a parser; `.py` → `PythonCodeParser` (AST-based `CodeSplitter`), everything else / parse failures → `FallbackParser` (token splitter). Add a new language by registering in `_parser_map` in `factory.py`.
- `storage/vector_index.py` — `index_nodes()` (re-exported as `code_rag_pipeline.storage.index_nodes`) embeds BaseNodes via global `Settings.embed_model` into a `LanceDBVectorStore` (default `data/lancedb`, one table per project, `mode="overwrite"`) and persists the docstore to `data/index/{project}`.
- Public API is re-exported through package `__init__.py` files (`config`, `core`, `utils`); import from those namespaces, not deep module paths.
- `config/logging.py` `setup_logging()` must run before other imports trigger loggers; it also silences noisy third-party loggers.

## Gotchas

- `data/` (incl. LanceDB output) is gitignored — generated artifacts, never commit.
- `README.md` has project overview; this file is the source of truth for internals.
- The pre-commit hook writes nothing to the repo; `pyproject.toml` mypy override for `lancedb.*` is currently unused (no direct lancedb imports yet).
- CLI uses `@app.callback()` for shared `setup_logging()` — don't add it back to individual commands.
