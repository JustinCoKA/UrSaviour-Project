// js/chatbot.js (enhanced with typing indicator, tone selection, agent status, typewriter effect)
document.addEventListener("DOMContentLoaded", () => {
  const chatInput = document.getElementById("Input-AI");
  const sendButton = document.querySelector(".chat-send-button");
  const chatContainer = document.querySelector(".chat-container");
  const agentStatus = document.getElementById("agentStatus");
  const statusDot = document.querySelector(".status-dot");

  if (!chatInput || !sendButton || !chatContainer) {
    console.warn("[Chat] Required elements not found; skipping init.");
    return;
  }

  const isLocal = ["localhost", "127.0.0.1", ""].includes(window.location.hostname) || window.location.protocol === "file:";
  const API_BASE = isLocal ? "http://127.0.0.1:8000" : ""; // same-origin in prod

  const chatBox = document.createElement("div");
  chatBox.className = "chat-box";
  chatBox.style.display = "flex";
  chatBox.style.flexDirection = "column";
  chatBox.style.marginBottom = "5px";
  chatBox.style.maxHeight = "60vh";
  chatBox.style.overflowY = "auto";
  chatContainer.parentNode.insertBefore(chatBox, chatContainer);

  function appendMessage(sender, text, progressive=false){
    const msg = document.createElement("div");
    msg.className = `chat-message ${sender}`;
    if(!progressive){
      msg.textContent = text;
    } else {
      typewriter(msg, text);
    }
    chatBox.appendChild(msg);
    chatBox.scrollTop = chatBox.scrollHeight;
  }

  function typewriter(el, full){
    let i=0; const total = full.length;
    const step = Math.max(1, Math.ceil(total/180)); // adaptive pacing
    function tick(){
      el.textContent = full.slice(0,i);
      i += step;
      if(i <= total){
        chatBox.scrollTop = chatBox.scrollHeight;
        requestAnimationFrame(tick);
      } else {
        el.textContent = full;
      }
    }
    tick();
  }

  function showTyping(){
    if(document.getElementById("typingIndicatorDynamic")) return;
    const ind = document.createElement("div");
    ind.className = "typing-indicator";
    ind.id = "typingIndicatorDynamic";
    ind.innerHTML = "<span></span><span></span><span></span>";
    chatBox.appendChild(ind);
    chatBox.scrollTop = chatBox.scrollHeight;
  }

  function removeTyping(){
    const ind = document.getElementById("typingIndicatorDynamic");
    if(ind) ind.remove();
  }

  function setBusy(){
    if(agentStatus) agentStatus.textContent = "Thinking…";
    if(statusDot) statusDot.classList.add("busy");
  }
  function clearBusy(){
    if(agentStatus) agentStatus.textContent = "Online";
    if(statusDot) statusDot.classList.remove("busy");
  }

  // Initial greeting
  appendMessage("bot", "Hi, welcome to our Saviour grocery assistant! How can I help you today?");

  async function sendMessage(){
    const userInput = chatInput.value.trim();
    if(!userInput) return;
    appendMessage("user", userInput);
    chatInput.value = "";
    setBusy();
    showTyping();

    try{
      const response = await fetch(`${API_BASE}/chat`, {
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body: JSON.stringify({ message: userInput })
      });
      if(!response.ok){ throw new Error(`HTTP ${response.status}`); }
      const data = await response.json();
      removeTyping();
      clearBusy();
      const botReply = data.answer || data.reply || data.message || "Sorry, I couldn’t understand that.";
      appendMessage("bot", botReply, true);
    } catch(err){
      console.error("[Chat] error:", err);
      removeTyping();
      clearBusy();
      appendMessage("bot", "⚠️ Connection error. Please check your backend.");
    }
  }

  sendButton.addEventListener("click", sendMessage);
  chatInput.addEventListener("keydown", e => {
    if(e.key === "Enter" && !e.shiftKey){
      e.preventDefault();
      sendMessage();
    }
  });
});

// Theme toggle (icon-only) -> affects page background only
const themeToggle = document.getElementById("themeToggle");
if (themeToggle) {
  const updateIcon = () => {
    const dark = document.documentElement.classList.contains("dark-mode");
    themeToggle.textContent = dark ? "☀️" : "🌙";
    themeToggle.setAttribute('aria-pressed', String(dark));
    themeToggle.setAttribute('title', dark ? 'Switch to light mode' : 'Switch to dark mode');
  };
  themeToggle.addEventListener("click", () => {
    document.documentElement.classList.toggle("dark-mode");
    document.body.classList.toggle("dark-mode"); // maintain compatibility if body styles rely on it
    updateIcon();
  });
  updateIcon();
}
