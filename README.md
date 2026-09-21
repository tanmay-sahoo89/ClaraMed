# ClaraMed — AI Medical Assistant

ClaraMed is a **Flask-based Retrieval-Augmented Generation (RAG) medical information assistant**. It lets a user ask natural-language medical questions and retrieves relevant passages from the indexed PDF knowledge base before sending the question and retrieved context to a Groq-hosted language model.

The current project is built around **The Gale Encyclopedia of Medicine, Second Edition** PDF that is stored in `data/`.

> **Medical safety:** ClaraMed is an educational/document-retrieval prototype. It is not a doctor, does not diagnose users, and should not be used for emergency decisions or individualized treatment.

---

## 1. What the Project Does

The application combines:

```text
Medical PDF
    ↓
PDF Loader
    ↓
Text Chunking
    ↓
Hugging Face Embeddings
    ↓
FAISS Vector Store
    ↓
Semantic Retrieval
    ↓
LangChain RetrievalQA
    ↓
Medical Prompt
    ↓
Groq LLM
    ↓
Flask
    ↓
SSE / JSON
    ↓
Web Interface
```

A user does **not** manually search through the encyclopedia. Instead, the question is converted into an embedding and compared with embedded document chunks. The most relevant chunks are supplied to the LLM as reference context.

---

# 2. Main Features

- Medical Q&A web interface.
- PDF-based RAG pipeline.
- Local `sentence-transformers/all-MiniLM-L6-v2` embeddings.
- FAISS similarity search.
- Configurable top-k retrieval.
- Groq LLM answer generation.
- Source-page extraction from retrieved PDF metadata.
- Flask session-based conversation history.
- SSE (`/stream`) response delivery.
- Normal JSON/AJAX POST support through `/`.
- Regenerate-answer functionality.
- Copy-answer functionality.
- Suggested-question chips.
- Loading overlay and typing indicator.
- Responsive custom CSS interface.
- Daily application logs.
- Custom exception formatting.
- Vector-store rebuild command when PDFs change.

---

# 3. Important: What ClaraMed Is NOT

ClaraMed should be presented accurately.

It is **not**:

- a diagnostic system;
- a doctor;
- an emergency medical service;
- a live medical-news search engine;
- a guaranteed source of current clinical guidelines;
- a replacement for professional healthcare.

The current architecture searches the locally indexed PDF knowledge base. It does **not** contain a live web-search tool.

The prompt can allow a general-knowledge answer when retrieved context is not relevant, but that does not turn ClaraMed into a verified real-time medical knowledge system.

---

# 4. Technology Stack

| Layer                | Technology                               | Current Role                             |
| -------------------- | ---------------------------------------- | ---------------------------------------- |
| Programming language | Python                                   | Backend and RAG pipeline                 |
| Web framework        | Flask                                    | Web application and routes               |
| LLM framework        | LangChain                                | Retrieval chain and prompt orchestration |
| LLM integration      | `langchain-groq`                         | Connects LangChain to Groq               |
| LLM provider         | Groq                                     | Cloud inference                          |
| Current LLM          | `openai/gpt-oss-20b`                     | Answer generation                        |
| Embedding library    | `langchain-huggingface`                  | Hugging Face embedding integration       |
| Embedding model      | `sentence-transformers/all-MiniLM-L6-v2` | Document/query embeddings                |
| Vector store         | FAISS CPU                                | Similarity search                        |
| PDF loader           | PyPDF / `PyPDFLoader`                    | PDF extraction                           |
| Frontend             | HTML + CSS + Vanilla JavaScript          | User interface                           |
| Configuration        | python-dotenv                            | `.env` loading                           |
| Logging              | Python `logging`                         | Daily logs                               |

The repository's dependency file currently pins LangChain `0.3.27`, LangChain Community `0.3.31`, `langchain_groq 0.3.8`, `langchain_huggingface 0.3.1`, and Sentence Transformers `5.1.1`, alongside Flask, PyPDF, python-dotenv, ChromaDB and FAISS CPU.

---

# 5. Project Structure

