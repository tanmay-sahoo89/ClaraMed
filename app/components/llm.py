from functools import lru_cache

from langchain_groq import ChatGroq

from app.config.config import GROQ_API_KEY
from app.common.logger import get_logger
from app.common.custom_exception import CustomException


logger = get_logger(__name__)


@lru_cache(maxsize=1)
def load_llm(
    model_name: str = "openai/gpt-oss-20b",
    groq_api_key: str = GROQ_API_KEY,
):
    """
    Load and cache the Groq LLM used by ClaraMed.

    The model is cached so that Flask does not recreate
    the Groq client for every user question.
    """

    try:

        # --------------------------------------------------------
        # Validate API key
        # --------------------------------------------------------

        if not groq_api_key:

            raise CustomException(
                "GROQ_API_KEY is missing from the environment."
            )

        logger.info("Loading LLM from Groq...")

        # --------------------------------------------------------
        # Create Groq LLM
        # --------------------------------------------------------

        llm = ChatGroq(
            model=model_name,
            groq_api_key=groq_api_key,

            # Lower temperature gives more consistent
            # medical-information responses.
            temperature=0.2,

            # Enough room for ClaraMed's concise answers.
            max_tokens=1024,

            # GPT-OSS supports reasoning effort.
            # Low keeps the response fast while still allowing
            # the model to reason when necessary.
            reasoning_effort="low",

            # Hide reasoning output from the final answer.
            reasoning_format="hidden",

            # Retry transient API failures.
            max_retries=2,

            # Prevent the request from hanging indefinitely.
            timeout=60,
        )

        logger.info(
            "LLM loaded successfully from Groq."
        )

        return llm

    except Exception as e:

        error_message = CustomException(
            "Failed to load LLM model.",
            e,
        )

        logger.error(
            str(error_message)
        )

        return None