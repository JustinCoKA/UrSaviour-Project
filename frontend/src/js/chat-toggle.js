function initChatToggle() {
  const toggleButton = document.getElementById("chat-toggle");
  const chatBox = document.getElementById("chat-box");

  if (toggleButton && chatBox) {
    toggleButton.addEventListener("click", function () {
      chatBox.style.display = chatBox.style.display === "block" ? "none" : "block";
    });
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const observer = new MutationObserver((mutations, obs) => {
    const toggleButton = document.getElementById("chat-toggle");
    const chatBox = document.getElementById("chat-box");
    if (toggleButton && chatBox) {
      initChatToggle();
      obs.disconnect(); // Stop observing once the elements are found
    }
  });

  observer.observe(document.body, {
    childList: true,
    subtree: true
  });
});
