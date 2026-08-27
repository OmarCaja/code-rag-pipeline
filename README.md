<div align="center">

# 🔍 Code RAG Pipeline

**Ask your codebase anything.**

A local Retrieval-Augmented Generation system that indexes codebases and answers questions using **LlamaIndex**,
**LanceDB**, and **Ollama**.

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
- 🔒 **100% local** — runs on your machine with Ollama, no data leaves your system
- 📁 **Git URL support** — index repos directly from GitHub URLs
- ⚡ **Fast indexing** — efficient embedding with LanceDB vector storage

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.12+**
- **[Ollama](https://ollama.com/)** running locally (or via Docker)
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

### Setup Ollama

```bash
# Start Ollama server
docker compose up -d ollama

# Pull required models
docker compose --profile init up
```

This pulls two models into a shared Docker volume:
| Model | Purpose | |-------|---------| | `nomic-embed-text` | Code embeddings | | `qwen2.5-coder:7b` | Code reasoning |

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

---

## ⚙️ Configuration

All settings live in `src/code_rag_pipeline/config/config.toml`:

```toml
[default]
ollama_host = "http://localhost:11434"
llm_model = "qwen2.5-coder:7b"
embed_model = "nomic-embed-text"
data_dir = "~/.code-rag/data"
supported_extensions = [".py", ".js", ".jsx", ".ts", ".tsx", ".astro", ".less", ".css", ".json", ".md", ".toml", ".yaml"]
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
├── config/
│   ├── config.toml             # All settings
│   ├── config.py               # Config reader
│   ├── logging.py              # Colored logging
│   └── ollama_settings.py      # LLM & embedding setup
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
3. **Embed** — Nodes embed via Ollama's `nomic-embed-text` model
4. **Store** — Vectors persist in LanceDB (one table per project)
5. **Chat** — Query engine retrieves relevant context and generates answers

---

## 🛠️ Tech Stack

| Technology                                         | Role                                |
|----------------------------------------------------|-------------------------------------|
| [LlamaIndex](https://docs.llamaindex.ai/)          | Data framework for LLM applications |
| [LanceDB](https://lancedb.com/)                    | Vector database                     |
| [Ollama](https://ollama.com/)                      | Local LLM inference                 |
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
