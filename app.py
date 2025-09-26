import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from thefuzz import process

# --- Pydantic Model for Input Validation ---
class Question(BaseModel):
    question: str

app = FastAPI()

# --- Knowledge Base is now embedded in the script ---
answers_db = {
    "what microbes have been studied on the iss": "E. coli and Bacillus subtilis are commonly studied on the ISS in microgravity experiments to understand their behavior in space.",
    "how does microgravity affect bacterial growth": "Microgravity can surprisingly alter bacterial growth rates, increase their resistance to antibiotics, and change their gene expression, which is a key area of study.",
    "what plants grow best in microgravity": "Leafy greens like lettuce and radishes, as well as dwarf wheat, have been successfully grown in microgravity. They are chosen for their fast growth cycles and nutritional value.",
    "how do astronauts maintain bone density in space": "Astronauts combat bone density loss through a strict regimen of resistance exercises (like weightlifting), a calcium-rich diet, and sometimes specific medications.",
    "can microbes survive long-term in space": "Yes, some incredibly resilient microbes called extremophiles, as well as certain bacterial spores, have been shown to survive for years when exposed to the vacuum and radiation of space.",
    "what is astrobiology": "Astrobiology is the scientific field dedicated to studying the origin, evolution, distribution, and future of life in the universe. It explores the possibility of life beyond Earth."
}
questions = list(answers_db.keys())