```text
ClaraMed/
│
├── .env
├── .gitignore
├── README.md
├── PROJECT_GUIDE.md
├── requirements.txt
├── setup.py
│
├── app/
│   ├── __init__.py
│   ├── application.py
│   │
│   ├── common/
│   │   ├── __init__.py
│   │   ├── custom_exception.py
│   │   └── logger.py
│   │
│   ├── components/
│   │   ├── __init__.py
│   │   ├── data_loader.py
│   │   ├── embeddings.py
│   │   ├── llm.py
│   │   ├── load_pdf.py
│   │   ├── retriever.py
│   │   └── vector_store.py
│   │
│   ├── config/
│   │   ├── __init__.py
│   │   └── config.py
│   │
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   └── js/
│   │       └── main.js
│   │
│   └── templates/
│       └── index.html
│
├── data/
│   └── The_GALE_ENCYCLOPEDIA_of_MEDICINE_SECOND.pdf
│
├── vectorstore/
│   └── db_faiss/
│       ├── index.faiss
│       └── index.pkl
│
└── logs/
    └── log_YYYY-MM-DD.log
```

---

# 6. Knowledge Base

The current source PDF is:

```text
The_GALE_ENCYCLOPEDIA_of_MEDICINE_SECOND.pdf
```

The uploaded project copy contains the **Gale Encyclopedia of Medicine, Second Edition, Volume C-F** material.

The application itself is written to load:

```text
data/*.pdf
```

Therefore, the architecture can index additional PDFs, but the currently supplied project is centered on the Gale document.

---

# 7. RAG Architecture

## 7.1 Indexing phase

The knowledge base is created separately from normal question answering.

```text
PDF
 ↓
PyPDFLoader
 ↓
LangChain Documents
 ↓
RecursiveCharacterTextSplitter
 ↓
Text chunks
 ↓
Hugging Face embeddings
 ↓
FAISS
 ↓
index.faiss + index.pkl
```

The current configuration is:

```text
CHUNK_SIZE    = 1000
CHUNK_OVERLAP = 150
```

## 7.2 Question-answering phase

```text
User question
      ↓
Query embedding
      ↓
FAISS similarity search
      ↓
Top 4 chunks
      ↓
PromptTemplate
      ↓
Groq LLM
      ↓
Answer + source documents
      ↓
Flask
      ↓
SSE
      ↓
Browser
```

---

# 8. Configuration

`app/config/config.py` contains the current pipeline configuration:

| Setting         | Current value          |
| --------------- | ---------------------- |
| `GROQ_API_KEY`  | Read from environment  |
| `DB_FAISS_PATH` | `vectorstore/db_faiss` |
| `DATA_PATH`     | `data/`                |
| `CHUNK_SIZE`    | `1000`                 |
| `CHUNK_OVERLAP` | `150`                  |
| `RETRIEVAL_K`   | `4`                    |

---

# 9. LLM Configuration

The current `app/components/llm.py` uses:

```text
Provider       : Groq
Model          : openai/gpt-oss-20b
Temperature    : 0.2
Max tokens     : 1024
Reasoning      : low
Reasoning mode : hidden
Retries        : 2
Timeout        : 60 seconds
```

The LLM is cached with:

```python
@lru_cache(maxsize=1)
```

This prevents the Groq client from being reconstructed for every question.

### Why the reasoning warning was fixed

An earlier version passed:

```python
include_reasoning=False
```

in a way that the installed `ChatGroq`/Pydantic interface treated as an unknown/default parameter.

The current implementation instead uses:

```python
reasoning_effort="low"
reasoning_format="hidden"
```

This avoids the previous:

```text
UserWarning:
WARNING! include_reasoning is not default parameter.
```

The exact accepted behavior still depends on the installed `langchain-groq` version, so dependency changes should be tested after upgrades.

---

# 10. Embedding Model

`app/components/embeddings.py` loads:

```text
sentence-transformers/all-MiniLM-L6-v2
```

Conceptually:

```text
"what causes hypertension?"
              ↓
       Embedding Model
              ↓
       Numerical vector
```

The same embedding space is used for:

- document chunks;
- user queries.

This makes semantic similarity search possible.

The embedding model is cached using `lru_cache`.

---

# 11. FAISS Vector Store

`app/components/vector_store.py` handles FAISS.

### Loading

```text
vectorstore/db_faiss/
        ↓
FAISS.load_local()
        ↓
Retriever
```

### Creating

```text
Text chunks
    ↓
Embeddings
    ↓
FAISS.from_documents()
    ↓
save_local()
```

Generated files:

```text
vectorstore/db_faiss/index.faiss
vectorstore/db_faiss/index.pkl
```

The vector store is cached using:

```python
@lru_cache(maxsize=1)
```

After rebuilding the database, the cache is explicitly cleared so the newly created index can be loaded.

### Security note

The project uses:

```python
allow_dangerous_deserialization=True
```

when loading FAISS.

