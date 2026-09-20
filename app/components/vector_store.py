from functools import lru_cache
import os

from langchain_community.vectorstores import FAISS

from app.common.logger import get_logger
from app.common.custom_exception import CustomException
from app.components.embeddings import get_embedding_model
from app.config.config import DB_FAISS_PATH


logger = get_logger(__name__)


@lru_cache(maxsize=1)
def load_vector_store():
    """
    Load the FAISS vector database only once.

    This is one of the main performance improvements.
    """

    try:
        embedding_model = get_embedding_model()

        if embedding_model is None:
            raise CustomException(
                "Embedding model could not be loaded."
            )

        if os.path.exists(DB_FAISS_PATH):

            logger.info("Loading existing vector store...")

            db = FAISS.load_local(
                DB_FAISS_PATH,
                embedding_model,
                allow_dangerous_deserialization=True
            )

            logger.info("Vector store loaded successfully.")

            return db

        else:
            logger.warning(
                "No vector store found at: %s",
                DB_FAISS_PATH
            )

            return None

    except Exception as e:

        error_message = CustomException(
            "Failed to load vector store.",
            e
        )

        logger.error(str(error_message))

        return None


def save_vector_store(text_chunks):

    try:

        if not text_chunks:
            raise CustomException(
                "No chunks were found."
            )

        logger.info(
            "Generating new vector store..."
        )

        embedding_model = get_embedding_model()

        if embedding_model is None:
            raise CustomException(
                "Embedding model could not be loaded."
            )

        db = FAISS.from_documents(
            text_chunks,
            embedding_model
        )

        logger.info(
            "Saving vector store..."
        )

        db.save_local(DB_FAISS_PATH)

        logger.info(
            "Vector store saved successfully."
        )

        # Clear the cached vector store so the newly-created
        # database will be loaded next time.
        load_vector_store.cache_clear()

        return db

    except Exception as e:

        error_message = CustomException(
            "Failed to create vector store.",
            e
        )

        logger.error(str(error_message))

        return None