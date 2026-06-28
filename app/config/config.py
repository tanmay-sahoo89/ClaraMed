import os

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

DB_FAISS_PATH = "vectorstore/db_faiss"
DATA_PATH = "data/"

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50