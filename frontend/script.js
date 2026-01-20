const API_URL = "http://127.0.0.1:8000/chat";
const SUGGEST_URL = "http://127.0.0.1:8000/suggest";
const USER_ID = "user123";

let isFirstMessage = true;
let isTyping = false;

// Initialize the app
document.addEventListener('DOMContentLoaded', function() {
    loadSuggestions();
    setupEventListeners();
});

function setupEventListeners() {
    const input = document.getElementById('msgInput');
    
    // Enter key to send
    input.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
}

function hideWelcomeMessage() {
    const welcomeMsg = document.getElementById('welcomeMessage');
    if (welcomeMsg) {
        welcomeMsg.style.display = 'none';
    }
}

function addMsg(text, cls, data = null) {
    const chatBox = document.querySelector('.chat-box');
    const msgDiv = document.createElement('div');
    msgDiv.className = `msg ${cls}`;
    
    // Create message content
    const msgContent = document.createElement('div');
    msgContent.className = 'msg-content';
    
    if (cls === 'bot' && data && data.products && data.products.length > 0) {
        // Format product results
        msgContent.innerHTML = formatProductResponse(text, data);
    } else {
        msgContent.innerText = text;
    }
    
    // Create timestamp
    const timestamp = document.createElement('div');
    timestamp.className = 'msg-time';
    timestamp.innerText = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    // Assemble message
    msgDiv.appendChild(msgContent);
    msgDiv.appendChild(timestamp);
    chatBox.appendChild(msgDiv);
    
    // Scroll to bottom
    chatBox.scrollTop = chatBox.scrollHeight;
}

function formatProductResponse(text, data) {
    let html = `<div>${text.replace(/\n/g, '<br>')}</div>`;
    
    if (data.products && data.products.length > 0) {
        data.products.forEach(product => {
            html += `
                <div class="product-card">
                    <div class="product-name">${product.name}</div>
                    <div class="product-price">₹${product.price}/${product.unit}</div>
                    <div class="product-business">
                        📍 ${product.business.name}<br>
                        📞 ${product.business.phone}
                    </div>
                </div>
            `;
        });
    }
    
    return html;
}

function showTypingIndicator() {
    if (isTyping) return;
    
    isTyping = true;
    const chatBox = document.querySelector('.chat-box');
    const typingDiv = document.createElement('div');
    typingDiv.className = 'msg bot typing-message';
    typingDiv.innerHTML = `
        <div class="typing-indicator">
            <div class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    `;
    chatBox.appendChild(typingDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function hideTypingIndicator() {
    const typingMsg = document.querySelector('.typing-message');
    if (typingMsg) {
        typingMsg.remove();
    }
    isTyping = false;
}

async function sendMessage() {
    const input = document.getElementById('msgInput');
    const text = input.value.trim();
    
    if (!text || isTyping) return;
    
    // Hide welcome message on first interaction
    if (isFirstMessage) {
        hideWelcomeMessage();
        isFirstMessage = false;
    }
    
    // Add user message
    addMsg(text, 'user');
    input.value = '';
    
    // Show typing indicator
    showTypingIndicator();
    
    try {
        const response = await fetch(API_URL, {
            method: "POST",
            headers: { 
                "Content-Type": "application/json" 
            },
            body: JSON.stringify({
                message: text,
                user_id: USER_ID,
                location: { latitude: 17.4485, longitude: 78.3908 }
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Hide typing indicator
        hideTypingIndicator();
        
        // Add bot response with product data if available
        addMsg(data.response, 'bot', data);
        
    } catch (error) {
        hideTypingIndicator();
        console.error('Error:', error);
        
        let errorMessage = '❌ Sorry, I encountered an error. ';
        if (error.message.includes('Failed to fetch')) {
            errorMessage += 'The backend server appears to be offline. Please ensure the server is running on port 8000.';
        } else {
            errorMessage += 'Please try again in a moment.';
        }
        
        addMsg(errorMessage, 'bot');
    }
    
    // Focus input for next message
    input.focus();
}

async function loadSuggestions() {
    try {
        const response = await fetch(SUGGEST_URL);
        if (!response.ok) throw new Error('Failed to load suggestions');
        
        const data = await response.json();
        const container = document.getElementById('suggestionButtons');
        container.innerHTML = '';
        
        data.questions.forEach(question => {
            const btn = document.createElement('button');
            btn.className = 'suggestion-btn';
            btn.innerText = question;
            btn.onclick = () => {
                document.getElementById('msgInput').value = question;
                sendMessage();
            };
            container.appendChild(btn);
        });
        
    } catch (error) {
        console.warn('Failed to load suggestions:', error);
        
        // Fallback suggestions
        const fallbackSuggestions = [
            'Show me rice', 'Products under Rs.50', 'Where can I buy vegetables?',
            'Grocery stores near me', 'Who sells dal?', 'Do you have apples?'
        ];
        
        const container = document.getElementById('suggestionButtons');
        container.innerHTML = '';
        
        fallbackSuggestions.forEach(question => {
            const btn = document.createElement('button');
            btn.className = 'suggestion-btn';
            btn.innerText = question;
            btn.onclick = () => {
                document.getElementById('msgInput').value = question;
                sendMessage();
            };
            container.appendChild(btn);
        });
    }
}

async function refreshSuggestions() {
    const refreshBtn = document.querySelector('.quick-action[onclick="refreshSuggestions()"]');
    
    // Add spinning animation to refresh button
    if (refreshBtn) {
        refreshBtn.innerHTML = '<i class="fas fa-sync fa-spin"></i> Refresh';
    }
    
    try {
        await loadSuggestions();
    } finally {
        // Restore refresh button icon
        setTimeout(() => {
            if (refreshBtn) {
                refreshBtn.innerHTML = '<i class="fas fa-sync"></i> Refresh';
            }
        }, 500);
    }
}

function clearChat() {
    const chatBox = document.querySelector('.chat-box');
    chatBox.innerHTML = '';
    isFirstMessage = true;
    
    // Show welcome message again
    const welcomeMsg = document.getElementById('welcomeMessage');
    if (welcomeMsg) {
        welcomeMsg.style.display = 'block';
        chatBox.appendChild(welcomeMsg);
    }
    
    document.getElementById('msgInput').focus();
}
