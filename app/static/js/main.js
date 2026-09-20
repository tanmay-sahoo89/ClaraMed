/* ============================================================
   ClaraMed — Frontend Controller
   Fixed SSE + Request Handling + Regenerate
   ============================================================ */

(function () {
  "use strict";

  /* ========================================================
       DOM REFERENCES
       ======================================================== */

  const form = document.getElementById("chat-form");

  const textarea = document.getElementById("prompt-input");

  const sendBtn = document.getElementById("btn-send");

  const chatWindow = document.getElementById("chat-window");

  const typingRow = document.getElementById("typing-row");

  const heroSection = document.getElementById("hero-section");

  const overlay = document.getElementById("loading-overlay");

  const loadingText = document.getElementById("loading-text");

  const charCounter = document.getElementById("char-counter");

  /* ========================================================
       STATE
       ======================================================== */

  let isGenerating = false;

  let lastUserQuery = "";

  let phraseInterval = null;

  /* ========================================================
       LOADING PHRASES
       ======================================================== */

  const loadingPhrases = [
    "Analyzing medical literature...",

    "Searching Gale Encyclopedia...",

    "Cross-referencing sources...",

    "Preparing your answer...",

    "Reviewing medical context...",
  ];

  function startLoadingPhrases() {
    if (!loadingText) return;

    let index = 0;

    loadingText.textContent = loadingPhrases[0];

    clearInterval(phraseInterval);

    phraseInterval = setInterval(function () {
      index = (index + 1) % loadingPhrases.length;

      loadingText.style.opacity = "0";

      setTimeout(function () {
        loadingText.textContent = loadingPhrases[index];

        loadingText.style.opacity = "1";
      }, 180);
    }, 2500);
  }

  function stopLoadingPhrases() {
    clearInterval(phraseInterval);

    phraseInterval = null;
  }

  function showOverlay(show) {
    if (!overlay) return;

    overlay.classList.toggle("visible", show);

    if (show) startLoadingPhrases();
    else stopLoadingPhrases();
  }

  /* ========================================================
       TYPING INDICATOR
       ======================================================== */

  function showTyping(show) {
    if (!typingRow) return;

    typingRow.classList.toggle("visible", show);

    if (show) scrollToBottom(true);
  }

  /* ========================================================
       TEXTAREA
       ======================================================== */

  function resizeTextarea() {
    if (!textarea) return;

    textarea.style.height = "auto";

    textarea.style.height = Math.min(textarea.scrollHeight, 160) + "px";
  }

  function updateCharCounter() {
    if (!textarea || !charCounter) return;

    const length = textarea.value.length;

    const max = Number(textarea.getAttribute("maxlength") || 2000);

    charCounter.textContent = length + " / " + max;

    charCounter.classList.toggle(
      "near-limit",
      length > max * 0.85 && length < max,
    );

    charCounter.classList.toggle("at-limit", length >= max);
  }

  /* ========================================================
       SCROLL
       ======================================================== */

  function isNearBottom() {
    if (!chatWindow) return true;

    return (
      chatWindow.scrollHeight - chatWindow.scrollTop - chatWindow.clientHeight <
      120
    );
  }

  function scrollToBottom(smooth) {
    if (!chatWindow) return;

    chatWindow.scrollTo({
      top: chatWindow.scrollHeight,

      behavior: smooth ? "smooth" : "auto",
    });
  }

  /* ========================================================
       CLEAN TEXT
       ======================================================== */

  function cleanText(value) {
    return String(value ?? "")
      .replace(/<br\s*\/?>/gi, "\n")

      .replace(/<\/p\s*>/gi, "\n")

      .replace(/<p\s*>/gi, "")

      .trim();
  }

  /* ========================================================
       APPEND MESSAGE
       ======================================================== */

  function appendMessage(role, content, meta) {
    if (!chatWindow) return null;

    if (heroSection) heroSection.style.display = "none";

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

      label.innerHTML = 'ClaraMed <span class="ai-badge">AI</span>';

      bubble.appendChild(label);
    }

    const text = document.createElement("span");

    text.className = "message-text";

    text.textContent = cleanText(content);

    bubble.appendChild(text);

    if (role === "assistant" && meta) {
      bubble.appendChild(buildToolsBar(content, meta));
    }

    row.appendChild(avatar);

    row.appendChild(bubble);

    chatWindow.insertBefore(row, typingRow);

    scrollToBottom(true);

    return {
      row: row,

      bubble: bubble,

      text: text,
    };
  }

  /* ========================================================
       MESSAGE TOOLS
       ======================================================== */

  function buildToolsBar(content, meta) {
    const tools = document.createElement("div");

    tools.className = "message-tools";

    /* ----------------------------------------------------
           Copy
           ---------------------------------------------------- */

    const copy = document.createElement("button");

    copy.type = "button";

    copy.className = "message-tool";

    copy.innerHTML =
      '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg> Copy';

    copy.addEventListener("click", async function () {
      const bubble = copy.closest(".msg-bubble");

      const value =
        bubble?.querySelector(".message-text")?.textContent ||
        cleanText(content);

      try {
        await navigator.clipboard.writeText(value);

        copy.textContent = "✓ Copied!";

        copy.classList.add("copied");

        setTimeout(function () {
          copy.innerHTML =
            '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg> Copy';

          copy.classList.remove("copied");
        }, 1500);
      } catch (error) {
        console.error("Clipboard error:", error);
      }
    });

    tools.appendChild(copy);

    /* ----------------------------------------------------
           Regenerate
           ---------------------------------------------------- */

    const regen = document.createElement("button");

    regen.type = "button";

    regen.className = "message-tool";

    regen.innerHTML =
      '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg> Regenerate';

    regen.addEventListener("click", function () {
      if (!isGenerating && lastUserQuery) {
        doSend(lastUserQuery, true);
      }
    });

    tools.appendChild(regen);

    /* ----------------------------------------------------
           Source
           ---------------------------------------------------- */

    if (meta && Array.isArray(meta.pages) && meta.pages.length) {
      const source = document.createElement("span");

      source.className = "source-chip";

      source.textContent =
        "📖 Gale Encyclopedia · Pages " + meta.pages.join(", ");

      tools.appendChild(source);
    }

    /* ----------------------------------------------------
           Response time
           ---------------------------------------------------- */

    if (meta && meta.time !== undefined) {
      const time = document.createElement("span");

      time.className = "response-time";

      time.textContent = "⏱ " + meta.time + "s";

      tools.appendChild(time);
    }

    return tools;
  }

  /* ========================================================
       GLOBAL COPY
       ======================================================== */

  window.copyText = async function (button) {
    const value =
      button.closest(".msg-bubble")?.querySelector(".message-text")
        ?.textContent || "";

    try {
      await navigator.clipboard.writeText(value);

      const oldHTML = button.innerHTML;

      button.textContent = "✓ Copied!";

      button.classList.add("copied");

      setTimeout(function () {
        button.innerHTML = oldHTML;

        button.classList.remove("copied");
      }, 1500);
    } catch (error) {
      console.error("Clipboard error:", error);
    }
  };

  /* ========================================================
       GLOBAL REGENERATE
       ======================================================== */

  window.regenerate = function () {
    if (!isGenerating && lastUserQuery) {
      doSend(lastUserQuery, true);
    }
  };

  /* ========================================================
       SUGGESTION CHIPS
       ======================================================== */

  window.fillPrompt = function (text) {
    if (!textarea) return;

    textarea.value = text;

    textarea.focus();

    resizeTextarea();

    updateCharCounter();
  };

  /* ========================================================
       SEND MESSAGE
       ======================================================== */

  async function doSend(query, isRegenerate) {
    if (isGenerating || !query) return;

    isGenerating = true;

    lastUserQuery = query;

    /* ----------------------------------------------------
           Add user bubble only for normal questions
           ---------------------------------------------------- */

    if (!isRegenerate) {
      appendMessage("user", query, null);
    }

    textarea.value = "";

    textarea.style.height = "auto";

    updateCharCounter();

    if (sendBtn) sendBtn.disabled = true;

    showOverlay(true);

    showTyping(true);

    try {
      /* ------------------------------------------------
               Build POST body
               ------------------------------------------------ */

      const body = new URLSearchParams();

      body.set("prompt", query);

      body.set("regenerate", isRegenerate ? "1" : "0");

      /* ------------------------------------------------
               Send request
               ------------------------------------------------ */

      const response = await fetch("/stream", {
        method: "POST",

        headers: {
          "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",

          Accept: "text/event-stream",

          "X-Requested-With": "XMLHttpRequest",
        },

        body: body.toString(),
      });

      /* ------------------------------------------------
               HTTP error
               ------------------------------------------------ */

      if (!response.ok) {
        let message = "Server error " + response.status;

        try {
          const data = await response.json();

          message = data.error || message;
        } catch (_) {}

        throw new Error(message);
      }

      /* ------------------------------------------------
               Verify SSE
               ------------------------------------------------ */

      const contentType = response.headers.get("content-type") || "";

      if (!contentType.includes("text/event-stream")) {
        throw new Error("The server did not return an SSE response.");
      }

      showOverlay(false);

      showTyping(false);

      /* ------------------------------------------------
               Create assistant bubble
               ------------------------------------------------ */

      const refs = appendMessage("assistant", "", null);

      if (!refs) {
        throw new Error("Could not create message bubble.");
      }

      refs.text.classList.add("streaming-cursor");

      /* ------------------------------------------------
               Read SSE stream
               ------------------------------------------------ */

      const reader = response.body.getReader();

      const decoder = new TextDecoder("utf-8");

      let buffer = "";

      let fullText = "";

      let meta = {
        pages: [],

        time: 0,
      };

      let serverError = null;

      while (true) {
        const result = await reader.read();

        if (result.done) break;

        buffer += decoder.decode(result.value, {
          stream: true,
        });

        const lines = buffer.split("\n");

        buffer = lines.pop() || "";

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;

          const payload = line.slice(6).trim();

          if (!payload || payload === "[DONE]") continue;

          try {
            const event = JSON.parse(payload);

            /* ------------------------------------
                           Token
                           ------------------------------------ */

            if (event.type === "token") {
              fullText += event.content || "";

              refs.text.textContent = fullText;

              if (isNearBottom()) {
                scrollToBottom(false);
              }
            } else if (event.type === "meta") {

            /* ------------------------------------
                           Metadata
                           ------------------------------------ */
              meta = {
                pages: Array.isArray(event.pages) ? event.pages : [],

                time: event.time ?? 0,
              };
            } else if (event.type === "error") {

            /* ------------------------------------
                           Server error
                           ------------------------------------ */
              serverError =
                event.content || "The server could not generate an answer.";
            }
          } catch (error) {
            console.warn("Ignored malformed SSE event:", error);
          }
        }
      }

      /* ------------------------------------------------
               Finalize response
               ------------------------------------------------ */

      refs.text.classList.remove("streaming-cursor");

      if (serverError) {
        refs.text.textContent = serverError;
      } else {
        refs.text.textContent = cleanText(fullText);

        refs.bubble.appendChild(buildToolsBar(fullText, meta));
      }

      scrollToBottom(true);
    } catch (error) {
      showOverlay(false);

      showTyping(false);

      appendMessage(
        "assistant",

        "ClaraMed could not generate the answer.\n" + error.message,

        {
          pages: [],

          time: 0,
        },
      );

      console.error("ClaraMed error:", error);
    } finally {
      showOverlay(false);

      showTyping(false);

      isGenerating = false;

      if (sendBtn) sendBtn.disabled = false;

      if (textarea) textarea.focus();
    }
  }

  /* ========================================================
       TEXTAREA EVENTS
       ======================================================== */

  if (textarea) {
    textarea.addEventListener("input", function () {
      resizeTextarea();

      updateCharCounter();
    });

    textarea.addEventListener("keydown", function (event) {
      if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();

        if (textarea.value.trim() && !isGenerating) {
          form?.dispatchEvent(
            new Event("submit", {
              cancelable: true,
            }),
          );
        }
      }
    });
  }

  /* ========================================================
       FORM SUBMIT
       ======================================================== */

  if (form) {
    form.addEventListener("submit", function (event) {
      event.preventDefault();

      const query = textarea?.value.trim() || "";

      if (query && !isGenerating) {
        doSend(query, false);
      }
    });
  }

  /* ========================================================
       INITIALIZATION
       ======================================================== */

  window.addEventListener("DOMContentLoaded", function () {
    scrollToBottom(false);

    updateCharCounter();

    const userMessages = document.querySelectorAll(
      ".msg-row.user .message-text",
    );

    if (userMessages.length) {
      lastUserQuery = userMessages[userMessages.length - 1].textContent.trim();
    }

    if (textarea && window.innerWidth > 640) {
      textarea.focus();
    }
  });
})();