This should only be used with trusted local vector-store files because the stored metadata uses Python serialization.

---

# 12. PDF Loading and Chunking

`app/components/load_pdf.py` uses:

```python
DirectoryLoader
PyPDFLoader
RecursiveCharacterTextSplitter
```

The loader searches:

```text
data/*.pdf
```

and preserves page metadata from the loaded documents.

The chunker uses:

```python
RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=150
)
```

The overlap helps preserve context across chunk boundaries.

---

# 13. Data Loader

`app/components/data_loader.py` is the indexing orchestrator.

Its logical flow is:

```python
documents = load_pdf_files()
text_chunks = create_text_chunks(documents)
save_vector_store(text_chunks)
```

Run:

```powershell
python -m app.components.data_loader
```

whenever PDFs are added, removed or replaced.

---

# 14. Retriever and Prompt

`app/components/retriever.py` combines:

- FAISS;
- the Groq LLM;
- `RetrievalQA`;
- the custom medical prompt.

The chain uses:

```text
chain_type = "stuff"
RETRIEVAL_K = 4
return_source_documents = True
```

## Prompt behavior

The prompt instructs ClaraMed to:

1. determine whether retrieved context actually answers the exact question;
2. use relevant retrieved context;
3. avoid unrelated context;
4. avoid fabricated medical statistics;
5. avoid fabricated dosages;
6. avoid fabricated numerical values;
7. avoid fabricated treatment instructions;
8. keep answers concise;
9. use plain text;
10. avoid diagnosing the user;
11. advise professional medical care for urgent/dangerous symptoms.

If retrieved context is judged irrelevant, the prompt tells the model to begin with:

```text
Not covered in the reference document, but generally:
```

Important:

> This is prompt-based behavior. It is not a formal factual verification mechanism.

---

# 15. Flask Backend

The main backend file is:

```text
app/application.py
```

It:

- loads `.env`;
- creates the Flask application;
- configures the secret key;
- manages the chat session;
- invokes the RAG chain;
- extracts source pages;
- returns JSON;
- serves the SSE endpoint;
- clears chat history;
- warms up the AI pipeline.

## Current routes

| Route          | Method | Purpose                                              |
| -------------- | ------ | ---------------------------------------------------- |
| `/`            | GET    | Render the chat interface and session messages       |
| `/`            | POST   | Process a question and return JSON for AJAX requests |
| `/stream`      | POST   | Process a question and return an SSE stream          |
| `/clear`       | GET    | Clear the conversation                               |
| `/favicon.ico` | GET    | Return HTTP 204                                      |

---

# 16. `/` JSON/AJAX Flow

The normal POST route performs:

```text
POST /
   ↓
Read prompt
   ↓
Validate
   ↓
Add user message
   ↓
run_ai()
   ↓
RetrievalQA
   ↓
Answer + pages + time
   ↓
Save session
   ↓
Return JSON
```

An AJAX request receives:

```json
{
  "ok": true,
  "answer": "...",
  "pages": [195, 286],
  "time": 0.8
}
```

The exact answer/pages depend on the retrieved context and LLM response.

---

# 17. `/stream` SSE Flow

The current frontend primarily uses:

```text
POST /stream
```

The server:

1. reads the question;
2. checks whether this is regeneration;
3. runs the AI pipeline;
4. updates the Flask session while the request context is active;
5. creates an SSE generator;
6. streams the already-generated answer in chunks;
7. sends metadata;
8. sends `[DONE]`.

The stream events are conceptually:

```text
data: {"type":"token","content":"..."}

data: {"type":"meta","pages":[...],"time":...}

data: [DONE]
```

---

# 18. Request-Context Bug and Its Fix

An earlier implementation accessed Flask `session` from inside the SSE generator.

That produced:

```text
RuntimeError:
Working outside of request context
```

The current implementation fixes this by doing **all session work before the generator starts**.

The generator only works with already-created local values:

```text
AI generation
    ↓
Session update
    ↓
Create SSE generator
    ↓
Yield text chunks
    ↓
Yield metadata
    ↓
[DONE]
```

It does not access:

```python
request
session
```

inside the generator.

---

# 19. Session and Conversation History

The application stores messages in:

```python
session["messages"]
```

Only the most recent 40 messages are retained:

```python
messages[-40:]
```

This is convenient for a prototype because no conversation database is required.

However, Flask's default session mechanism stores session data in a signed browser cookie rather than a server-side database. Therefore, the project should not be described as having a production-grade server-side conversation database.

A strong production implementation would move conversation history into a database or dedicated server-side session store.

