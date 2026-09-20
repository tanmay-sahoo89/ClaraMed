from functools import lru_cache

from app.common.logger import get_logger
from app.common.custom_exception import CustomException

from app.components.llm import load_llm
from app.components.vector_store import load_vector_store

from app.config.config import RETRIEVAL_K

from langchain_core.prompts import PromptTemplate
from langchain.chains import RetrievalQA


logger = get_logger(__name__)


# ============================================================
# ClaraMed Medical Prompt
# ============================================================

CPT = """
You are ClaraMed, an AI medical information assistant.

Answer the user's medical question clearly and concisely.

Use the supplied reference context when it is relevant.

IMPORTANT RULES:

1. First determine whether the retrieved context actually
   answers the exact question.

2. Do not use unrelated context simply because it contains
   similar medical keywords.

3. If the context is relevant:
   - Use the information from the context.
   - Do not invent information.

4. If the context is not relevant:
   - Answer using reliable general medical knowledge.
   - Begin the response with:
     "Not covered in the reference document, but generally:"

5. Never fabricate:
   - medical statistics
   - dosages
   - numerical values
   - treatment instructions
   - scientific claims

6. Keep the answer concise, normally around 3-5 sentences.

7. Use plain text only.

8. Do NOT generate HTML tags such as:
   <br>
   <br/>
   <br />
   <p>
   </p>

9. Use normal line breaks when needed.

10. Do not claim to diagnose the user.

11. For urgent or dangerous symptoms, advise the user
    to seek appropriate professional medical care.

Reference Context:
{context}

Question:
{question}

Answer:
"""


# ============================================================
# Prompt Template
# ============================================================

def set_custom_prompt():

    return PromptTemplate(

        template=CPT,

        input_variables=[
            "context",
            "question"
        ]

    )


# ============================================================
# Create QA Chain
# ============================================================

@lru_cache(maxsize=1)
def create_qa_chain():

    try:

        logger.info(
            "Loading vector store for context."
        )


        # ----------------------------------------------------
        # Load FAISS vector store
        # ----------------------------------------------------

        db = load_vector_store()


        if db is None:

            raise CustomException(
                "Vector store not present or empty."
            )


        # ----------------------------------------------------
        # Load Groq LLM
        # ----------------------------------------------------

        llm = load_llm()


        if llm is None:

            raise CustomException(
                "LLM not loaded."
            )


        # ----------------------------------------------------
        # Create Retrieval QA Chain
        # ----------------------------------------------------

        qa_chain = RetrievalQA.from_chain_type(

            llm=llm,

            chain_type="stuff",

            retriever=db.as_retriever(

                search_kwargs={
                    "k": RETRIEVAL_K
                }

            ),

            return_source_documents=True,

            chain_type_kwargs={

                "prompt":
                    set_custom_prompt()

            }

        )


        logger.info(
            "Successfully created the QA Chain."
        )


        return qa_chain


    except Exception as e:

        error_message = CustomException(

            "Failed to make QA chain",

            e

        )

        logger.error(
            str(error_message)
        )


        return None