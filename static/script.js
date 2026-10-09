/**
 * script.js
 * =========
 * Frontend client logic for NovaMart AI FAQ Chatbot.
 * Handles DOM interactions, message rendering, suggestion chips,
 * and asynchronous fetch() communication with the Flask /ask backend.
 */

document.addEventListener("DOMContentLoaded", () => {
  // --- DOM Element References ---
  const chatMessages = document.getElementById("chat-messages");
  const chatForm = document.getElementById("chat-form");
  const userInput = document.getElementById("user-input");
  const sendBtn = document.getElementById("send-btn");
  const typingIndicator = document.getElementById("typing-indicator");
  const clearBtn = document.getElementById("clear-btn");
  const suggestedChips = document.getElementById("suggested-chips");

  // --- Helper: Format Current Time ---
  function getCurrentTime() {
    const now = new Date();
    return now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  }

  // --- Helper: Scroll Chat to Bottom ---
  function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  // --- Helper: Create SVG Bot Icon ---
  function getBotIconSVG() {
    return `
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <rect x="3" y="11" width="18" height="10" rx="3"></rect>
        <circle cx="12" cy="5" r="2"></circle>
        <path d="M12 7v4"></path>
      </svg>
    `;
  }

  // --- Append a User Message Bubble ---
  function appendUserMessage(text) {
    const msgDiv = document.createElement("div");
    msgDiv.className = "message user-message";

    const contentDiv = document.createElement("div");
    contentDiv.className = "message-content";

    const bubbleDiv = document.createElement("div");
    bubbleDiv.className = "message-bubble";
    bubbleDiv.textContent = text;

    const timeSpan = document.createElement("span");
    timeSpan.className = "message-time";
    timeSpan.textContent = getCurrentTime();

    contentDiv.appendChild(bubbleDiv);
    contentDiv.appendChild(timeSpan);
    msgDiv.appendChild(contentDiv);

    // Insert before typing indicator
    chatMessages.insertBefore(msgDiv, typingIndicator);
    scrollToBottom();
  }

  // --- Append a Bot Message Bubble ---
  function appendBotMessage(answer, matchedQuestion = null, confidence = 0.0) {
    const msgDiv = document.createElement("div");
    msgDiv.className = "message bot-message";

    const avatarDiv = document.createElement("div");
    avatarDiv.className = "avatar-small";
    avatarDiv.innerHTML = getBotIconSVG();

    const contentDiv = document.createElement("div");
    contentDiv.className = "message-content";

    const bubbleDiv = document.createElement("div");
    bubbleDiv.className = "message-bubble";

    const textP = document.createElement("p");
    textP.textContent = answer;
    bubbleDiv.appendChild(textP);

    // If there is match information, render a badge to showcase the NLP model
    if (matchedQuestion && confidence >= 0.3) {
      const tagDiv = document.createElement("div");
      tagDiv.className = "match-info-tag matched";
      const confidencePercent = Math.round(confidence * 100);
      tagDiv.innerHTML = `🎯 <strong>Matched:</strong> &ldquo;${escapeHTML(matchedQuestion)}&rdquo; &bull; <strong>${confidencePercent}% confidence</strong>`;
      bubbleDiv.appendChild(tagDiv);
    } else if (confidence > 0 && confidence < 0.3) {
      const tagDiv = document.createElement("div");
      tagDiv.className = "match-info-tag fallback";
      tagDiv.innerHTML = `⚠️ <strong>Low Confidence:</strong> ${Math.round(confidence * 100)}% (Fallback triggered)`;
      bubbleDiv.appendChild(tagDiv);
    }

    const timeSpan = document.createElement("span");
    timeSpan.className = "message-time";
    timeSpan.textContent = getCurrentTime();

    contentDiv.appendChild(bubbleDiv);
    contentDiv.appendChild(timeSpan);

    msgDiv.appendChild(avatarDiv);
    msgDiv.appendChild(contentDiv);

    // Insert before typing indicator
    chatMessages.insertBefore(msgDiv, typingIndicator);
    scrollToBottom();
  }

  // --- Helper to escape HTML in matched questions for security ---
  function escapeHTML(str) {
    const div = document.createElement("div");
    div.innerText = str;
    return div.innerHTML;
  }

  // --- Toggle Typing Indicator ---
  function showTypingIndicator(show) {
    typingIndicator.style.display = show ? "flex" : "none";
    if (show) {
      scrollToBottom();
    }
  }

  // --- Send Question to Backend API ---
  async function handleSendQuestion(questionText) {
    const trimmed = (questionText || userInput.value).trim();
    if (!trimmed) return;

    // Display user's question in chat
    appendUserMessage(trimmed);

    // Clear input field and disable UI while bot responds
    userInput.value = "";
    userInput.disabled = true;
    sendBtn.disabled = true;
    showTypingIndicator(true);

    try {
      // POST request to Flask backend
      const response = await fetch("/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ question: trimmed })
      });

      const data = await response.json();

      // Artificial short delay (400ms) for natural conversational feel
      await new Promise((resolve) => setTimeout(resolve, 350));

      showTypingIndicator(false);

      if (response.ok) {
        appendBotMessage(data.answer, data.matched_question, data.confidence);
      } else {
        appendBotMessage(
          data.answer || "Sorry, an error occurred while processing your request.",
          null,
          0.0
        );
      }
    } catch (error) {
      console.error("Fetch error:", error);
      showTypingIndicator(false);
      appendBotMessage(
        "Sorry, I cannot connect to the backend server right now. Please ensure 'python app.py' is running.",
        null,
        0.0
      );
    } finally {
      // Re-enable input and refocus
      userInput.disabled = false;
      sendBtn.disabled = false;
      userInput.focus();
      scrollToBottom();
    }
  }

  // --- Form Submit Event (Enter key or Send button) ---
  chatForm.addEventListener("submit", (e) => {
    e.preventDefault();
    handleSendQuestion();
  });

  // --- Clickable Suggested Question Chips ---
  if (suggestedChips) {
    suggestedChips.addEventListener("click", (e) => {
      const chip = e.target.closest(".chip");
      if (chip) {
        const question = chip.getAttribute("data-question");
        if (question) {
          handleSendQuestion(question);
        }
      }
    });
  }

  // --- Clear Chat History ---
  clearBtn.addEventListener("click", () => {
    // Keep only the welcome message, chips, and typing indicator
    const allMessages = chatMessages.querySelectorAll(".message");
    allMessages.forEach((msg) => {
      if (msg.id !== "welcome-message") {
        msg.remove();
      }
    });
    userInput.value = "";
    userInput.focus();
    scrollToBottom();
  });

  // Focus input automatically on initial load
  userInput.focus();
});
