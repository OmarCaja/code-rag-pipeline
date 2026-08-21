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
git clone https://github.com/omarcaja/code-rag-pipeline.git
cd code-rag-pipeline
uv sync
```

### Start Ollama & Pull Models

```bash
docker compose up -d ollama
docker compose --profile init up
```

This pulls two models into a shared Docker volume:
- `nomic-embed-text` — embeddings
- `qwen2.5-coder:7b` — code reasoning

### Index a Project

```bash
uv run code-rag index my-project /path/to/your/codebase
```

### Query Your Code

```bash
uv run code-rag query my-project "How does the document loader work?"
```

## CLI Commands

| Command | Description |
|---------|-------------|
| `index <name> <path>` | Parse and embed a codebase into LanceDB |
| `query <name> <question>` | Ask a question about an indexed project |
| `list` | List all indexed projects |

## Architecture

```
src/code_rag_pipeline/
├── cli/            # Typer CLI app
├── config/         # LLM settings, logging
├── core/           # Document loading & code parsing
│   ├── loaders/    # File reader (SimpleDirectoryReader)
│   └── parsers/    # AST-based & fallback code splitters
├── storage/        # LanceDB vector store + docstore persistence
└── utils/          # Helpers
```

**Supported file types:** `.py .js .ts .less .css .json .md`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama server URL |
| `LLM_MODEL` | `qwen2.5-coder:7b` | LLM model for generation |
| `EMBED_MODEL` | `nomic-embed-text` | Embedding model |

## Tech Stack

- [LlamaIndex](https://docs.llamaindex.ai/) — data framework for LLM applications
- [LanceDB](https://lancedb.com/) — vector database
- [Ollama](https://ollama.com/) — local LLM inference
- [Typer](https://typer.tiangolo.com/) — CLI framework
- [Tree-sitter](https://tree-sitter.github.io/) — AST parsing for code splitting

## License

MIT
