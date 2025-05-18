const apiUrl = 'http://127.0.0.1:8000/chat';

function escapeHTML(str) {
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function formatMarkup(text) {
    const esc = escapeHTML(text);
    return esc
      // strong/bold
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      // italic
      .replace(/\*(.+?)\*/g, '<i>$1</i>');
}

function renderBotResponse(rawText) {
    const wrapper = document.createElement('div');
    wrapper.classList.add('message', 'bot');

    const lines = rawText.split('\n');
    let ul;

    lines.forEach(line => {
        const trimmed = line.trim();
        if (trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
            // start a UL if we haven’t already
            if (!ul) {
                ul = document.createElement('ul');
                wrapper.appendChild(ul);
            }
            const li = document.createElement('li');
            li.innerHTML = formatMarkup(trimmed.substring(2).trim());
            ul.appendChild(li);
        }
        else if (trimmed === '') {
            // blank line → add a <br> or just skip
            wrapper.appendChild(document.createElement('br'));
        }
        else {
            // normal paragraph
            const p = document.createElement('p');
            p.innerHTML = formatMarkup(line);
            wrapper.appendChild(p);
            ul = null;  // close any open list
        }
    });

    return wrapper;
}

function handleKeyPress(event) {
    if (event.key === "Enter") {
        sendMessage();
    }
}

function sendMessage() {
    const userInput = document.getElementById('user-input').value;
    if (userInput.trim() === '') return;

    addUserMessage('user', userInput);

    fetch(apiUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ question: userInput })
    })
    .then(response => response.json())
    .then(data => {
        addMessage('bot', data.answer);
    })
    .catch(error => {
        console.error('Error:', error);
        addMessage('bot', 'Sorry, something went wrong.');
    });

    document.getElementById('user-input').value = '';
}

function sendAMessage() {
    const userInput = document.getElementById('user-input').value;
    if (userInput.trim() === '') return;

    addUserMessage('user', userInput);
    document.getElementById('user-input').value = '';

    fetch('http://127.0.0.1:8000/chat-stream', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ question: userInput })
    })
    .then(async (response) => {
        if (!response.ok || !response.body) {
            throw new Error("No stream response");
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder("utf-8");
        let buffer = '';
        let botContainer = document.createElement('div');
        botContainer.classList.add('message', 'bot');
        document.getElementById('messages').appendChild(botContainer);
        document.getElementById('messages').scrollTop = document.getElementById('messages').scrollHeight;

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });

            // Process by SSE format (each chunk ends with \n\n)
            const parts = buffer.split("\n\n");
            buffer = parts.pop();  // last incomplete part

            for (const part of parts) {
                if (part.startsWith("data: ")) {
                    const text = part.slice(6);
                    const span = document.createElement('span');
                    span.innerHTML = formatMarkup(text);
                    botContainer.appendChild(span);
                    document.getElementById('messages').scrollTop = document.getElementById('messages').scrollHeight;
                }
            }
        }

        if (buffer && buffer.startsWith("data: ")) {
            const text = buffer.slice(6);
            const span = document.createElement('span');
            span.innerHTML = formatMarkup(text);
            botContainer.appendChild(span);
        }

    })
    .catch(error => {
        console.error('Error:', error);
        addMessage('bot', 'Sorry, something went wrong.');
    });
}

function addMessage(sender, text) {
    const messageContainer = renderBotResponse(text);
    messageContainer.classList.add('message', sender);
    document.getElementById('messages').appendChild(messageContainer);
    document.getElementById('messages').scrollTop = document.getElementById('messages').scrollHeight;
}
function addUserMessage(sender, text) {
    const messageContainer = document.createElement('div');
    messageContainer.classList.add('message', sender);
    messageContainer.textContent = text;
    document.getElementById('messages').appendChild(messageContainer);
    document.getElementById('messages').scrollTop = document.getElementById('messages').scrollHeight;
}