# --- Frontend HTML, CSS, and JavaScript ---
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>AstroBio Knowledge Engine</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css">
    <style>
        body {
            margin: 0; padding: 0; font-family: "Orbitron", sans-serif;
            color: white; text-align: center;
            background: radial-gradient(ellipse at bottom, #0d1b2a 0%, #000000 100%);
            overflow-x: hidden; overflow-y: auto; height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        body::before {
            content: ""; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: url('https://www.transparenttextures.com/patterns/stardust.png');
            z-index: -3; animation: stars 200s linear infinite;
        }
        @keyframes stars { from { background-position: 0 0; } to { background-position: -10000px 5000px; } }
        h1 { font-size: 2.3rem; margin: 20px 10px; text-shadow: 0 0 15px cyan, 0 0 30px blue; }
        .earth-container {
            position: relative;
            width: 250px;
            height: 250px;
            margin: 40px auto; /* Reduced margin */
            flex-shrink: 0;
        }
        .earth {
            width: 100%; height: 100%; border-radius: 50%;
            background: url('https://upload.wikimedia.org/wikipedia/commons/9/97/The_Earth_seen_from_Apollo_17.jpg') no-repeat center/cover;
            animation: spin 30s linear infinite; box-shadow: 0 0 40px rgba(76, 201, 240, 0.8);
        }
        .orbit {
            position: absolute; top: -75px; left: -75px; width: 400px; height: 400px;
            border: 1px dashed rgba(255, 255, 255, 0.3); border-radius: 50%; animation: rotate 20s linear infinite;
        }
        .iss {
            width: 50px; height: 25px;
            background: url('https://upload.wikimedia.org/wikipedia/commons/d/d0/International_Space_Station.svg') no-repeat center/contain;
            position: absolute; top: 0; left: 50%; transform: translateX(-50%);
        }
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        @keyframes rotate { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        
        /* Decorative elements are hidden on smaller screens to save space */
        .planet, .comet, .satellite { display: none; }
        @media (min-width: 1024px) {
            .planet { position: absolute; border-radius: 50%; background-size: cover; opacity: 0.8; display: block; }
            .planet.mars {
                width: 80px; height: 80px;
                background: url('https://upload.wikimedia.org/wikipedia/commons/0/02/OSIRIS_Mars_true_color.jpg') no-repeat center/cover;
                top: 20%; left: 10%; animation: float 25s ease-in-out infinite alternate;
            }
            .planet.jupiter {
                width: 120px; height: 120px;
                background: url('https://upload.wikimedia.org/wikipedia/commons/e/e2/Jupiter.jpg') no-repeat center/cover;
                bottom: 15%; right: 8%; animation: float 30s ease-in-out infinite alternate;
            }
            @keyframes float { from { transform: translateY(0px); } to { transform: translateY(40px); } }
            .comet {
                display: block; position: absolute; width: 150px; height: 2px;
                background: linear-gradient(90deg, white, transparent); opacity: 0.8; animation: shoot 10s linear infinite;
            }
            .comet:nth-of-type(1) { top: 10%; left: -200px; animation-delay: 2s; }
            .comet:nth-of-type(2) { top: 50%; left: -200px; animation-delay: 5s; }
            .satellite {
                display: block; position: absolute; width: 40px; height: 40px;
                background: url('https://upload.wikimedia.org/wikipedia/commons/5/5d/Cartoon_satellite.png') no-repeat center/contain;
                top: 60%; left: -60px; animation: drift 60s linear infinite;
            }
            @keyframes shoot { from { transform: translateX(0) translateY(0); } to { transform: translateX(120vw) translateY(-100px); } }
            @keyframes drift { from { transform: translateX(0); } to { transform: translateX(120vw); } }
        }
        
        .engine {
            max-width: 700px;
            width: 90%;
            background: rgba(0, 0, 0, 0.65);
            padding: 25px;
            border-radius: 20px;
            box-shadow: 0 0 25px rgba(0, 255, 255, 0.4);
            margin: auto 0;
            margin-bottom: 20px; /* Added margin at the bottom */
        }
        .input-wrapper {
            position: relative;
            width: 100%;
            margin: 0 auto 15px auto;
        }
        input[type="text"] {
            width: 100%;
            padding: 14px 80px 14px 14px;
            border-radius: 12px;
            border: 2px solid cyan;
            outline: none;
            font-size: 1rem;
            background: rgba(255,255,255,0.08); color: white;
            transition: all 0.3s ease;
            box-sizing: border-box;
        }
        input[type="text"]:focus { box-shadow: 0 0 20px cyan; }
        .icon-btn {
            position: absolute;
            top: 50%;
            transform: translateY(-50%);
            background: none;
            border: none;
            color: cyan;
            font-size: 1.2rem;
            cursor: pointer;
            transition: color 0.3s ease;
        }
        .icon-btn:hover { color: white; }
        .icon-btn.mic { right: 45px; }
        .icon-btn.mic.listening { color: red; animation: pulse 1.5s infinite; }
        .icon-btn.attach { right: 10px; }
        #file-label {
            font-size: 0.8rem;
            color: #aaa;
            height: 1em; /* Reserve space to prevent layout shift */
        }
        @keyframes pulse {
            0% { transform: translateY(-50%) scale(1); }
            50% { transform: translateY(-50%) scale(1.1); }
            100% { transform: translateY(-50%) scale(1); }
        }
        button[type="submit"] {
            padding: 12px 25px; font-size: 1rem; border: none; border-radius: 12px;
            cursor: pointer; background: linear-gradient(90deg, cyan, deepskyblue);
            color: black; font-weight: bold; transition: all 0.3s ease;
        }
        button[type="submit"]:hover:not(:disabled) {
            background: linear-gradient(90deg, deepskyblue, cyan); box-shadow: 0 0 20px cyan;
        }
        button[type="submit"]:disabled { cursor: not-allowed; background: grey; }
        .answer-box {
            margin-top: 20px; padding: 20px; background: rgba(0,0,50,0.6);
            border-radius: 12px; text-align: left; font-size: 1.1rem;
            line-height: 1.6;
            display: none; animation: fadeIn 1s ease;
            min-height: 50px;
        }
        .answer-box .did-you-mean {
            font-style: italic;
            color: #ccc;
            display: block;
            margin-bottom: 10px;
            font-size: 0.9em;
        }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
    </style>
</head>
<body>
    <h1>🚀 AstroBio Knowledge Engine 🚀</h1>

    <div class="earth-container">
        <div class="earth"></div>
        <div class="orbit">
            <div class="iss"></div>
        </div>
    </div>
    
    <!-- Decorative elements -->
    <div class="planet mars"></div>
    <div class="planet jupiter"></div>
    <div class="comet"></div>
    <div class="comet"></div>
    <div class="satellite"></div>

    <div class="engine">
        <form id="qaForm">
            <div class="input-wrapper">
                <input type="text" id="question" placeholder="Ask about space biology..." autocomplete="off">
                <button type="button" id="mic-btn" class="icon-btn mic" title="Ask with voice">
                    <i class="fa-solid fa-microphone"></i>
                </button>
                <label for="file-upload" class="icon-btn attach" title="Attach file (UI only)">
                    <i class="fa-solid fa-paperclip"></i>
                </label>
                <input type="file" id="file-upload" style="display: none;">
            </div>
            <div id="file-label"></div>
            <button id="askButton" type="submit">Ask</button>
        </form>
        <div id="answer" class="answer-box"></div>
    </div>

<script>
    const qaForm = document.getElementById("qaForm");
    const questionInput = document.getElementById("question");
    const askButton = document.getElementById("askButton");
    const answerBox = document.getElementById("answer");
    const micBtn = document.getElementById("mic-btn");
    const fileUpload = document.getElementById("file-upload");
    const fileLabel = document.getElementById("file-label");

    // --- MODIFIED: A helper function to display messages in the answer box ---
    function showMessage(htmlContent, isError = false) {
        answerBox.style.display = "block";
        answerBox.style.color = isError ? "#ff8a8a" : "white";
        typeEffect(answerBox, htmlContent);
    }

    async function handleQuestion(event) {
        event.preventDefault();
        const question = questionInput.value.trim();
        if (!question) return;

        askButton.disabled = true;
        askButton.textContent = "Searching...";
        showMessage("Transmitting your query to deep space...");
        fileLabel.textContent = "";

        try {
            const response = await fetch("/ask", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ question: question })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            // --- MODIFIED: Smarter response handling ---
            let answerHtml = "";
            if (data.confidence === "high") {
                answerHtml = "🛰️ <strong>Answer Received:</strong> " + data.answer;
            } else if (data.confidence === "medium") {
                answerHtml = `<span class='did-you-mean'>I think you mean: "${data.match}"</span>` + data.answer;
            } else {
                answerHtml = data.answer; // Low confidence message from backend
            }
            
            setTimeout(() => {
                showMessage(answerHtml);
            }, 500); // Shorter delay

        } catch (err) {
            console.error("Fetch Error:", err);
            showMessage("Error: Lost signal with the knowledge base!", true);
        } finally {
            setTimeout(() => {
                askButton.disabled = false;
                askButton.textContent = "Ask";
            }, 1000);
        }
    }
    qaForm.addEventListener('submit', handleQuestion);

    fileUpload.addEventListener('change', () => {
        if (fileUpload.files.length > 0) {
            fileLabel.textContent = `File selected: ${fileUpload.files[0].name}`;
        } else {
            fileLabel.textContent = "";
        }
    });

    // --- MODIFIED: Microphone Logic with no alerts ---
    let isListening = false;
    micBtn.addEventListener('click', () => {
        if (isListening) return;

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            showMessage("Sorry, your browser doesn't support speech recognition. Try Google Chrome.", true);
            return;
        }

        const recognition = new SpeechRecognition();
        recognition.lang = 'en-US';
        recognition.interimResults = false;
        
        recognition.addEventListener('start', () => {
            isListening = true;
            micBtn.classList.add('listening');
        });

        recognition.addEventListener('result', (e) => {
            const transcript = Array.from(e.results)
                .map(result => result[0])
                .map(result => result.transcript)
                .join('');
            questionInput.value = transcript;
            // Automatically submit the question after successful speech recognition
            if (transcript) {
                handleQuestion(new Event('submit'));
            }
        });
        
        recognition.addEventListener('end', () => {
            isListening = false;
            micBtn.classList.remove('listening');
        });
        
        recognition.addEventListener('error', (e) => {
            isListening = false;
            micBtn.classList.remove('listening');
            
            let errorMessage = `An error occurred: ${e.error}`;
            if (e.error === 'not-allowed' || e.error === 'service-not-allowed') {
                errorMessage = "Microphone permission was denied. Please allow microphone access in your browser's site settings.";
            } else if (e.error === 'no-speech') {
                errorMessage = "No speech was detected. Please try again.";
            }
            // Use the answer box to show errors instead of alert
            showMessage(errorMessage, true);
        });

        recognition.start();
    });

    function typeEffect(element, text, speed = 20) {
        element.innerHTML = "";
        let i = 0;
        function typing() {
            if (i < text.length) {
                // Allow HTML tags to be rendered correctly
                const char = text.slice(i).match(/^<[^>]+>/);
                if (char) {
                    const tag = char[0];
                    element.innerHTML += tag;
                    i += tag.length;
                } else {
                    element.innerHTML += text.charAt(i);
                    i++;
                }
                setTimeout(typing, speed);
            }
        }
        typing();
    }
