import os
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.common.logger import get_logger
from app.common.custom_exception import CustomException
from app.config.config import DATA_PATH, CHUNK_SIZE, CHUNK_OVERLAP

logger = get_logger(__name__)

def load_pdf_files():
    try:
        if not os.path.exists(DATA_PATH):
            raise CustomException("Data Path doesn't exist.")
        logger.info(f"Loading files from {DATA_PATH}")
        
        loader = DirectoryLoader(
            DATA_PATH,
            glob="*.pdf",
            loader_cls=PyPDFLoader
        )
        
        documents = loader.load() #pdf stored in this
        
        if not documents:
            logger.warning("No PDF's were found.")
        else:
            logger.info(f"Successfully fetched {len(documents)} documents.")
        return documents
    except Exception as e:
        error_message = CustomException("Failed to load PDF", e)
        logger.error(str(error_message))
        return []
    
def create_text_chunks(documents):
    