from app.common.logger import get_logger
from app.common.custom_exception import CustomException
from app.components.llm import load_llm
from app.components.vector_store import load_vector_store
from langchain_core.prompts import PromptTemplate
from langchain.chains import RetrievalQA

logger = get_logger(__name__)

CPT = """
    Answer the following medical Question in 2-3 lines maximum using only the information provided in the context.
    Context:
    {Context}
    
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
            llm = llm,
            chain_type = "stuff",
            retriever = db.as_retriever(search_kwargs={'k' : 1}),
            return_source_documents = False,
            chain_type_kwargs = {'prompt':set_custom_prompt()}
        )
        
        logger.info("Successfully created the QA Chain.")
        return qa_chain
    except Exception as e:
        error_message = CustomException("Failed to make QA chain", e)
        logger.error(str(error_message))
        return None