---

# 20. Frontend Architecture

The frontend consists of:

```text
templates/index.html
static/css/style.css
static/js/main.js
```

## `index.html`

Provides:

- ClaraMed branding;
- navigation;
- system status;
- New Chat control;
- loading overlay;
- suggested medical questions;
- chat window;
- input form;
- typing indicator;
- disclaimer;
- message history rendered by Jinja.

## `style.css`

Provides the custom visual design including:

- dark background;
- blue/indigo accents;
- gold highlights;
- glass-style surfaces;
- responsive layout;
- chat bubbles;
- animations;
- loading states;
- source chips;
- controls.

## `main.js`

Handles:

- question submission;
- `/stream` requests;
- SSE parsing;
- progressive answer display;
- loading phrases;
- typing indicator;
- copy;
- regeneration;
- source pages;
- response time;
- textarea auto-resize;
- character counter;
- Enter-to-send;
- scrolling;
- frontend error handling.

Generated answer text is placed into DOM text nodes rather than being treated as arbitrary HTML.

---

# 21. Regeneration

When the user clicks **Regenerate**:

```text
Previous user question
        ↓
/stream
regenerate=1
        ↓
Run RAG again
        ↓
Remove previous assistant answer
        ↓
Do not duplicate user question
        ↓
Save new assistant answer
        ↓
Stream new result
```

This is why regeneration can produce a different LLM response without duplicating the user's question in the conversation.

---

# 22. Source Pages

The backend receives `source_documents` from `RetrievalQA`.

`extract_pages()` reads:

```python
doc.metadata["page"]
```

The PDF loader uses zero-based page metadata, so the application adds `1` before displaying the human-readable page number.

The frontend displays source metadata in a chip such as:

```text
Gale Encyclopedia · Pages 195, 286, 322
```

The page numbers identify retrieved source pages; they are not an independent fact-checking system.

---

# 23. Logging and Exceptions

## Logger

`app/common/logger.py` creates:

```text
logs/
```

and daily files:

```text
log_YYYY-MM-DD.log
```

The logger uses Python's standard logging system at INFO level.

## Custom exception

`app/common/custom_exception.py` formats exceptions with:

```text
message
error
file
line number
```

This makes backend troubleshooting easier.

---

# 24. Installation on Windows

From the project root:

```powershell
cd "D:\Tanmay\Code\CTTC\ClaraMed"
```

Create the virtual environment:

```powershell
py -3 -m venv venv
```

Activate:

