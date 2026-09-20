# ClaraMed

ClaraMed is a Flask-based Retrieval-Augmented Generation (RAG) application for asking questions about medical PDF documents. It indexes PDFs with local Hugging Face embeddings, retrieves relevant passages with FAISS, and uses a Groq-hosted language model to generate concise answers with source-page references.

## Features

- Reads every PDF in `data/`
- Splits documents into overlapping text chunks
- Creates local embeddings with `sentence-transformers/all-MiniLM-L6-v2`
- Stores embeddings and metadata in a FAISS index
- Answers questions through a responsive Flask chat interface
- Retrieves up to four relevant chunks by default
- Returns source page numbers with successful answers
- Supports AJAX chat responses without a full-page reload
- Includes suggested questions, auto-resizing input, typing feedback, clear-chat support, and responsive styling
- Writes application diagnostics to daily log files

> ClaraMed is an information-retrieval tool, not a substitute for a qualified healthcare professional. Do not use it for diagnosis or emergency decisions.

## Technology

- Python 3.9+
- Flask
- LangChain and LangChain Community
- FAISS CPU
- Hugging Face Sentence Transformers
- PyPDF
- Groq API through `langchain-groq`
- Vanilla HTML, CSS, and JavaScript

## Project layout

```text
ClaraMed/
├── app/
│   ├── common/                 # Logging and custom exceptions
│   ├── components/             # PDF, embeddings, FAISS, LLM, and RAG pipeline
│   ├── config/                 # Environment variables and pipeline settings
│   ├── static/
│   │   ├── css/style.css       # ClaraMed visual design and responsive layout
│   │   └── js/main.js          # AJAX chat and browser interactions
│   ├── templates/index.html    # Jinja chat interface
│   └── application.py          # Flask entry point and routes
├── data/                       # Source PDF files
├── vectorstore/db_faiss/       # Generated FAISS index and metadata
├── logs/                       # Generated daily logs
├── requirements.txt
├── setup.py
├── README.md
└── PROJECT_GUIDE.md
```

## Prerequisites

- Python 3.9 or newer
- pip
- A Groq API key
- Internet access on first run so the embedding model can be downloaded and for Groq requests

## Windows setup and run

Open PowerShell in the repository root:

```powershell
cd "D:\Tanmay\Code\CTTC\ClaraMed"
```

Create a virtual environment if needed and activate it:

```powershell
py -3 -m venv venv
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

Create `.env` in the project root:

```env
GROQ_API_KEY=gsk_your_key_here
FLASK_SECRET_KEY=replace_with_a_long_random_secret
```

`FLASK_SECRET_KEY` is optional, but setting it keeps browser sessions stable across server restarts. Never commit `.env`.

## Build or rebuild the knowledge base

The repository may already contain `vectorstore/db_faiss`. Run the loader whenever PDFs are added, removed, or replaced:

```powershell
python -m app.components.data_loader
```

The loader reads `data/*.pdf`, creates 1,000-character chunks with 150-character overlap, generates embeddings, and writes the FAISS files to `vectorstore/db_faiss`.

## Start the application

```powershell
python app\application.py
```

Open <http://127.0.0.1:5000> in a browser. Stop the server with `Ctrl+C`.

## Configuration

Settings are defined in `app/config/config.py`:

| Setting | Default | Purpose |
|---|---:|---|
| `GROQ_API_KEY` | from environment | Groq authentication |
| `DB_FAISS_PATH` | `vectorstore/db_faiss` | FAISS index location |
| `DATA_PATH` | `data/` | PDF source directory |
| `CHUNK_SIZE` | `1000` | Characters per chunk |
| `CHUNK_OVERLAP` | `150` | Overlap between chunks |
| `RETRIEVAL_K` | `4` | Number of chunks retrieved per question |

The current LLM configuration is in `app/components/llm.py`: Groq model `openai/gpt-oss-20b`, temperature `0.5`, and maximum output of `450` tokens.

## How a request works

1. The browser submits a question using `fetch()` as an AJAX request.
2. Flask records the user message in the session.
3. The RAG chain loads the FAISS index and retrieves up to `RETRIEVAL_K` chunks.
4. The prompt asks the model to check whether the context is relevant. If it is not, the response clearly states that the answer is general knowledge and not covered by the reference document.
5. Groq generates the answer.
6. Flask returns JSON containing `ok`, `answer`, and source `pages`.
7. The browser appends the answer and source-page text to the chat without reloading the page.

## Routes

| Route | Method | Purpose |
|---|---|---|
| `/` | GET | Render the chat page and current session messages |
| `/` | POST | Process a question; returns JSON for AJAX requests or HTML for regular form requests |
| `/clear` | GET | Clear the current browser session's conversation |
| `/favicon.ico` | GET | Return an empty successful favicon response |

## Troubleshooting

| Problem | Solution |
|---|---|
| `GROQ_API_KEY` is missing | Create `.env` in the project root or set `$env:GROQ_API_KEY` before starting Flask |
| Vector store is missing or stale | Run `python -m app.components.data_loader` |
| `ModuleNotFoundError: app` | Run commands from the repository root and use `pip install -e .` |
| First run is slow | The embedding model is downloaded and cached locally |
| Answers are not relevant | Add the correct PDFs to `data/` and rebuild the vector store |
| Port 5000 is busy | Run `Get-NetTCPConnection -LocalPort 5000`, then stop the specific process with `Stop-Process -Id <PID>` |
| Chat history resets | The session cookie is cleared or `FLASK_SECRET_KEY` changed |

For the detailed architecture and file-by-file explanation, see [PROJECT_GUIDE.md](PROJECT_GUIDE.md).

## License

Apache License 2.0. See [LICENSE](LICENSE).
