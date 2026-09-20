# pyrefly: ignore [missing-import]

import os
import re
import json
import time
import traceback

from dotenv import load_dotenv

# Load .env before importing application components
load_dotenv()

from flask import (
    Flask,
    render_template,
    request,
    session,
    redirect,
    url_for,
    jsonify,
    Response,
)

from app.components.retriever import create_qa_chain


# ============================================================
# Flask App
# ============================================================

app = Flask(__name__)

app.secret_key = os.environ.get(
    "FLASK_SECRET_KEY",
    "claramed-demo-secret-key-change-this",
)

app.config["JSON_AS_ASCII"] = False


# ============================================================
# Clean AI Response
# ============================================================

def clean_ai_text(value):
    if value is None:
        return ""

    text = str(value)

    # Convert accidental HTML line breaks
    text = re.sub(
        r"<br\s*/?>",
        "\n",
        text,
        flags=re.IGNORECASE,
    )

    # Remove closing paragraph tags
    text = re.sub(
        r"</p\s*>",
        "\n",
        text,
        flags=re.IGNORECASE,
    )

    # Remove opening paragraph tags
    text = re.sub(
        r"<p\s*>",
        "",
        text,
        flags=re.IGNORECASE,
    )

    return text.strip()


# ============================================================
# Extract Source Pages
# ============================================================

def extract_pages(source_documents):
    pages = []

    for doc in source_documents or []:

        try:
            page = doc.metadata.get("page")

            if page is not None:
                page_number = int(page) + 1

                if page_number not in pages:
                    pages.append(page_number)

        except (AttributeError, TypeError, ValueError):
            continue

    return sorted(pages)


# ============================================================
# AJAX Detection
# ============================================================

def is_ajax_request():
    return (
        request.headers.get("X-Requested-With")
        == "XMLHttpRequest"
    )


# ============================================================
# Session Helpers
# ============================================================

def get_messages():
    return session.get(
        "messages",
        [],
    )


def save_messages(messages):
    # Keep the Flask session cookie reasonably small.
    # Only the most recent 40 messages are retained.
    session["messages"] = messages[-40:]

    session.modified = True


# ============================================================
# AI Pipeline
# ============================================================

def run_ai(user_input):
    start_time = time.perf_counter()

    # Load cached QA chain
    qa_chain = create_qa_chain()

    if qa_chain is None:
        raise RuntimeError(
            "The AI pipeline could not be created. "
            "Check the Flask terminal, GROQ_API_KEY, "
            "dependencies and vector store."
        )

    # Run RAG pipeline
    response = qa_chain.invoke({
        "query": user_input
    })

    # Extract answer
    result = clean_ai_text(
        response.get(
            "result",
            "",
        )
    )

    if not result:
        result = (
            "I could not generate an answer "
            "for that question."
        )

    # Extract source pages
    pages = extract_pages(
        response.get(
            "source_documents",
            [],
        )
    )

    # Calculate response time
    elapsed = round(
        time.perf_counter()
        - start_time,
        2,
    )

    return result, pages, elapsed


# ============================================================
# Main Route
# ============================================================

@app.route(
    "/",
    methods=["GET", "POST"],
)
def index():

    if "messages" not in session:
        session["messages"] = []

    # ========================================================
    # POST
    # ========================================================

    if request.method == "POST":

        user_input = request.form.get(
            "prompt",
            "",
        ).strip()

        # ----------------------------------------------------
        # Empty question
        # ----------------------------------------------------

        if not user_input:

            if is_ajax_request():
                return jsonify({
                    "ok": False,
                    "error": "Please enter a medical question.",
                }), 400

            return redirect(
                url_for("index")
            )

        # ----------------------------------------------------
        # Save user message
        # ----------------------------------------------------

        messages = get_messages()

        messages.append({
            "role": "user",
            "content": user_input,
        })

        # ----------------------------------------------------
        # Run AI
        # ----------------------------------------------------

        try:

            result, pages, elapsed = run_ai(
                user_input
            )

            # ------------------------------------------------
            # Save assistant message
            # ------------------------------------------------

            messages.append({
                "role": "assistant",
                "content": result,
                "pages": pages,
                "time": elapsed,
            })

            save_messages(messages)

            # ------------------------------------------------
            # AJAX response
            # ------------------------------------------------

            if is_ajax_request():

                return jsonify({
                    "ok": True,
                    "answer": result,
                    "pages": pages,
                    "time": elapsed,
                }), 200

            return redirect(
                url_for("index")
            )

        except Exception as exc:

            traceback.print_exc()

            save_messages(messages)

            error_msg = (
                "ClaraMed could not generate the answer. "
                f"{exc}"
            )

            if is_ajax_request():

                return jsonify({
                    "ok": False,
                    "error": error_msg,
                }), 500

            return render_template(
                "index.html",
                messages=get_messages(),
                error=error_msg,
            )

    # ========================================================
    # GET
    # ========================================================

    return render_template(
        "index.html",
        messages=get_messages(),
    )


