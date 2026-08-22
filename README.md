# Code RAG Pipeline

A local Retrieval-Augmented Generation system that indexes and queries codebases using **LlamaIndex**, **LanceDB**, and **Ollama**.

Ask questions about your code in natural language — the pipeline parses, embeds, and stores your codebase locally, then retrieves relevant context to answer queries.

## Quick Start

### Prerequisites

- Python >= 3.12
- [Ollama](https://ollama.com/) running locally (or via Docker)
- `uv` package manager

### Installation

```bash
uv tool install git+https://github.com/omarcaja/code-rag-pipeline.git
```

This installs `code-rag` globally. To update:

```bash
uv tool install --force git+https://github.com/omarcaja/code-rag-pipeline.git
```

Or install from source:

```bash
git clone https://github.com/omarcaja/code-rag-pipeline.git
cd code-rag-pipeline
uv sync
uv run code-rag
```

### Start Ollama & Pull Models

```bash
docker compose up -d ollama
docker compose --profile init up
```

This pulls two models into a shared Docker volume:
- `nomic-embed-text` — embeddings
- `qwen2.5-coder:7b` — code reasoning

### Run

```bash
uv run code-rag
```

Interactive menu:
1. **Chat with a project** — select an indexed project and ask questions
2. **Index a new project** — provide a path, project name is derived from the folder

## Configuration

All settings live in `pyproject.toml` under `[tool.code-rag]`:

```toml
[tool.code-rag]
ollama_host = "http://localhost:11434"
llm_model = "qwen2.5-coder:7b"
embed_model = "nomic-embed-text"
data_dir = "data"
supported_extensions = [".py", ".js", ".ts", ".less", ".css", ".json", ".md", ".toml", ".yaml"]
exclude_paths = ["**/data/**"]
system_prompt = """
You are a code assistant. Answer the question based on the code context below.
Cite specific file paths when relevant.

Context:
{context_str}

Question: {query_str}

Answer:
"""

[tool.code-rag.ext_map]
py = "python"
js = "javascript"
ts = "typescript"
json = "json"
md = "markdown"
toml = "toml"
yaml = "yaml"
less = "less"
css = "css"
```

## Architecture

```
src/code_rag_pipeline/
├── cli/                # Interactive CLI (Typer + Questionary + Rich)
├── config/
│   ├── config.py       # Reads [tool.code-rag] from pyproject.toml
│   ├── lancedb_settings.py  # LanceDB/index paths
│   ├── logging.py      # Colored logging setup
│   └── ollama_settings.py   # LlamaIndex Settings (LLM + embedding)
├── core/
│   ├── loaders/        # SimpleDirectoryReader with metadata enrichment
│   └── parsers/        # AST-based & fallback code splitters
│       ├── python_parser.py   # Python → CodeSplitter (AST)
│       ├── config_parser.py   # JSON/TOML/YAML → small token chunks
│       └── fallback_parser.py # Everything else → token splitter
├── storage/
│   └── vector_index.py # LanceDB vector store + docstore persistence
└── utils/              # Helpers
```

## Tech Stack

- [LlamaIndex](https://docs.llamaindex.ai/) — data framework for LLM applications
- [LanceDB](https://lancedb.com/) — vector database
- [Ollama](https://ollama.com/) — local LLM inference
- [Typer](https://typer.tiangolo.com/) — CLI framework
- [Questionary](https://questionary.readthedocs.io/) — interactive prompts
- [Rich](https://rich.readthedocs.io/) — terminal formatting
- [Tree-sitter](https://tree-sitter.github.io/) — AST parsing for code splitting

## License

MIT
