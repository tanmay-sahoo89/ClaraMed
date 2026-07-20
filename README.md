# ClaraMed

ClaraMed is a Python-based Retrieval-Augmented Generation (RAG) application for exploring medical PDF documents through a simple web interface. It loads documents, splits them into meaningful chunks, creates embeddings, stores them in a FAISS vector database, and uses a Groq-powered language model to answer user questions based on the indexed content.

## Overview

ClaraMed is designed to make medical documents easier to query. Instead of reading long PDF files manually, users can ask questions in natural language and receive grounded answers based on the document content that was indexed into the system.

## Features

- Loads PDF files from the data directory
- Splits documents into smaller text chunks for retrieval
- Generates embeddings using sentence-transformers
- Stores and retrieves document vectors using FAISS
- Answers questions through a Flask-based chat interface
- Uses Groq LLMs for response generation
- Includes logging and custom exception handling for smoother debugging

## Tech Stack

- Python
- Flask
- LangChain
- FAISS
- Hugging Face sentence-transformers
- PyPDF
- Groq API

## Project Structure

```text
ClaraMed/
├── app/
│   ├── common/          # Logging and exception utilities
│   ├── components/      # PDF loading, chunking, embeddings, LLM, retriever, vector store
│   ├── config/          # Application configuration
│   ├── static/          # CSS and JavaScript assets
│   ├── templates/       # HTML templates for the web app
│   └── application.py   # Flask application entry point
├── data/                # PDF files to be indexed
├── vectorstore/         # FAISS index files
├── requirements.txt     # Python dependencies
├── setup.py             # Package setup configuration
└── README.md            # Project documentation
```

## Prerequisites

Before running the project, make sure you have:

- Python 3.9 or newer
- pip installed
- A Groq API key

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd ClaraMed
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

3. Install dependencies:

```bash
pip install -r requirements.txt
pip install -e .
```

## Configuration

Create a .env file in the project root and add your Groq API key:

```env
GROQ_API_KEY=your_groq_api_key_here
```

You can also adjust the default settings in app/config/config.py:

- DATA_PATH: folder containing PDF files
- DB_FAISS_PATH: location where the FAISS vector store is saved
- CHUNK_SIZE: size of each text chunk
- CHUNK_OVERLAP: overlap between adjacent chunks

## Building the Knowledge Base

Place one or more PDF files into the data directory, then run:

```bash
python -m app.components.data_loader
```

This step will:

- load the PDFs
- split them into chunks
- generate embeddings
- save the vector store to vectorstore/db_faiss

## Running the Application

Start the Flask app with:

```bash
python app/application.py
```

Then open your browser at:

```text
http://127.0.0.1:5000
```

## Usage

1. Open the web app in your browser.
2. Enter a question related to the uploaded medical documents.
3. The application will retrieve relevant context from the vector database and generate an answer using the LLM.

## Notes

- The vector store is built from the PDF files in the data folder.
- If the vector store is missing or outdated, re-run the data loader step.
- Keep your .env file private and do not commit it to version control.

## License

This project is licensed under the Apache 2.0 License.
