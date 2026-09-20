from app.common.logger import get_logger
from app.common.custom_exception import CustomException
from app.components.llm import load_llm
from app.components.vector_store import load_vector_store
from app.config.config import RETRIEVAL_K
from langchain_core.prompts import PromptTemplate
from langchain.chains import RetrievalQA

logger = get_logger(__name__)

CPT = """
    You are a medical assistant. Answer the question in 3-5 sentences.

    Step 1 - Check relevance: Look at the context below and decide whether it
    actually answers THIS exact question, for a general adult/person. Context
    that discusses a different, more specific scenario than what was asked
    (for example: fetal/newborn/pediatric/pregnancy-specific information when a
    general question was asked, or a different condition/organ/age group than
    the one asked about) does NOT count as relevant, even if it mentions the
    same keyword.

    Step 2 - Answer:
    - If the context is relevant, answer using it.
    - If the context is not relevant or is about a different specific scenario,
      ignore it and instead answer using your own general medical knowledge,
      starting your reply with "Not covered in the reference document, but
      generally:".
    - If you don't have reliable general knowledge either, say so plainly
      instead of guessing.

    Never fabricate specific numbers, dosages, or statistics.

    Context:
    {context}

    Question:
    {question}

    Answer:
"""

def set_custom_prompt():
    return PromptTemplate(
        template=CPT,
        input_variables=["context", "question"]
    )

def create_qa_chain():
    try:
        logger.info("Loading vector store for context.")
        db = load_vector_store()

        if db is None:
            raise CustomException("Vector store not present or empty.")

        llm = load_llm()

        if llm is None:
            raise CustomException("LLM not loaded..")

        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=db.as_retriever(search_kwargs={'k': RETRIEVAL_K}),
            return_source_documents=True,
            chain_type_kwargs={'prompt': set_custom_prompt()}
        )

        logger.info("Successfully created the QA Chain.")
        return qa_chain
    except Exception as e:
        error_message = CustomException("Failed to make QA chain", e)
        logger.error(str(error_message))
        return None