</script>
</body>
</html>
"""

# --- API Endpoints ---
@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    return HTMLResponse(content=html_content)

# --- MODIFIED: This is the core fix for your application ---
@app.post("/ask")
async def ask_question(question_data: Question):
    query = question_data.question.lower().strip()
    
    # Use extractOne to find the best possible match from the knowledge base
    best_match = process.extractOne(query, questions)
    
    # --- DEBUGGING: You can check your terminal to see the match score ---
    print("-" * 50)
    print(f"[DEBUG] User Question: '{query}'")
    if best_match:
        print(f"[DEBUG] Best Match Found: '{best_match[0]}' with score {best_match[1]}")
    else:
        print("[DEBUG] No match found.")
    print("-" * 50)
    # -------------------------------------------------------------------

    answer = "Sorry, my knowledge circuits couldn't find a confident answer. Please try rephrasing."
    matched_question = ""
    confidence = "low"

    if best_match:
        match_str, score = best_match
        # High confidence: If the score is very high, it's almost certainly the right question.
        if score > 90:
            answer = answers_db[match_str]
            confidence = "high"
            matched_question = match_str
        # Medium confidence: If the score is decent, we provide the answer but also clarify what question we *think* was asked. This prevents wrong answers.
        elif score > 70:
            answer = answers_db[match_str]
            confidence = "medium"
            matched_question = match_str
            
    # For low confidence, the default message is used.
    
    return JSONResponse({
        "answer": answer,
        "match": matched_question,
        "confidence": confidence
    })

# --- Main execution block ---
if __name__ == "__main__":
    # It's recommended to run with uvicorn from the command line,
    # but this block is here for convenience.
    uvicorn.run(app, host="127.0.0.1", port=8000)
