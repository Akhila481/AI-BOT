// DOM elements
const chatBox = document.getElementById('chat-box');
const userInput = document.getElementById('user-input');

// Display welcome message
function displayWelcomeMessage() {
    // Already included in HTML
}

// Display message in chat
function displayMessage(text, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', sender);
    
    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    messageDiv.innerHTML = `
        <div class="message-text">${text}</div>
        <div class="message-time">${time}</div>
    `;
    
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
    return messageDiv;
}

// Show typing indicator
function showTypingIndicator() {
    const typingDiv = document.createElement('div');
    typingDiv.classList.add('typing-indicator');
    typingDiv.id = 'typing-indicator';
    typingDiv.innerHTML = `
        <span></span>
        <span></span>
        <span></span>
    `;
    chatBox.appendChild(typingDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
    return typingDiv;
}

// Remove typing indicator
function removeTypingIndicator() {
    const typingIndicator = document.getElementById('typing-indicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

// Send message function
async function sendMessage() {
    const message = userInput.value.trim();
    
    if (message === "") {
        return;
    }

    // Display user message
    displayMessage(message, 'user');
    userInput.value = '';

    // Show typing indicator
    const typingIndicator = showTypingIndicator();

    try {
        // Send request to backend
        const response = await fetch("http://localhost:5000/ask", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                question: message
            }),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        
        // Remove typing indicator
        removeTypingIndicator();
        
        // Display bot response
        displayMessage(data.answer, 'bot');
        
    } catch (error) {
        console.error("Error:", error);
        
        // Remove typing indicator
        removeTypingIndicator();
        
        // Display error message
        displayMessage("❌ Error: Cannot connect to backend. Make sure Flask is running on http://localhost:5000", 'bot');
    }
}

// Suggest question from sidebar
function suggestQuestion(question) {
    userInput.value = question;
    userInput.focus();
}

// Enter key to send message
userInput.addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
});

// Full screen toggle
function toggleFullScreen() {
    if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen().catch(err => {
            console.error(`Error attempting to enable full-screen mode: ${err.message}`);
        });
    } else {
        if (document.exitFullscreen) {
            document.exitFullscreen();
        }
    }
}

// Logout function
function logout() {
    if (confirm('Are you sure you want to log out?')) {
        window.location.href = 'login.html';
    }
}

// Test backend connection on load
window.addEventListener('load', function() {
    testBackend();
});

// Test backend connection
async function testBackend() {
    try {
        const response = await fetch("http://localhost:5000/");
        const text = await response.text();
        console.log("✅ Backend is running:", text);
    } catch (error) {
        console.error("❌ Backend is NOT running:", error);
        displayMessage("⚠️ Backend is not running! Please run 'python app.py' in your backend folder.", 'bot');
    }
}