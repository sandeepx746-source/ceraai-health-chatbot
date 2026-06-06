document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatMessages = document.getElementById('chat-messages');
    const typingIndicatorContainer = document.getElementById('typing-indicator-container');
    const chatMessagesInner = document.querySelector('.chat-messages-inner');
    const currentConversationIdInput = document.getElementById('current-conversation-id');
    const sendBtn = document.querySelector('.send-btn');

    if (chatInput) {
        chatInput.addEventListener('keydown', function (e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    }

    if (chatForm) {
        chatForm.addEventListener('submit', function (e) {
            e.preventDefault();
            sendMessage();
        });
    }

    if (sendBtn) {
        sendBtn.addEventListener('click', function (e) {
            e.preventDefault();
            sendMessage();
        });
    }

    async function sendMessage() {
        const message = chatInput.value.trim();
        if (!message) return;

        const welcomeState = document.querySelector('.welcome-state');
        if (welcomeState) welcomeState.remove();

        appendMessage(message, 'user');

        chatInput.value = '';
        chatInput.focus();

        if (typingIndicatorContainer) {
            typingIndicatorContainer.classList.remove('d-none');
        }

        scrollToBottom();

        let conversationId = currentConversationIdInput ? currentConversationIdInput.value : '';
        if (conversationId === '') conversationId = null;

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: message,
                    conversation_id: conversationId
                })
            });

            const data = await response.json();

            if (typingIndicatorContainer) {
                typingIndicatorContainer.classList.add('d-none');
            }

            if (!response.ok || data.error) {
                appendMessage(data.error || 'Server error. Please try again.', 'bot');
                return;
            }

            appendMessage(data.response || 'No response received.', 'bot');

            if (!conversationId && data.conversation_id) {
                currentConversationIdInput.value = data.conversation_id;
                window.history.pushState({}, '', `/chatbot/${data.conversation_id}`);
            }

        } catch (error) {
            if (typingIndicatorContainer) {
                typingIndicatorContainer.classList.add('d-none');
            }
            appendMessage('Connection error. Please check backend.', 'bot');
        }
    }

    function appendMessage(text, sender) {
        const messageContainer = document.createElement('div');
        messageContainer.className = `chat-bubble-container show-message ${sender === 'user' ? 'user-row' : 'bot-row'}`;

        const bubbleDiv = document.createElement('div');
        bubbleDiv.className = `chat-bubble ${sender}`;

        if (sender === 'user') {
            bubbleDiv.textContent = text;
        } else {
            bubbleDiv.innerHTML = cleanBotHtml(text);
            prepareLineFade(bubbleDiv);
        }

        messageContainer.appendChild(bubbleDiv);
        chatMessagesInner.insertBefore(messageContainer, typingIndicatorContainer);

        if (sender === 'bot') {
            animateSingleBotMessage(bubbleDiv);
        }

        scrollToBottom();
    }

    function cleanBotHtml(html) {
        let text = String(html)
            .replace(/```html/g, '')
            .replace(/```/g, '')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .trim();

        if (!text.includes('<p') && !text.includes('<ul') && !text.includes('<li')) {
            text = text
                .split(/\n+/)
                .filter(line => line.trim() !== '')
                .map(line => `<p>${line.trim()}</p>`)
                .join('');
        }

        return text;
    }

    function prepareLineFade(bubble) {
        bubble.querySelectorAll('p, li').forEach(line => {
            line.classList.add('chat-line-fade');
        });
    }

    function animateSingleBotMessage(bubble) {
        const lines = bubble.querySelectorAll('.chat-line-fade');

        lines.forEach((line, index) => {
            setTimeout(() => {
                line.classList.add('show');
                scrollToBottom();
            }, index * 160);
        });
    }

    function scrollToBottom() {
        if (!chatMessages) return;

        setTimeout(() => {
            chatMessages.scrollTo({
                top: chatMessages.scrollHeight,
                behavior: 'smooth'
            });
        }, 50);
    }
});