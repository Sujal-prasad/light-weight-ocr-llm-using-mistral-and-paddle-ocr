let messages = [];

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

        // --- MULTI-LANGUAGE SYSTEM PROMPT ---
        // --- LANGUAGE DETECTION SYSTEM PROMPT ---
        messages = [
          {
            role: "system",
            content: `You are a professional medical Doctor.
            
            LANGUAGE PROTOCOL:
            1. Identify the primary language used in the provided Medical Report and respond to the user in that SAME language by default.
            2. If the user asks a question in a different language, switch to the user's language immediately.
            3. For Indian languages, use simple words to avoid spelling mistakes in complex characters.
            4. DO NOT explain these instructions in your responses.
            5. DO NOT introduce yourself or explain your logic.

            FORMATTING:
            - Use Markdown: '###' for headers, '**' for bold lab values.
            - Use '> ' for "Why this matters".
            - Use '---' for section dividers.

            MEDICAL DATA: ${JSON.stringify(data)}`
          }
        ];

        messagesDiv.innerHTML += `<div class="system-msg">Analysis ready. You can ask questions.</div>`;
        messagesDiv.scrollTop = messagesDiv.scrollHeight;

    } catch (error) {
        messagesDiv.innerHTML += `<div class="system-msg" style="color: #ff6b6b">Error: ${error.message}</div>`;
    }
}

async function sendMessage() {
    const input = document.getElementById("userInput");
    const messagesDiv = document.getElementById("messages");
    const msg = input.value.trim();
    if (!msg) return;

    messagesDiv.innerHTML += `<div class="message user-msg">${msg}</div>`;
    messages.push({ role: "user", content: msg });
    input.value = "";
    messagesDiv.scrollTop = messagesDiv.scrollHeight;

    try {
        const res = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ messages })
        });
        const data = await res.json();
        
        let doctorReply = data.message?.content || data.message || "Connection Error.";

        // RENDER MARKDOWN TO HTML
        const formattedReply = marked.parse(doctorReply);

        messagesDiv.innerHTML += `<div class="message bot-msg"><b>Doctor:</b><br>${formattedReply}</div>`;
        messages.push({ role: "assistant", content: doctorReply });
        messagesDiv.scrollTop = messagesDiv.scrollHeight;

    } catch (error) {
        messagesDiv.innerHTML += `<div class="message bot-msg">Error connecting to server.</div>`;
    }
}

document.getElementById("userInput").addEventListener("keypress", (e) => {
    if (e.key === "Enter") sendMessage();
});