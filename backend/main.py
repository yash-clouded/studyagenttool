
import os
import json
import asyncio
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, Response, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from agents.reader import ReaderAgent
from agents.flashcard import FlashcardAgent
from agents.quiz import QuizAgent
from agents.planner import PlannerAgent
from agents.chat_agent import ChatAgent

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_community.embeddings import OllamaEmbeddings

from dotenv import load_dotenv

# --- App Initialization ---
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)

# --- Environment and API Key Loading ---
backend_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(backend_dir)
env_path = os.path.join(root_dir, '.env')
load_dotenv(dotenv_path=env_path)

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "mistral")

FAISS_INDEX_PATH = os.environ.get("FAISS_INDEX_PATH", "./outputs/faiss_index")

# --- LLM and Embeddings Initialization (Ollama first) ---
llm = None
embeddings = None
active_provider = "None"

# Tier 1: Ollama
try:
    from utils.ollama_llm import create_ollama_llm
    llm = create_ollama_llm(model=OLLAMA_MODEL)
    embeddings = OllamaEmbeddings(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL)
    active_provider = "Ollama"
    print("✅ Using Ollama as primary LLM provider.")
except Exception as e:
    print(f"Ollama initialization failed: {e}. Falling back...")

# Tier 2: Google Gemini
if not llm and GOOGLE_API_KEY:
    try:
        from utils.google_llm import create_google_llm
        llm = create_google_llm(api_key=GOOGLE_API_KEY)
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GOOGLE_API_KEY)
        active_provider = "Google Gemini"
        print("✅ Using Google Gemini as fallback LLM provider.")
    except Exception as e:
        print(f"Google Gemini initialization failed: {e}. Falling back...")

# Tier 3: OpenAI
if not llm and OPENAI_API_KEY:
    try:
        llm = ChatOpenAI(model_name=os.environ.get("LLM_MODEL", "gpt-4o-mini"), temperature=0.1, api_key=OPENAI_API_KEY)
        embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY)
        active_provider = "OpenAI"
        print("✅ Using OpenAI as final fallback LLM provider.")
    except Exception as e:
        print(f"OpenAI initialization failed: {e}")

if not llm:
    raise RuntimeError("FATAL: All LLM providers failed to initialize. Please check your configurations.")

print(f"\n🎯 Active LLM Provider: {active_provider}\n")

# --- Agent Instantiation ---
reader = ReaderAgent()
flash_agent = FlashcardAgent(llm=llm)
quiz_agent = QuizAgent(llm=llm)
planner_agent = PlannerAgent()
chat_agent = ChatAgent(faiss_index_path=FAISS_INDEX_PATH, llm=llm, embeddings=embeddings)

# --- In-Memory Stores and Helpers ---
accuracy_store = {}
os.makedirs("./outputs", exist_ok=True)

def store_json(obj, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

# --- API Endpoints ---
@app.post("/upload_pdf")
async def upload_pdf(file: UploadFile = File(...)):
    tmp_path = f"./outputs/{file.filename}"
    with open(tmp_path, "wb") as f:
        f.write(await file.read())
    
    chunks = reader.read_file(tmp_path)
    db = FAISS.from_documents([Document(page_content=c) for c in chunks], embeddings)
    db.save_local(FAISS_INDEX_PATH)
    store_json({"chunks_count": len(chunks)}, "./outputs/reader_summary.json")
    return {"status": "ok"}

@app.get("/generate_all")
async def generate_all():
    async def generator():
        if not os.path.exists(FAISS_INDEX_PATH):
            yield f"data: {json.dumps({'error': 'No materials uploaded.'})}\n\n"
            return
        
        db = FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
        chunks = [d.page_content for d in db.docstore._dict.values()]

        yield f"data: {json.dumps({'message': 'Generating flashcards...', 'progress': 10})}\n\n"
        await asyncio.sleep(0.1)
        flashcards = flash_agent.generate_from_chunks(chunks)
        store_json(flashcards, "./outputs/flashcards.json")
        
        yield f"data: {json.dumps({'message': 'Generating quizzes...', 'progress': 50})}\n\n"
        await asyncio.sleep(0.1)
        difficult_chunks = [c for c, s in accuracy_store.items() if s["incorrect"] > s["correct"]]
        quizzes = quiz_agent.generate_from_chunks(chunks + difficult_chunks)
        store_json(quizzes, "./outputs/quizzes.json")

        yield f"data: {json.dumps({'message': 'Creating study plan...', 'progress': 90})}\n\n"
        await asyncio.sleep(0.1)
        all_topics = [c.split("\n")[0][:80] or "Topic" for c in chunks]
        planner = planner_agent.create_revision_schedule(all_topics, accuracy_store)
        store_json(planner, "./outputs/planner.json")

        yield f"data: {json.dumps({'message': 'Complete!', 'progress': 100})}\n\n"

    return StreamingResponse(generator(), media_type="text/event-stream")

@app.get("/flashcards")
async def get_flashcards():
    if not os.path.exists("./outputs/flashcards.json"): return []
    with open("./outputs/flashcards.json") as f: return json.load(f)

@app.get("/quizzes")
async def get_quizzes():
    if not os.path.exists("./outputs/quizzes.json"): return []
    with open("./outputs/quizzes.json") as f: return json.load(f)

@app.get("/planner")
async def get_planner():
    if not os.path.exists("./outputs/planner.json"): return []
    with open("./outputs/planner.json") as f: return json.load(f)

@app.get("/download_plan")
async def download_plan():
    if not os.path.exists("./outputs/planner.json"): raise HTTPException(404, "Plan not found.")
    with open("./outputs/planner.json") as f: plan = json.load(f)
    return Response(planner_agent.to_ics(plan), media_type="text/calendar", headers={"Content-Disposition": "attachment; filename=plan.ics"})

class ChatRequest(BaseModel):
    question: str
    chat_history: list = Field(default_factory=list)

@app.post("/chat")
async def chat(req: ChatRequest):
    if not os.path.exists(FAISS_INDEX_PATH): raise HTTPException(400, "Index not found.")
    db = FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
    retriever = db.as_retriever()
    chain = chat_agent.build_chain(retriever)
    res = chain({"question": req.question, "chat_history": req.chat_history})
    return {"answer": res.get("answer"), "sources": [d.page_content for d in res.get("source_documents", [])]}

class AnswerRequest(BaseModel):
    source_chunk: str
    is_correct: bool

@app.post("/submit_answer")
async def submit_answer(req: AnswerRequest):
    accuracy_store.setdefault(req.source_chunk, {"correct": 0, "incorrect": 0})
    if req.is_correct: accuracy_store[req.source_chunk]["correct"] += 1
    else: accuracy_store[req.source_chunk]["incorrect"] += 1
    return {"status": "ok"}

@app.get("/health")
def health(): return {"status": "ok"}
