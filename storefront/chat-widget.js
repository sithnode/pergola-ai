(function () {
  var AGENT_URL = window.AGENT_URL || "http://localhost:8000";
  var conversationHistory = [];
  var isOpen = false;

  // ── Styles ──────────────────────────────────────────────────────────────────
  var style = document.createElement("style");
  style.textContent = [
    "#pp-btn{position:fixed;bottom:24px;right:24px;width:60px;height:60px;border-radius:50%;background:#92400e;color:#fff;border:none;cursor:pointer;box-shadow:0 4px 16px rgba(0,0,0,.3);font-size:26px;z-index:9999;transition:transform .2s;}",
    "#pp-btn:hover{transform:scale(1.08);}",
    "#pp-win{position:fixed;bottom:96px;right:24px;width:360px;height:520px;background:#fff;border-radius:16px;box-shadow:0 8px 32px rgba(0,0,0,.18);display:none;flex-direction:column;z-index:9998;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;overflow:hidden;}",
    "#pp-win.open{display:flex;}",
    "#pp-hdr{background:#92400e;color:#fff;padding:14px 16px;display:flex;align-items:center;gap:10px;}",
    "#pp-hdr .av{width:38px;height:38px;background:#fef3c7;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:20px;flex-shrink:0;}",
    "#pp-hdr h4{margin:0;font-size:14px;font-weight:600;}",
    "#pp-hdr p{margin:2px 0 0;font-size:11px;opacity:.8;}",
    "#pp-msgs{flex:1;overflow-y:auto;padding:14px;display:flex;flex-direction:column;gap:10px;background:#fafafa;}",
    ".pp-m{max-width:82%;padding:10px 14px;border-radius:12px;font-size:13px;line-height:1.55;word-break:break-word;}",
    ".pp-m.u{background:#92400e;color:#fff;align-self:flex-end;border-radius:12px 12px 2px 12px;}",
    ".pp-m.a{background:#fff;color:#1f2937;align-self:flex-start;border-radius:12px 12px 12px 2px;box-shadow:0 1px 3px rgba(0,0,0,.08);}",
    ".pp-m.t{opacity:.55;font-style:italic;}",
    "#pp-inp{display:flex;padding:10px;border-top:1px solid #e5e7eb;gap:8px;background:#fff;}",
    "#pp-inp input{flex:1;border:1px solid #e5e7eb;border-radius:20px;padding:9px 14px;font-size:13px;outline:none;transition:border .15s;}",
    "#pp-inp input:focus{border-color:#92400e;}",
    "#pp-inp button{background:#92400e;color:#fff;border:none;border-radius:50%;width:36px;height:36px;cursor:pointer;font-size:17px;flex-shrink:0;transition:background .15s;}",
    "#pp-inp button:hover{background:#78350f;}",
    "#pp-inp button:disabled{opacity:.5;cursor:default;}",
  ].join("");
  document.head.appendChild(style);

  // ── DOM ─────────────────────────────────────────────────────────────────────
  var btn = document.createElement("button");
  btn.id = "pp-btn";
  btn.title = "Chat with our AI advisor";
  btn.textContent = "💬";

  var win = document.createElement("div");
  win.id = "pp-win";
  win.innerHTML =
    '<div id="pp-hdr"><div class="av">🌿</div><div><h4>Alex — Pergola Advisor</h4><p>AI-powered · replies instantly</p></div></div>' +
    '<div id="pp-msgs"></div>' +
    '<div id="pp-inp"><input id="pp-txt" type="text" placeholder="Ask about pergolas, sizes, prices…" autocomplete="off"><button id="pp-snd">↑</button></div>';

  document.body.appendChild(btn);
  document.body.appendChild(win);

  var msgs = document.getElementById("pp-msgs");
  var txt = document.getElementById("pp-txt");
  var snd = document.getElementById("pp-snd");

  // ── Helpers ──────────────────────────────────────────────────────────────────
  function addMsg(text, role) {
    var d = document.createElement("div");
    d.className = "pp-m " + role;
    d.textContent = text;
    msgs.appendChild(d);
    msgs.scrollTop = msgs.scrollHeight;
    return d;
  }

  function setLoading(loading) {
    txt.disabled = loading;
    snd.disabled = loading;
    if (!loading) txt.focus();
  }

  async function send(text) {
    text = text.trim();
    if (!text) return;
    txt.value = "";
    setLoading(true);
    addMsg(text, "u");
    var typing = addMsg("Typing…", "a t");

    try {
      var res = await fetch(AGENT_URL + "/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text, conversation_history: conversationHistory }),
      });
      if (!res.ok) throw new Error("HTTP " + res.status);
      var data = await res.json();
      conversationHistory = data.conversation_history;
      typing.remove();
      addMsg(data.response, "a");
    } catch (e) {
      typing.textContent = "Sorry, I couldn't connect. Please try again.";
      typing.classList.remove("t");
    } finally {
      setLoading(false);
    }
  }

  function welcome() {
    if (msgs.children.length === 0) {
      addMsg(
        "Hi! I'm Alex, your pergola advisor. I can help you find the perfect pergola, check availability, and give you a quote. What can I help you with?",
        "a"
      );
    }
  }

  // ── Events ───────────────────────────────────────────────────────────────────
  btn.addEventListener("click", function () {
    isOpen = !isOpen;
    win.classList.toggle("open", isOpen);
    btn.textContent = isOpen ? "✕" : "💬";
    if (isOpen) { welcome(); txt.focus(); }
  });

  snd.addEventListener("click", function () { send(txt.value); });
  txt.addEventListener("keypress", function (e) { if (e.key === "Enter") send(txt.value); });

  // ── Global API (called from product buttons) ─────────────────────────────────
  window.openChat = function (initialMessage) {
    if (!isOpen) {
      isOpen = true;
      win.classList.add("open");
      btn.textContent = "✕";
      welcome();
    }
    if (initialMessage) {
      txt.value = initialMessage;
      txt.focus();
    }
  };
})();
