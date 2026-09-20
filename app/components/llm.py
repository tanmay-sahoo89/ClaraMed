from langchain_groq import ChatGroq
from app.config.config import GROQ_API_KEY
from app.common.logger import get_logger
from app.common.custom_exception import CustomException

logger = get_logger(__name__)

def load_llm(model_name: str = "openai/gpt-oss-20b", groq_api_key: str = GROQ_API_KEY):
    try:
        logger.info("Loading LLM from Groq....")
        llm = ChatGroq(
            model_name=model_name,
            groq_api_key=groq_api_key,
            temperature=0.5,
            max_tokens=450,
        )
        logger.info("LLM loaded successfully from groq.....")
        return llm
    except Exception as e:
        error_message = CustomException("Failed to load llm model.", e)
        logger.error(str(error_message))
        return None