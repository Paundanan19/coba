document.getElementById("chat-form").addEventListener("submit", async function(event) {
    event.preventDefault();

    let userInput = document.getElementById("user-input").value.trim();
    if (userInput === "") return;

    appendMessage("user", userInput);
    document.getElementById("user-input").value = "";

    try {
        let response = await fetch("/ask", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question: userInput })
        });

        let data = await response.json();
        let botResponse = `<strong>Nama Event:</strong> ${data.event_name} <br> <strong>Deskripsi:</strong> ${data.event_about}`;
        appendMessage("bot", botResponse);

        // Konversi teks ke suara
        speakText(botResponse);
    } catch (error) {
        appendMessage("bot", "Terjadi kesalahan, coba lagi nanti.");
    }
});

function appendMessage(sender, text) {
    let chatBox = document.getElementById("chat-box");
    let messageDiv = document.createElement("div");
    messageDiv.classList.add("chat-message", sender);
    messageDiv.innerHTML = `<p>${text}</p>`;
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Fitur input suara
document.getElementById("voice-btn").addEventListener("click", function() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        alert("Speech Recognition tidak didukung di browser ini.");
        return;
    }

    let recognition = new SpeechRecognition();
    recognition.lang = "id-ID";

    recognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript;
        document.getElementById("user-input").value = transcript;
    };

    recognition.onerror = function(event) {
        console.log("Error: " + event.error);
    };

    recognition.start();
});

// Fungsi untuk mengubah teks menjadi suara
function speakText(text) {
    const speechSynthesis = window.speechSynthesis;
    if (!speechSynthesis) {
        console.warn("Text-to-Speech tidak didukung di browser ini.");
        return;
    }

    let utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "id-ID";
    speechSynthesis.speak(utterance);
}

const https = require('https');
const fs = require('fs');
const express = require('express');
const app = express();

const options = {
  key: fs.readFileSync('key.pem'),
  cert: fs.readFileSync('cert.pem')
};

app.use(express.static('public'));

app.get('/', (req, res) => {
  res.send('Hello HTTPS!');
});

https.createServer(options, app).listen(443, () => {
  console.log('Server HTTPS berjalan di https://localhost:443');
});