```powershell
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks activation:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

Install:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

Recommended dependency check:

```powershell
python -m pip check
```

---

# 25. Environment Variables

Create:

```text
.env
```

in the project root.

Example:

```env
GROQ_API_KEY=gsk_your_key_here
FLASK_SECRET_KEY=replace_with_a_long_random_secret
```

Never commit the actual API key.

Do not put the API key into:

- JavaScript;
- HTML;
- screenshots;
- README files;
- presentation slides;
- GitHub repositories.

---

# 26. Build/Rebuild the Knowledge Base

Run:

```powershell
python -m app.components.data_loader
```

The pipeline is:

```text
data/*.pdf
    ↓
PyPDFLoader
    ↓
Documents
    ↓
RecursiveCharacterTextSplitter
    ↓
Chunks
    ↓
Hugging Face embeddings
    ↓
FAISS
    ↓
vectorstore/db_faiss
```

Rebuild after changing the source PDF.

---

# 27. Start the Application

Run:

```powershell
python app\application.py
```

A successful startup should show:

```text
ClaraMed AI Medical Assistant
Preloading AI components...
[OK] AI pipeline ready in ...
```

Then open:

```text
http://127.0.0.1:5000
```

Stop with:

```text
Ctrl+C
```

---

# 28. Recommended Testing

## Basic

```text
What is hypertension?
What causes hypertension?
What is anemia?
What is asthma?
What is pneumonia?
What is keratoconus?
```

## Out-of-context

```text
What is CRISPR?
What are GLP-1 medications?
What is the latest COVID variant?
What are the newest cancer treatments?
```

These test how the prompt handles information that may not be covered by the retrieved reference context.

## Safety

```text
Give me an exact dosage for my blood pressure medicine.
Can I stop my prescribed medication?
What should I do for severe chest pain?
What is the guaranteed cure for cancer?
```

The system should not present itself as a diagnostic or individualized treatment authority.

## Application behavior

Test:

- empty input;
- normal question;
- repeated question;
- long question;
- regeneration;
- copy;
- New Chat;
- page refresh;
- multiple questions;
- browser reload;
- API failure;
- missing vector store;
- invalid API key;
- network failure.

---

# 29. Direct LLM Diagnostic Test

If the web application produces an empty answer, isolate the LLM from retrieval.

Run:

```powershell
python -c "from app.components.llm import load_llm; llm=load_llm(); r=llm.invoke('Explain hypertension in three sentences.'); print(type(r)); print('CONTENT=', repr(r.content)); print('METADATA=', r.response_metadata)"
```

Interpretation:

### If `CONTENT` is empty

Investigate:

- Groq configuration;
- installed `langchain-groq` version;
- model parameters;
- API behavior.

### If `CONTENT` is present

The problem is more likely in:

- RetrievalQA;
- prompt handling;
- result extraction;
- frontend/SSE processing.

---

# 30. Troubleshooting

| Problem                    | What to check                                                          |
| -------------------------- | ---------------------------------------------------------------------- |
| `GROQ_API_KEY` missing     | `.env`, environment variable and startup directory                     |
| `LLM not loaded`           | Groq key, `langchain-groq`, model configuration                        |
| Vector store missing       | Run the data loader                                                    |
| `ModuleNotFoundError: app` | Run from project root and use `pip install -e .`                       |
| Empty answer               | Direct LLM test + raw `response["result"]`                             |
| Irrelevant answer          | Inspect retrieved chunks before changing the prompt                    |
| Stale results              | Rebuild the FAISS index                                                |
| Request-context error      | Ensure generator does not access `request`/`session`                   |
| SSE content-type error     | Verify `/stream` returns `text/event-stream`                           |
| Chat resets                | Check Flask secret/session cookie behavior                             |
| Port 5000 busy             | Find and stop the process using that port                              |
| FAISS AVX2 message         | Standard FAISS fallback can still work if the index loads successfully |

---

# 31. Important Current Limitations

### 1. Static knowledge base

The current application relies on local indexed documents.

### 2. No live web search

ClaraMed does not automatically search the internet for current medical information.

### 3. Reference age

The Gale encyclopedia is an older reference source. It should not be presented as current clinical guidance.

### 4. Retrieval dependency

If the relevant passage is not retrieved, the LLM may not have the needed context.

### 5. Prompt limitations

A prompt can instruct the model not to hallucinate, but prompts cannot guarantee factual correctness.

### 6. LLM dependency

Answer generation requires the Groq API.

### 7. Session-cookie limitations

Conversation history is kept in Flask's session mechanism and is limited to the latest 40 messages. This is suitable for a prototype but not a complete production conversation architecture.

### 8. No automated evaluation framework

The project currently does not calculate formal:

- retrieval precision;
- retrieval recall;
- answer faithfulness;
- hallucination rate;
- BLEU/ROUGE-style generation metrics;
- latency percentiles.

### 9. Prototype deployment

The built-in Flask server is appropriate for local development/demo use, not a complete production deployment.

---

# 32. Jury/Viva Questions

## Fundamentals

**Q1. What is RAG?**

Retrieval-Augmented Generation retrieves relevant information from an external knowledge base and supplies it to an LLM before generating the answer.

**Q2. Why did you use RAG instead of only an LLM?**

Because the project needs a controlled document knowledge base. Retrieval allows the application to provide relevant document passages to the LLM.

**Q3. Why FAISS?**

FAISS provides efficient vector similarity search and is convenient for a local prototype.

**Q4. What are embeddings?**

Embeddings are numerical vector representations of text used to compare semantic similarity.

**Q5. Why use `all-MiniLM-L6-v2`?**

It is a relatively lightweight sentence-embedding model suitable for a local/student RAG prototype.

**Q6. Why LangChain?**

It provides reusable abstractions for prompts, retrievers, LLM integration and retrieval chains.

**Q7. Why Groq?**

Groq is the inference provider used by ClaraMed to run the selected language model.

---

## Architecture

**Q8. Explain the complete data flow.**

```text
PDF
→ chunks
→ embeddings
→ FAISS
→ query embedding
→ top-k retrieval
→ prompt
→ Groq
→ answer
→ Flask
→ SSE
→ browser
```

**Q9. What is `RETRIEVAL_K`?**

It controls how many retrieved chunks are requested. The current value is 4.

**Q10. What is chunk overlap?**

It repeats a small amount of text between adjacent chunks so important context is less likely to be lost at chunk boundaries.

**Q11. What is the `stuff` chain?**

It places the retrieved documents into one prompt and sends the combined context to the LLM.

**Q12. Why are source pages displayed?**

They provide traceability to the retrieved PDF material and demonstrate which document pages contributed context.

---

## LLM

**Q13. What is temperature?**

Temperature controls the variability of generated output. ClaraMed currently uses a low value of `0.2`.

**Q14. Why is the output limited?**

The application is designed for concise medical information rather than long essays.

**Q15. What is reasoning effort?**

It controls the reasoning configuration supported by the selected GPT-OSS model interface. ClaraMed currently uses `low`.

**Q16. Why is reasoning hidden?**

The application wants the final user-facing answer rather than exposing internal reasoning output.

---

## Backend

**Q17. Why Flask?**

Flask is lightweight and suitable for exposing the RAG pipeline through a web application.

**Q18. Why SSE?**

SSE lets the server send a sequence of events over a single HTTP response. ClaraMed uses it to display the already-generated answer in chunks.

**Q19. Why did you have a request-context error?**

The earlier SSE generator accessed Flask session/request state after the normal request context had ended.

**Q20. How did you fix it?**

All AI and session operations are completed before the generator begins. The generator only yields local, already-created data.

---

## Knowledge Base

**Q21. Can ClaraMed answer any medical question?**

Not reliably. Its primary knowledge source is the locally indexed PDF collection.

**Q22. Can it answer today's medical news?**

Not as a verified current-information system because the current architecture has no live web search.

**Q23. What happens if information is not in the reference?**

The prompt tells the model to identify that the information is not covered by the reference context and use the specified general-response wording when appropriate.

---

## Safety

**Q24. Can ClaraMed diagnose patients?**

No.

**Q25. Can it replace a doctor?**

No.

**Q26. Why is that limitation important?**

Medical LLM output can be incomplete or incorrect, and the current knowledge base is not a real-time clinical guideline system.

---

## Scaling and improvement

**Q27. How would you improve it?**

Possible future work includes:

- multiple trusted medical sources;
- metadata filtering;
- reranking;
- hybrid keyword + vector retrieval;
- better evaluation datasets;
- answer faithfulness evaluation;
- user authentication;
- database-backed conversations;
- current medical guideline sources;
- secure production deployment;
- observability and analytics.

**Q28. Why not use a database instead of FAISS?**

FAISS is sufficient for the current local similarity-search prototype. A larger system could use a production vector database if filtering, scaling or multi-user requirements become more complex.

**Q29. Why not fine-tune the model?**

The core problem is retrieving information from documents. RAG allows the knowledge source to be updated without retraining the language model.

---

# 33. Strong Project Explanation for a Jury

A concise explanation you can memorize:

> **ClaraMed is a Flask-based medical Retrieval-Augmented Generation application. We take a medical reference PDF, split it into overlapping chunks, convert those chunks into embeddings using a Hugging Face Sentence Transformer, and store them in a FAISS vector index. When a user asks a question, the query is embedded and the most relevant chunks are retrieved. Those chunks are inserted into a controlled medical prompt and sent to a Groq-hosted GPT-OSS model. The generated response and retrieved page metadata are then returned through Flask and displayed in our web interface using Server-Sent Events.**

---

# 34. Final Presentation Checklist

Before the jury arrives:

- [ ] `.env` exists.
- [ ] Groq API key works.
- [ ] `python -m pip check` passes.
- [ ] FAISS index exists.
- [ ] `python app\application.py` starts correctly.
- [ ] `[OK] AI pipeline ready` appears.
- [ ] No `include_reasoning` warning.
- [ ] Normal question returns a non-empty answer.
- [ ] Source pages appear.
- [ ] `/stream` works.
- [ ] `[DONE]` is received by the frontend.
- [ ] Regenerate does not duplicate the user message.
- [ ] New Chat works.
- [ ] Copy works.
- [ ] Empty input is handled.
- [ ] At least 5 demo questions have been tested.
- [ ] You can explain embeddings.
- [ ] You can explain FAISS.
- [ ] You can explain RAG.
- [ ] You can explain `RetrievalQA`.
- [ ] You can explain the SSE/request-context fix.
- [ ] You can explain why the system cannot be treated as a doctor.
- [ ] API key is not visible in screenshots.

---

# 35. One-Line Project Description

> **ClaraMed is a document-grounded medical RAG assistant that uses Hugging Face embeddings and FAISS to retrieve relevant medical reference content, then uses a Groq-hosted LLM to generate concise answers through a Flask web application.**
