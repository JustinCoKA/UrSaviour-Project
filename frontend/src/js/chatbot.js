document.addEventListener("DOMContentLoaded", () => {
    const chatInput = document.getElementById("Input-AI");
    // Prefer the explicit send button (aria-label) to avoid conflicts with other buttons
    const sendButton = document.querySelector('button[aria-label="Send message"]') || document.querySelector(".chat-send-button");
    const chatContainer = document.querySelector(".chat-container");

    if (!chatInput || !sendButton || !chatContainer) return;

    sendButton.addEventListener("click", sendMessage);

    // Send on Enter (without Shift) from the textarea
    chatInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Backend endpoint used by the sample code. Change if your backend is mounted at a different path.
    const backendUrl = "http://localhost:8000/chat";

    async function sendMessage() {
        const userMessage = chatInput.value.trim();
        if (!userMessage) return;

            // Display the user's message in the chat window (with emoji)
            addMessage("user", userMessage);
            chatInput.value = "";

        // Send the user's message to the backend
        try {
            const resp = await fetch(backendUrl, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: userMessage }),
            });

            if (!resp.ok) {
                // Try to parse JSON error body and show a helpful message in the UI
                let errText = `Server returned ${resp.status}`;
                try {
                    const errJson = await resp.json();
                    if (errJson && errJson.detail) errText = String(errJson.detail);
                } catch (e) {
                    // ignore JSON parse errors
                }
                console.error("Server returned", resp.status, errText);
                addMessage("bot", `Server error: ${errText}`);
                return;
            }

            const data = await resp.json();
            if (data && (data.answer || data.reply)) {
                // support both `answer` (your sample) and `reply` (older backend)
                addMessage("bot", data.answer || data.reply);
            } else if (data && data.detail) {
                addMessage("bot", String(data.detail));
            } else {
                addMessage("bot", "Sorry, I didn't understand that.");
            }
        } catch (error) {
            console.error("Error communicating with the backend:", error);
            addMessage("bot", "Unable to connect to the server. Please try again later.");
        }
    }

    function addMessage(sender, text) {
        const messageElement = document.createElement("div");
        messageElement.className = `chat-message ${sender}`;

        // Prefix messages with a simple emoji to match the sample UI
        const prefix = sender === "user" ? "🧍 " : "🤖 ";

        // Use a <pre> to respect line breaks, but keep a simple container to allow styling
        const content = document.createElement("div");
        content.className = "chat-message-content";
        content.textContent = prefix + text;

        messageElement.appendChild(content);

        // Insert messages before the input textarea so input stays at bottom
        const inputEl = chatInput;
        if (inputEl && inputEl.parentNode === chatContainer) {
            chatContainer.insertBefore(messageElement, inputEl);
        } else {
            chatContainer.appendChild(messageElement);
        }

        // Auto-scroll to bottom
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    // Support an optional tone selector (if present on the page)
    const toneSelect = document.getElementById("tone");

    // Ensure sendMessage reads the tone when sending
    async function sendMessage() {
        const userMessage = chatInput.value.trim();
        if (!userMessage) return;

        // Display the user's message
        addMessage("user", userMessage);
        chatInput.value = "";

        // Disable the button while sending
        if (sendButton) {
            sendButton.disabled = true;
            sendButton.setAttribute('aria-busy', 'true');
        }

        const tone = toneSelect ? toneSelect.value : undefined;

        try {
            const resp = await fetch(backendUrl, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: userMessage, ...(tone ? { tone } : {}) }),
            });

            if (!resp.ok) {
                let errText = `Server returned ${resp.status}`;
                try {
                    const errJson = await resp.json();
                    if (errJson && errJson.detail) errText = String(errJson.detail);
                } catch (e) {
                    // ignore
                }
                console.error("Server returned", resp.status, errText);
                addMessage("bot", `Server error: ${errText}`);
                return;
            }

            const data = await resp.json();
            if (data && (data.answer || data.reply)) {
                addMessage("bot", data.answer || data.reply);
            } else if (data && data.detail) {
                addMessage("bot", String(data.detail));
            } else {
                addMessage("bot", "Sorry, I didn't understand that.");
            }
        } catch (error) {
            console.error("Error communicating with the backend:", error);
            addMessage("bot", "Unable to connect to the server. Please try again later.");
        } finally {
            if (sendButton) {
                sendButton.disabled = false;
                sendButton.removeAttribute('aria-busy');
            }
        }
    }
});