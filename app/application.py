from dotenv import load_dotenv
load_dotenv()

from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from app.components.retriever import create_qa_chain
import os

app = Flask(__name__)

app.secret_key = os.environ.get("FLASK_SECRET_KEY", "a-fixed-demo-key-change-later")

from markupsafe import Markup

def nl2br(value):
    return Markup(value.replace("\n", "<br>\n"))

app.jinja_env.filters['nl2br'] = nl2br

def extract_pages(source_documents):
    pages = []
    for doc in source_documents or []:
        page = doc.metadata.get("page")
        if page is not None and (page + 1) not in pages:
            pages.append(page + 1)
    return sorted(pages)

@app.route("/", methods=["GET", "POST"])
def index():
    if "messages" not in session:
        session["messages"] = []

    if request.method == "POST":
        user_input = request.form.get("prompt")
        is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

        if user_input:
            messages = session['messages']

            messages.append({"role": "user", "content": user_input})
            session["messages"] = messages

            try:
                qa_chain = create_qa_chain()
                if qa_chain is None:
                    raise Exception("QA CHAIN could not be created (llm or vectorstore issue)")

                response = qa_chain.invoke({"query": user_input})

                result = response.get("result", "No response")
                pages = extract_pages(response.get("source_documents"))

                messages.append({"role": "assistant", "content": result, "pages": pages})
                session["messages"] = messages

                if is_ajax:
                    return jsonify({"ok": True, "answer": result, "pages": pages})

            except Exception as e:
                error_msg = f"Error : {str(e)}"

                if is_ajax:
                    return jsonify({"ok": False, "error": error_msg})

                return render_template(
                    "index.html",
                    messages=session["messages"],
                    error=error_msg
                )

        return redirect(url_for("index"))
    return render_template("index.html", messages=session.get("messages", []))

@app.route("/clear")
def clear():
    session.pop("messages", None)
    return redirect(url_for("index"))

@app.route("/favicon.ico")
def favicon():
    return "", 204

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
        use_reloader=False
    )