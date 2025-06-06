/*
    Format text before send
*/

function escapeHTML(str) {
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function formatMarkup(text) {
    text = escapeHTML(text);
    // Headings
    text = text.replace(/^### (.+)$/gm, '<h3>$1</h3>');
    text = text.replace(/^## (.+)$/gm, '<h2>$1</h2>');
    text = text.replace(/^# (.+)$/gm, '<h1>$1</h1>');

    // Bold
    text = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

    // Italic
    text = text.replace(/\*(.+?)\*/g, '<i>$1</i>');

    // Lists
    // text = text.replace(/(^|\n)([-*]) (.+)/g, '$1<li>$3</li>');

    // Wrap <li> with <ul> only once (do not nest every list item)
    // text = text.replace(/(<li>[\s\S]*?<\/li>)/g, '<ul>$1</ul>');

    // Replace double newlines with paragraph breaks
    text = text.replace(/\n{2,}/g, "<br><br>");

    // Replace single newlines (which are not already replaced) with <br>
    text = text.replace(/\n/g, "<br>");

    return text;
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
        let fullAnswer = '';

        // Bot message container
        let botContainer = document.createElement('div');
        botContainer.classList.add('message', 'bot');
        document.getElementById('messages').appendChild(botContainer);
        document.getElementById('messages').scrollTop = document.getElementById('messages').scrollHeight;

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            // console.log(buffer);

            // Process by SSE format (each chunk ends with \n\n)
            const parts = buffer.split("\n\n");
            buffer = parts.pop();  // last incomplete part

            for (let part of parts) {
                // console.log(part);
                if (part === "") {
                    fullAnswer += "\n\n";
                    botContainer.innerHTML += formatMarkup("\n\n");
                    document.getElementById('messages').scrollTop = document.getElementById('messages').scrollHeight;
                    continue;
                }
                if (part === "\n") {
                    fullAnswer += "\n";
                    botContainer.innerHTML += formatMarkup("\n");
                    document.getElementById('messages').scrollTop = document.getElementById('messages').scrollHeight;
                    continue;
                }
                if (part.startsWith("\n")) {
                    fullAnswer += "\n";
                    botContainer.innerHTML += formatMarkup("\n");
                    document.getElementById('messages').scrollTop = document.getElementById('messages').scrollHeight;
                    part = part.trim();
                }
                if (part.startsWith("data: ")) {
                    const text = part.slice(6);

                    fullAnswer += text;
                    botContainer.innerHTML += formatMarkup(text);

                    document.getElementById('messages').scrollTop = document.getElementById('messages').scrollHeight;
                }
            }
        }

        if (buffer && buffer.startsWith("data: ")) {
            const text = buffer.slice(6);

            fullAnswer += text;
            botContainer.innerHTML += formatMarkup(text);
        }
        botContainer.innerHTML = formatMarkup(fullAnswer);
        document.getElementById('messages').scrollTop = document.getElementById('messages').scrollHeight;
        // Save message
        // saveMessage(userInput, fullAnswer);
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
function handleKeyPress(event) {
    if (event.key === "Enter") {
        sendAMessage();
    }
}
function saveMessage(question, answer) {
    /*
        This will save message to mysql database in local
    */
    fetch('http://localhost:3001/api/message', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
            question: question, 
            answer: answer 
        })
    }).then(async (response) => {
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Failed to save message: ${errorText}`); 
        }
        console.log("Message is saved!");
    }).catch(error => {
        console.error('Error:', error);
    });
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
function sendMessage() {
    const userInput = document.getElementById('user-input').value;
    if (userInput.trim() === '') return;

    addUserMessage('user', userInput);

    fetch('http://127.0.0.1:8000/chat', {
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