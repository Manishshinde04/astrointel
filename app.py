import uvicorn
import os
import numpy as np
from openai import OpenAI
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv

# --- 1. Configuration and Setup ---
load_dotenv()
try:
    client = OpenAI() # Automatically finds OPENAI_API_KEY in the .env file
except Exception as e:
    print(f"Error initializing OpenAI client: {e}")
    client = None

# --- 2. Knowledge Base ---
knowledge_base = [
    {"id": 1, "context": "E. coli and Bacillus subtilis are commonly studied microbes on the ISS in microgravity experiments to understand their behavior, growth, and mutation in space."},
    {"id": 2, "context": "Microgravity can surprisingly alter bacterial growth rates, increase their resistance to antibiotics, and change their gene expression, which is a key area of study for long-duration space missions."},
    {"id": 3, "context": "Leafy greens like lettuce and radishes, as well as dwarf wheat, have been successfully grown in microgravity. They are chosen for their fast growth cycles and nutritional value for astronauts."},
    {"id": 4, "context": "To combat bone density loss in a zero-gravity environment, astronauts must follow a strict regimen of resistance exercises using special equipment, maintain a calcium-rich diet, and sometimes use specific medications."},
    {"id": 5, "context": "Some incredibly resilient microbes called extremophiles, as well as certain bacterial spores, have been shown to survive for years when exposed to the vacuum and radiation of space, raising questions about the interplanetary transfer of life."},
    {"id": 6, "context": "Astrobiology is the scientific field dedicated to studying the origin, evolution, distribution, and future of life in the universe. It combines principles of biology, chemistry, and astronomy to explore the possibility of life beyond Earth."}
]

# --- 3. Semantic Search Engine ---
class Context_Retriever:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        print("Initializing Context Retriever...")
        self.embedding_model = SentenceTransformer(model_name)
        self.contexts = [item['context'] for item in knowledge_base]
        self.embeddings = self._get_or_create_embeddings()
        print("Context Retriever ready.")

    def _get_or_create_embeddings(self):
        embedding_file = 'kb_embeddings.npy'
        if os.path.exists(embedding_file):
            print("Loading cached embeddings...")
            return np.load(embedding_file)
        else:
            print("Creating and caching new embeddings...")
            embeddings = self.embedding_model.encode(self.contexts, convert_to_tensor=False)
            np.save(embedding_file, embeddings)
            return embeddings

    def retrieve_context(self, query: str, threshold=0.3):
        query_embedding = self.embedding_model.encode([query])
        similarities = cosine_similarity(query_embedding, self.embeddings)[0]
        most_similar_index = np.argmax(similarities)
        if similarities[most_similar_index] < threshold:
            return None
        return self.contexts[most_similar_index]

# --- 4. OpenAI Answer Generation ---
def generate_answer_with_openai(context: str, question: str):
    if not client:
        return "Error: OpenAI client not initialized. Check your API key."

    system_prompt = "You are a helpful assistant. Use only the provided context to answer the user's question. If the context doesn't contain the answer, say that you don't have information on that topic."
    user_prompt = f'Context: "{context}"\n\nQuestion: "{question}"'

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return "Sorry, an error occurred while communicating with the OpenAI AI."

# --- 5. FastAPI Web Application ---
app = FastAPI()
context_retriever = Context_Retriever()

class Question(BaseModel):
    question: str

# --- Full HTML, CSS, and JavaScript Content ---
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
        margin: 70px auto;
        flex-shrink: 0;
    }
    .earth {
      width: 250px; height: 250px; border-radius: 50%;
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
    .planet { position: absolute; border-radius: 50%; background-size: cover; opacity: 0.8; }
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
      position: absolute; width: 150px; height: 2px;
      background: linear-gradient(90deg, white, transparent); opacity: 0.8; animation: shoot 10s linear infinite;
    }
    .comet:nth-child(1) { top: 10%; left: -200px; animation-delay: 2s; }
    .comet:nth-child(2) { top: 50%; left: -200px; animation-delay: 5s; }
    .comet:nth-child(3) { top: 80%; left: -200px; animation-delay: 8s; }
    @keyframes shoot { from { transform: translateX(0) translateY(0); } to { transform: translateX(120vw) translateY(-100px); } }
    .satellite {
      position: absolute; width: 40px; height: 40px;
      background: url('https://upload.wikimedia.org/wikipedia/commons/5/5d/Cartoon_satellite.png') no-repeat center/contain;
      top: 60%; left: -60px; animation: drift 60s linear infinite;
    }
    @keyframes drift { from { transform: translateX(0); } to { transform: translateX(120vw); } }
    .engine {
        max-width: 700px;
        width: 90%;
        background: rgba(0, 0, 0, 0.65);
        padding: 25px;
        border-radius: 20px;
        box-shadow: 0 0 25px rgba(0, 255, 255, 0.4);
        margin: auto 0;
    }
    .input-wrapper {
        position: relative;
        width: 80%;
        max-width: 550px;
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
      margin-top: 20px; padding: 15px; background: rgba(0,0,50,0.6);
      border-radius: 12px; text-align: left; font-size: 1.1rem;
      display: none; animation: fadeIn 1s ease;
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

  <div class="planet mars"></div>
  <div class="planet jupiter"></div>
  <div class="comet"></div>
  <div class="comet"></div>
  <div class="comet"></div>
  <div class="satellite"></div>

  <div class="engine">
    <form id="qaForm">
        <div class="input-wrapper">
            <input type="text" id="question" placeholder="Ask or speak..." autocomplete="off">
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

    async function handleQuestion(event) {
        event.preventDefault();
        const question = questionInput.value.trim();
        if (!question) return;

        askButton.disabled = true;
        askButton.textContent = "Searching...";
        answerBox.style.display = "block";
        typeEffect(answerBox, "Transmitting your query to deep space...");
        fileLabel.textContent = "";

        try {
            const response = await fetch("/ask", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ question: question })
            });
            const data = await response.json();
            
            setTimeout(() => {
                typeEffect(answerBox, "🛰️ Answer Received: " + data.answer);
            }, 1000);

        } catch (err) {
            typeEffect(answerBox, "Error: Lost signal with the knowledge base!");
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

    let isListening = false;
    micBtn.addEventListener('click', () => {
        if (isListening) return;

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            alert("Sorry, your browser doesn't support speech recognition. Try Google Chrome.");
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
                errorMessage = "Microphone permission was denied. Please allow microphone access in your browser's site settings (click the lock icon in the address bar).";
            } else if (e.error === 'no-speech') {
                errorMessage = "No speech was detected. Please try again.";
            } else if (e.error === 'aborted') {
                errorMessage = "Listening was aborted. This can happen if no microphone is found. Please check your microphone connection and settings.";
            }
            alert(errorMessage);
        });

        recognition.start();
    });

    function typeEffect(element, text, speed = 30) {
      element.innerHTML = "";
      let i = 0;
      function typing() {
        if (i < text.length) {
          element.innerHTML += text.charAt(i);
          i++;
          setTimeout(typing, speed);
        }
      }
      typing();
    }
  </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    return HTMLResponse(content=html_content)

@app.post("/ask")
async def ask_question(question_data: Question):
    query = question_data.question
    relevant_context = context_retriever.retrieve_context(query)
    
    if relevant_context:
        final_answer = generate_answer_with_openai(relevant_context, query)
    else:
        final_answer = "I'm sorry, my knowledge base doesn't seem to contain a specific fact about that topic."
    
    return JSONResponse({"answer": final_answer})

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)