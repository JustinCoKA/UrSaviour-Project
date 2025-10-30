// js/chatbot.js
document.addEventListener("DOMContentLoaded", () => {
  const chatInput = document.getElementById("Input-AI");
  const sendButton = document.querySelector(".chat-send-button");
  const chatContainer = document.querySelector(".chat-container");

  if (!chatInput || !sendButton || !chatContainer) {
    console.warn("[Chat] Required elements not found; skipping init.");
    return;
  }

  // Decide backend base URL (local dev vs prod)
  const isLocal = ["localhost", "127.0.0.1", ""].includes(window.location.hostname) || window.location.protocol === "file:";
  const API_BASE = isLocal ? "http://127.0.0.1:8000" : ""; // use same-origin in prod

  // Create box to show messages above the input row
  const chatBox = document.createElement("div");
  chatBox.className = "chat-box";
  chatBox.style.display = "flex";
  chatBox.style.flexDirection = "column";
  chatBox.style.marginBottom = "5px";
  chatBox.style.maxHeight = "60vh";
  chatBox.style.overflowY = "auto";
  // Insert the chat messages container BEFORE the input row
  chatContainer.parentNode.insertBefore(chatBox, chatContainer);

  // Append messages
  function appendMessage(sender, message) {
    const msg = document.createElement("div");
    msg.className = `chat-message ${sender}`;
    // Styling is handled via CSS classes in Chat-page.html

    msg.textContent = message;
    chatBox.appendChild(msg);
    chatBox.scrollTop = chatBox.scrollHeight;
  }

  async function sendMessage() {
    const userInput = chatInput.value.trim();
    if (!userInput) return;

    appendMessage("user", userInput);
    chatInput.value = "";

    // Loading placeholder
    appendMessage("bot", "Thinking...");

    try {
      const response = await fetch(`${API_BASE}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userInput }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      const botReply = data.answer || data.reply || data.message || "Sorry, I couldn’t understand that.";

      // Remove the "Thinking..." message
      if (chatBox.lastChild) chatBox.lastChild.remove();
      appendMessage("bot", botReply);
    } catch (error) {
      if (chatBox.lastChild) chatBox.lastChild.remove();
      appendMessage("bot", "⚠️ Connection error. Please check your backend.");
      console.error("[Chat] error:", error);
    }
  }

  sendButton.addEventListener("click", sendMessage);
  chatInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });
});