# ============================================================
# Streaming SSE Endpoint
# ============================================================

@app.route(
    "/stream",
    methods=["POST"],
)
def stream():

    """
    Stream the completed ClaraMed answer using SSE.

    IMPORTANT:

    The previous version accessed Flask `session` inside the
    generator. The generator executes after the normal Flask
    request processing has started returning the response.

    That caused:

        RuntimeError:
        Working outside of request context.

    This version performs ALL AI + session work BEFORE the
    generator starts.

    The generator only sends already-created text chunks.
    It never accesses Flask request/session objects.
    """

    user_input = request.form.get(
        "prompt",
        "",
    ).strip()

    is_regenerate = (
        request.form.get(
            "regenerate",
            "0",
        ) == "1"
    )

    # --------------------------------------------------------
    # Validate input
    # --------------------------------------------------------

    if not user_input:

        return jsonify({
            "ok": False,
            "error": "Please enter a medical question.",
        }), 400

    # --------------------------------------------------------
    # Run AI BEFORE creating the stream
    # --------------------------------------------------------

    try:

        result, pages, elapsed = run_ai(
            user_input
        )

        # ----------------------------------------------------
        # Save conversation while request context is active
        # ----------------------------------------------------

        messages = get_messages()

        if is_regenerate:

            # Remove the previous assistant answer
            if (
                messages
                and messages[-1].get("role")
                == "assistant"
            ):
                messages.pop()

            # Do not duplicate the user question
            if not (
                messages
                and messages[-1].get("role")
                == "user"
                and messages[-1].get("content")
                == user_input
            ):

                messages.append({
                    "role": "user",
                    "content": user_input,
                })

        else:

            # Normal new question
            messages.append({
                "role": "user",
                "content": user_input,
            })

        # Save final assistant answer
        messages.append({
            "role": "assistant",
            "content": result,
            "pages": pages,
            "time": elapsed,
        })

        save_messages(messages)

    except Exception as exc:

        traceback.print_exc()

        error_msg = (
            "ClaraMed could not generate the answer. "
            f"{exc}"
        )

        error_payload = (
            "data: "
            + json.dumps(
                {
                    "type": "error",
                    "content": error_msg,
                },
                ensure_ascii=False,
            )
            + "\n\n"
        )

        done_payload = "data: [DONE]\n\n"

        return Response(
            error_payload + done_payload,
            mimetype="text/event-stream",
            headers={
                "Cache-Control":
                    "no-cache, no-store, must-revalidate",
                "X-Accel-Buffering":
                    "no",
                "Connection":
                    "keep-alive",
            },
        )

    # --------------------------------------------------------
    # SSE Generator
    # --------------------------------------------------------

    def generate():

        # IMPORTANT:
        # No Flask session/request access here.

        chunk_size = 28

        for start in range(
            0,
            len(result),
            chunk_size,
        ):

            chunk = result[
                start:
                start + chunk_size
            ]

            yield (
                "data: "
                + json.dumps(
                    {
                        "type": "token",
                        "content": chunk,
                    },
                    ensure_ascii=False,
                )
                + "\n\n"
            )

        # Metadata
        yield (
            "data: "
            + json.dumps(
                {
                    "type": "meta",
                    "pages": pages,
                    "time": elapsed,
                },
                ensure_ascii=False,
            )
            + "\n\n"
        )

        # Stream complete
        yield "data: [DONE]\n\n"

    # --------------------------------------------------------
    # Return SSE response
    # --------------------------------------------------------

    return Response(
        generate(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control":
                "no-cache, no-store, must-revalidate",
            "X-Accel-Buffering":
                "no",
            "Connection":
                "keep-alive",
        },
    )


# ============================================================
# Clear Chat
# ============================================================

@app.route("/clear")
def clear():

    session.pop(
        "messages",
        None,
    )

    session.modified = True

    return redirect(
        url_for("index")
    )


# ============================================================
# Favicon
# ============================================================

@app.route("/favicon.ico")
def favicon():
    return "", 204


# ============================================================
# Warm Up
# ============================================================

def warm_up():

    print()
    print("=" * 60)
    print("        ClaraMed AI Medical Assistant")
    print("=" * 60)

    print(
        "Preloading AI components..."
    )

    start = time.perf_counter()

    chain = create_qa_chain()

    elapsed = round(
        time.perf_counter()
        - start,
        2,
    )

    if chain is not None:

        print(
            f"[OK] AI pipeline ready in {elapsed}s"
        )

    else:

        print(
            "[FAIL] AI pipeline could not be loaded."
        )

        print(
            "Check GROQ_API_KEY, dependencies "
            "and vectorstore/db_faiss."
        )

    print("=" * 60)
    print()


# ============================================================
# Run
# ============================================================

if __name__ == "__main__":

    warm_up()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
        use_reloader=False,
    )