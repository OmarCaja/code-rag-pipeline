# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Local RAG pipeline (LlamaIndex + LanceDB + LM Studio) that indexes and queries codebases. src-layout, managed with `uv`, Python >=3.12.

## Commands

- Install: `uv sync` (dev deps included by default via dependency-groups).
- Typecheck: `uv run mypy src/` — also the only pre-commit hook (runs on all of `src/`, ignores staged files).
- No test suite. Verification = mypy + running the app against a live LM Studio server.
- `uv run code-rag` — interactive CLI (index projects, chat with indexed codebases). `-v` enables debug logging.
- `uv run code-rag-mcp` — MCP server over stdio (for agents). Verify tools with an `mcp.Client(StdioServerParameters(...))` script.

## Running

Requires LM Studio's OpenAI-compatible server at `http://localhost:1234/v1` (override via `LLM_API_BASE`) with `qwen/qwen3-coder-30b` and `text-embedding-qwen3-embedding-4b` downloaded (`lms get`, see README). LM Studio loads models on first request (JIT); there is no upfront connectivity check, so a wrong model id only fails at the first index/chat call.

## Architecture

- `config/config.toml` — all settings (bundled with the package, read by `config/config.py` via `importlib.resources`). Values live here, not in `pyproject.toml`.
- `config/llm_settings.py` — `setup_llama_settings()` sets LlamaIndex global `Settings` to `OpenAILike` (LLM) + an `OpenAILikeEmbedding` subclass that prefixes queries with `query_instruction` (Qwen3-Embedding format; documents get no prefix).
- `config/logging.py` — `setup_logging()` must run before other imports trigger loggers; it also silences noisy third-party loggers.
- `core/loaders/document_loader.py` — `SimpleDirectoryReader`, recursive, restricted to `supported_extensions`, hidden files excluded, `exclude_paths` applied.
- `core/parsers/factory.py` — `split_documents()` groups docs by extension and routes via `_parser_map`. Parser types in `splitters.py`: `CodeSplitterParser(language=...)` (tree-sitter `CodeSplitter` for `.py/.js/.jsx/.ts/.tsx/.java`) and `TokenSplitterParser` (128-token chunks for `.json/.toml/.yaml`; 512-token default for everything else, e.g. `.jsp/.tag/.xml/.md/.css`). A `SyntaxError/ValueError/NotImplementedError` falls back to the token splitter. Add a language with a `CodeSplitterParser` entry in `_parser_map` and its extension in `supported_extensions`.
- `storage/vector_index.py` — one LanceDB table per project. `index_nodes()` drops an existing table then embeds via global `Settings.embed_model`; `list_projects()` reads table names and hides names starting with `_`. DB lives in `data_dir` (default `~/.code-rag/data`).
- `cli/app.py` — `@app.callback(invoke_without_command=True)` shows a `questionary` menu; don't add subcommands back. Flows: `cli/index_cmd.py` (`do_index`) and `cli/chat_cmd.py` (`do_chat`, `ChatMemoryBuffer` + `as_chat_engine()`, type `new` to reset). `rich` for output.
- `mcp_server.py` — `MCPServer` (mcp 2.x; `FastMCP` no longer exists) with tools `list_projects`, `search_code` (retriever only, no LLM), `ask_codebase` (single-turn `context` chat engine), `index_project`. stdout is the protocol channel: never `print()` there; logging goes to stderr. Shares storage/core with the CLI.
- `utils/git.py` — `resolve_project_path()` accepts a local path or git URL (`https://`, `http://`, `git@`); URLs are shallow-cloned to a temp dir removed by `cleanup_temp()`. Project/table name = repo or directory name. `load_documents()` makes stored `file_path` metadata repo-relative.

## Conventions

- Public API is re-exported through package `__init__.py` files (`config`, `core`, `storage`, `utils`); import from those namespaces, not deep module paths.
- Imports: relative for same-package (`from .base import ...`), absolute for cross-package (`from code_rag_pipeline.config import ...`). Never `..` parent-relative imports. `__init__.py` re-exports use relative imports.

## Gotchas

- `data/` is gitignored — never commit generated artifacts.
- Reindex after changing the embedding model, parsers or metadata enrichment — old LanceDB tables have the previous schema.
