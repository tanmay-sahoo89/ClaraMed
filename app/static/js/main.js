/* ============================================================
   ClaraMed — main.js
   Place at: app/static/js/main.js
   ============================================================ */

(function () {
  "use strict";

  /* ── DOM refs ─────────────────────────────────────────── */
  const form        = document.getElementById("chat-form");
  const textarea    = document.getElementById("prompt-input");
  const sendBtn     = document.getElementById("btn-send");
  const chatWindow  = document.getElementById("chat-window");
  const typingRow   = document.getElementById("typing-row");
  const heroSection = document.getElementById("hero-section");

  /* ── Auto-resize textarea ─────────────────────────────── */
  function resizeTextarea() {
    if (!textarea) return;
    textarea.style.height = "auto";
    textarea.style.height = Math.min(textarea.scrollHeight, 160) + "px";
  }

  if (textarea) {
    textarea.addEventListener("input", resizeTextarea);

    /* Enter = send, Shift+Enter = newline */
    textarea.addEventListener("keydown", function (e) {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        if (textarea.value.trim()) {
          form.dispatchEvent(new Event("submit", { cancelable: true }));
        }
      }
    });
  }

  /* ── Fill from suggestion chip ───────────────────────── */
  window.fillPrompt = function (text) {
    if (!textarea) return;
    textarea.value = text;
    textarea.focus();
    resizeTextarea();
  };

  /* ── Scroll chat to bottom ────────────────────────────── */
  function scrollToBottom(smooth) {
    if (!chatWindow) return;
    chatWindow.scrollTo({
      top: chatWindow.scrollHeight,
      behavior: smooth ? "smooth" : "instant",
    });
  }

  /* ── Show / hide typing dots ──────────────────────────── */
  function showTyping(on) {
    if (!typingRow) return;
    if (on) {
      typingRow.classList.add("visible");
      scrollToBottom(true);
    } else {
      typingRow.classList.remove("visible");
    }
  }

  /* ── Append a message bubble to the DOM ──────────────── */
  function appendMessage(role, content) {
    if (!chatWindow) return;

    /* Hide hero on first message */
    if (heroSection) {
      heroSection.style.display = "none";
    }

    const row = document.createElement("div");
    row.className = "msg-row " + role;

    const avatar = document.createElement("div");
    avatar.className = "msg-avatar";
    avatar.textContent = role === "user" ? "You" : "CM";

    const bubble = document.createElement("div");
    bubble.className = "msg-bubble";

    if (role === "assistant") {
      const label = document.createElement("span");
      label.className = "msg-label";
      label.textContent = "ClaraMed";
      bubble.appendChild(label);
    }

    const text = document.createElement("span");
    /* nl2br: replace \n with <br> */
    text.innerHTML = escapeHtml(content).replace(/\n/g, "<br>");
    bubble.appendChild(text);

    row.appendChild(avatar);
    row.appendChild(bubble);

    /* Insert before typing indicator */
    chatWindow.insertBefore(row, typingRow);
    scrollToBottom(true);
  }

  /* Simple HTML escape to prevent XSS */
  function escapeHtml(str) {
    return str
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  /* ── Form submit — AJAX POST ──────────────────────────── */
  if (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();

      const query = textarea ? textarea.value.trim() : "";
      if (!query) return;

      /* Immediately show user message */
      appendMessage("user", query);

      /* Clear input */
      if (textarea) {
        textarea.value = "";
        textarea.style.height = "auto";
      }

      /* Disable send while waiting */
      if (sendBtn) sendBtn.disabled = true;
      showTyping(true);

      /* Send to Flask */
      fetch(form.action, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: "prompt=" + encodeURIComponent(query),
      })
        .then(function (res) {
          if (!res.ok) throw new Error("Server returned " + res.status);
          /* Flask returns a redirect; follow it and parse the refreshed page
             to extract the last assistant message from the updated session. */
          return res.text();
        })
        .then(function (html) {
          showTyping(false);
          if (sendBtn) sendBtn.disabled = false;

          /* Parse the returned HTML and grab the last assistant bubble */
          const parser = new DOMParser();
          const doc = parser.parseFromString(html, "text/html");
          const bubbles = doc.querySelectorAll(".msg-row.assistant .msg-bubble");

          if (bubbles.length > 0) {
            const last = bubbles[bubbles.length - 1];
            /* Get the text node, skip the .msg-label */
            const label = last.querySelector(".msg-label");
            if (label) label.remove();
            const rawContent = last.innerHTML
              .replace(/<br\s*\/?>/gi, "\n")
              .replace(/<[^>]+>/g, "")
              .trim();
            appendMessage("assistant", rawContent);
          }
        })
        .catch(function (err) {
          showTyping(false);
          if (sendBtn) sendBtn.disabled = false;
          appendMessage(
            "assistant",
            "Something went wrong. Please check your connection and try again."
          );
          console.error("ClaraMed fetch error:", err);
        });
    });
  }

  /* ── On page load: scroll to bottom ──────────────────── */
  window.addEventListener("DOMContentLoaded", function () {
    scrollToBottom(false);

    /* Focus textarea on desktop */
    if (textarea && window.innerWidth > 600) {
      textarea.focus();
    }
  });
})();
