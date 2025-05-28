// chat.js
async function loadMessages(contact = "919746574552") {
  try {
    const response = await fetch(
      `/api/method/whatsapp_manager.api.chat.get_messages?contact=${contact}`
    );
    const data = await response.json();
    console.log("API Response:", data); // Debug log
    displayMessages(data.message || data); // Handle different response formats
  } catch (error) {
    console.error("Error loading messages:", error);
  }
}

function displayMessages(messages) {
  const container = document.getElementById("chat-container");
  if (!container) return;

  container.innerHTML = "";

  // Handle if messages is an array directly or nested in an object
  const messageArray = Array.isArray(messages)
    ? messages
    : messages.messages || [];

  messageArray.forEach((message) => {
    const messageElement = document.createElement("div");
    messageElement.className = `message ${message.direction.toLowerCase()}`;
    messageElement.innerHTML = `
            <div class="message-content">
                <strong>${message.contact}</strong> 
                <span class="direction">(${message.direction})</span>
                <br>
                ${message.content}
                <br>
                <small>${message.timestamp}</small>
                <span class="status">${message.status}</span>
            </div>
        `;
    container.appendChild(messageElement);
  });
}

// Call when page loads
window.onload = loadMessages;

// Auto-refresh every 10 seconds
setInterval(loadMessages, 10000);
