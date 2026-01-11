let messages = [];

function scrollToBottom() {
    const messagesDiv = document.getElementById("messages");
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function showTyping() {
    const messagesDiv = document.getElementById("messages");
    const id = "typing-" + Date.now();
    const html = `
        <div class="message bot-msg typing-indicator" id="${id}">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        </div>
    `;
    messagesDiv.insertAdjacentHTML('beforeend', html);
    scrollToBottom();
    return id;
}

function removeTyping(id) {
    const element = document.getElementById(id);
    if (element) element.remove();
}

async function uploadPDF() {
    const fileInput = document.getElementById("pdfUpload");
    const reportOutput = document.getElementById("reportOutput");
    const messagesDiv = document.getElementById("messages");

    if (!fileInput.files.length) return;

    try {
        messagesDiv.innerHTML += `<div class="system-msg">Processing report...</div>`;
        
        const formData = new FormData();
        formData.append("file", fileInput.files[0]);

        const res = await fetch("/upload", { method: "POST", body: formData });
        const data = await res.json();

        reportOutput.textContent = JSON.stringify(data, null, 2);

        // --- EXTRACT DETECTED LANGUAGE ---
        const detectedLang = data.report_metadata?.language || "English";
        console.log("Detected Language:", detectedLang);

        // --- MULTI-LANGUAGE SYSTEM PROMPT (ANTI-REPETITION FIX) ---
        messages = [
          {
            role: "system",
            content: `You are a friendly and professional Medical Doctor.
            
            **CONTEXT:**
            The patient's medical report is attached below as JSON data.
            Language Detected: **${detectedLang}**.

            **CRITICAL CONVERSATION RULES:**
            1. **NO REPETITION:** The user has already seen the initial summary. DO NOT repeat the patient's name, age, or general diagnosis in every reply.
            2. **DIRECT ANSWERS:** If the user asks a specific question (e.g., "What should I eat?"), answer ONLY that question. Do not re-summarize the report.
            3. **BE CONCISE:** Keep responses short and conversational, like a real chat.
            4. **LANGUAGE:** Always reply in **${detectedLang}** (or whatever language the user switches to).

            **MEDICAL DATA:** ${JSON.stringify(data)}`
          }
        ];

        messagesDiv.innerHTML += `<div class="system-msg">Analysis ready (${detectedLang}). You can ask questions.</div>`;
        
        // --- OPTIONAL: TRIGGER FIRST WELCOME MESSAGE AUTOMATICALLY ---
        // Uncomment below if you want the bot to speak first
        // sendMessage("Please summarize my report."); 

        scrollToBottom();

    } catch (error) {
        messagesDiv.innerHTML += `<div class="system-msg" style="color: #ff6b6b">Error: ${error.message}</div>`;
    }
}

async function sendMessage(manualMsg = null) {
    const input = document.getElementById("userInput");
    const messagesDiv = document.getElementById("messages");
    const msg = manualMsg || input.value.trim();
    if (!msg) return;

    messagesDiv.innerHTML += `<div class="message user-msg">${msg}</div>`;
    messages.push({ role: "user", content: msg });
    
    if(!manualMsg) input.value = "";
    scrollToBottom();

    const typingId = showTyping();

    try {
        const res = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ messages })
        });
        const data = await res.json();
        
        removeTyping(typingId);

        let doctorReply = data.message?.content || data.message || "Connection Error.";
        const formattedReply = marked.parse(doctorReply);

        messagesDiv.innerHTML += `<div class="message bot-msg"><b>Doctor:</b><br>${formattedReply}</div>`;
        messages.push({ role: "assistant", content: doctorReply });
        scrollToBottom();

    } catch (error) {
        removeTyping(typingId);
        messagesDiv.innerHTML += `<div class="message bot-msg">Error connecting to server.</div>`;
    }
}

document.getElementById("userInput").addEventListener("keypress", (e) => {
    if (e.key === "Enter") sendMessage();
});