<div align="center">

# 🔍 Code RAG Pipeline

**Ask your codebase anything.**

A local Retrieval-Augmented Generation system that indexes codebases and answers questions using **LlamaIndex**,
**LanceDB**, and **LM Studio**.

*No cloud. No API keys. Your code stays on your machine.*

---

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![uv](https://img.shields.io/badge/uv-package%20manager-purple.svg)](https://docs.astral.sh/uv/)

</div>

---

## ✨ Features

- 🗂️ **Multi-language support** — Python, JavaScript, TypeScript, JSON, YAML, TOML, and more
- 🧠 **AST-aware parsing** — understands code structure, not just text
- 💬 **Interactive chat** — ask questions about your code in natural language
- 🔒 **100% local** — runs on your machine with LM Studio, no data leaves your system
- 📁 **Git URL support** — index repos directly from GitHub URLs
- ⚡ **Fast indexing** — efficient embedding with LanceDB vector storage

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.12+**
- **[LM Studio](https://lmstudio.ai/)** with its local server running (Apple Silicon recommended)
- **[uv](https://docs.astral.sh/uv/)** package manager

### Install

```bash
# Install globally
uv tool install git+https://github.com/omarcaja/code-rag-pipeline.git

# Or from source
git clone https://github.com/omarcaja/code-rag-pipeline.git
cd code-rag-pipeline
uv sync
```

To reinstall after changes:

```bash
uv tool install --force git+https://github.com/omarcaja/code-rag-pipeline.git
```

#### Editable install (for development)

Install `code-rag` and `code-rag-mcp` globally on your `PATH`, linked to your local checkout:

```bash
cd code-rag-pipeline
uv tool install --editable .
```

Source edits (including `config.toml`) take effect on the next run, with no reinstall needed. Reinstall only after changing
dependencies or `[project.scripts]` in `pyproject.toml`:

```bash
uv tool install --editable --reinstall .
```

To remove it: `uv tool uninstall code-rag-pipeline`. Run `uv tool list` to see what's installed.

### Setup LM Studio

```bash
lms get "qwen/qwen3-coder-30b@6bit" --mlx
lms get https://huggingface.co/Qwen/Qwen3-Embedding-4B-GGUF --gguf
lms server start
```

| Model | Purpose | Size |
|-------|---------|------|
| `qwen/qwen3-coder-30b` (MLX 6-bit, MoE 3B active) | Code reasoning | ~25 GB |
| `text-embedding-qwen3-embedding-4b` (GGUF) | Code embeddings | ~2.5–4 GB |

Sized for an M4 Pro with 48 GB. On 24–32 GB machines use `qwen/qwen3-coder-30b@4bit` (~17 GB) and `Qwen3-Embedding-0.6B`. Load the LLM with at least `context_window` (32768) tokens of context.

### Run

```bash
uv run code-rag
```

<div align="center">

```
╭─────────────────────────────────────╮
│  What do you want to do?            │
│  > Chat with a project              │
│    Index a new project              │
╰─────────────────────────────────────╯
```

</div>

1. **Index a new project** — provide a path or git URL
2. **Chat with a project** — select an indexed project and ask questions
    - Type `new` to reset conversation
    - Type `exit` to quit

### Use from an agent (MCP)

`code-rag-mcp` runs an MCP server over stdio against the same indexes as the CLI. Register it with Claude Code:

```bash
claude mcp add code-rag -- uv --directory /path/to/code-rag-pipeline run code-rag-mcp
```

| Tool | Purpose |
|------|---------|
| `list_projects()` | Indexed project names |
| `search_code(project, query, top_k=8)` | Relevant code chunks with file path and score (embedding model only) |
| `ask_codebase(project, question)` | One-shot answer from the local LLM over retrieved code |
| `index_project(path_or_url)` | Index or re-index a local path or git URL |

---

## ⚙️ Configuration

All settings live in `src/code_rag_pipeline/config/config.toml`:

```toml
[default]
llm_api_base = "http://localhost:1234/v1"   # env LLM_API_BASE overrides
llm_model = "qwen/qwen3-coder-30b"
embed_model = "text-embedding-qwen3-embedding-4b"
query_instruction = "Instruct: Given a question about a codebase, retrieve the code snippets that answer it\nQuery: "
context_window = 32768
data_dir = "~/.code-rag/data"
supported_extensions = [".py", ".js", ".jsx", ".ts", ".tsx", ".astro", ".less", ".css", ".json", ".md", ".toml", ".yaml", ".java", ".jsp", ".tag", ".xml"]
exclude_paths = ["**/data/**", "**/dist/**", "**/node_modules/**", "**/*lock*"]
system_prompt = "You are a code assistant. Answer questions based on the provided context. Cite specific file paths when relevant."
memory_limit = 4096
similarity_top_k = 5
```

Fork and customize. The file is bundled with the package and read at runtime via `importlib.resources`.

---

## 🏗️ Architecture

```
src/code_rag_pipeline/
├── cli/                        # Interactive CLI
│   ├── app.py                  # Main entry point
│   ├── chat_cmd.py             # Chat engine with memory
│   └── index_cmd.py            # Project indexing workflow
│
├── mcp_server.py               # MCP server (stdio) for agents
│
├── config/
│   ├── config.toml             # All settings
│   ├── config.py               # Config reader
│   ├── logging.py              # Colored logging
│   └── llm_settings.py         # LLM & embedding setup
│
├── core/
│   ├── loaders/
│   │   └── document_loader.py  # File discovery & loading
│   └── parsers/
│       ├── factory.py          # Extension-based routing
│       └── splitters.py        # AST & token splitters
│
├── storage/
│   └── vector_index.py         # LanceDB operations
│
└── utils/
    ├── document_helpers.py     # Document grouping
    ├── git.py                  # Git operations
    └── progress.py             # Token bar display
```

**How it works:**

1. **Load** — `SimpleDirectoryReader` scans your project, filtering by supported extensions
2. **Parse** — Documents route to AST-based splitters (Python/JS/TS) or token splitters (configs)
3. **Embed** — Nodes embed via LM Studio's `Qwen3-Embedding-4B` model
4. **Store** — Vectors persist in LanceDB (one table per project)
5. **Chat** — Query engine retrieves relevant context and generates answers

---

## 🛠️ Tech Stack

| Technology                                         | Role                                |
|----------------------------------------------------|-------------------------------------|
| [LlamaIndex](https://docs.llamaindex.ai/)          | Data framework for LLM applications |
| [LanceDB](https://lancedb.com/)                    | Vector database                     |
| [LM Studio](https://lmstudio.ai/)                  | Local LLM inference                 |
| [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) | Agent tool server |
| [Typer](https://typer.tiangolo.com/)               | CLI framework                       |
| [Rich](https://rich.readthedocs.io/)               | Terminal formatting                 |
| [Questionary](https://questionary.readthedocs.io/) | Interactive prompts                 |
| [Tree-sitter](https://tree-sitter.github.io/)      | AST parsing                         |

---

## 📝 Development

```bash
# Type checking
uv run mypy src/

# Run with debug logging
uv run code-rag -v
```

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

*Star this repo if you find it useful!*

</div>
