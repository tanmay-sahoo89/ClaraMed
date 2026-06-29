from langchain_groq import ChatGroq
from app.config.config import GROQ_API_KEY
from app.common.logger import get_logger
from app.common.custom_exception import CustomException

logger = get_logger(__name__)

def load_llm(model_name: str = "llama-3.1-8b-instant", groq_api_key: str = GROQ_API_KEY):
    try:
        logger.info("Loading LLM from Groq....")
        llm = ChatGroq(
            model_name=model_name, 
            groq_api_key=groq_api_key, 
            temperature=0.7,
            max_tokens=250,
        )
        logger.info("LLM loaded successfully from groq.....")
        return llm
    except Exception as e:
        error_message = CustomException("Failed to load llm model.")
        logger.error(str(error_message))
        return None