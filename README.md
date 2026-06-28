# ClaraMed

> **Status:** Under active development

ClaraMed is a Python-based document processing project that loads PDF files, splits them into text chunks, computes embeddings using Hugging Face, and stores the result in a FAISS vector store.

## Features

- Load PDF files from `data/`
- Split documents into text chunks
- Generate embeddings with `sentence-transformers/all-MiniLM-L6-v2`
- Save and load FAISS vector store from `vectorstore/db_faiss`
- Simple logging and custom exception handling

## Requirements

Dependencies are listed in `requirements.txt` and installed via:

```bash
pip install -r requirements.txt
```

## Setup

Install the package and its dependencies locally in editable mode:

```bash
pip install -e .
```

> This installs `ClaraMed` along with the dependencies listed in `requirements.txt` via `setup.py`.

## Usage

1. Place PDF files into the `data/` directory.
2. Run the data loader to process PDFs and build the vector store:

```bash
python -m app.components.data_loader
```

## Configuration

Environment variables and constants are defined in `app/config/config.py`:

- `GROQ_API_KEY` — optional environment variable for external API usage
- `DB_FAISS_PATH` — vector store save/load path
- `DATA_PATH` — PDF input folder
- `CHUNK_SIZE` — text chunk size
- `CHUNK_OVERLAP` — chunk overlap size

## Project Structure

- `app/`
  - `components/` — PDF loading, chunking, embeddings, vector store creation
  - `common/` — custom exception and logger utilities
  - `config/` — project configuration constants
- `data/` — source PDF files
- `vectorstore/` — saved FAISS index files
- `requirements.txt` — Python dependencies
- `setup.py` — package metadata

## Notes

- Keep `.env` and local environment settings out of source control.
- `vectorstore/` and `logs/` are ignored by `.gitignore`.

## License

This project is licensed under the Apache 2.0 License.
