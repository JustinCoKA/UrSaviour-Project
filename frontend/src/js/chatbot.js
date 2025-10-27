document.addEventListener("DOMContentLoaded", () => {
    const chatInput = document.getElementById("Input-AI");
    const sendButton = document.querySelector(".chat-send-button");
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

    const backendUrl = "http://127.0.0.1:8000/api/chat"; // use absolute backend URL so frontend dev server (8080) proxies correctly

    async function sendMessage() {
        const userMessage = chatInput.value.trim();
        if (!userMessage) return;

        // Display the user's message in the chat window
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
            if (data && data.reply) {
                addMessage("bot", data.reply);
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
        // Respect line breaks from the server/user
        messageElement.textContent = text;

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
});