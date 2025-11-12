import React, { useState, useEffect } from "react";
import UploadPanel from "./components/UploadPanel";
import Flashcards from "./components/Flashcards";
import Quizzes from "./components/Quizzes";
import Planner from "./components/Planner";
import Chat from "./components/Chat";
import { fetchFlashcards, fetchQuizzes, fetchPlanner } from "./api";

export default function App(){
  const [files, setFiles] = useState([]);
  const [flashcards, setFlashcards] = useState([]);
  const [quizzes, setQuizzes] = useState([]);
  const [planner, setPlanner] = useState([]);
  const [activeTab, setActiveTab] = useState("upload");
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadedFile, setUploadedFile] = useState(null);

  const loadAll = async () => {
    try{
      const f = await fetchFlashcards();
      const q = await fetchQuizzes();
      const p = await fetchPlanner();
      setFlashcards(f.data || []);
      setQuizzes(q.data || []);
      setPlanner(p.data || []);
    }catch(e){
      console.error(e);
    }
  };

  const addQuizzes = async () => {
    try {
      const resp = await fetchQuizzes();
      const newItems = resp.data || [];
      const existingQs = new Set(quizzes.map((q) => q.question));
      const toAdd = newItems.filter((q) => !existingQs.has(q.question));
      if (toAdd.length > 0) {
        setQuizzes((prev) => [...prev, ...toAdd]);
      }
    } catch (e) {
      console.error("Failed to fetch quizzes:", e);
    }
  };

  useEffect(()=>{ loadAll(); }, []);

  const tabs = [
    { id: "upload", label: "Upload", icon: "📤" },
    { id: "flashcards", label: "Flashcards", icon: "📚" },
    { id: "quizzes", label: "Quizzes", icon: "✅" },
    { id: "planner", label: "Revision Plan", icon: "📅" },
    { id: "chat", label: "Chat", icon: "💬" },
  ];

  return (
    <div className="app-container">
      <header>
        <div className="brand">
          <h1>StudyBuddy AI</h1>
        </div>
        <nav>
          {tabs.map(tab => (
            <a 
              href="#"
              key={tab.id} 
              className={`nav-tab ${activeTab === tab.id ? 'active' : ''}`}
              onClick={(e) => { e.preventDefault(); setActiveTab(tab.id); }}
            >
              {tab.label}
            </a>
          ))}
        </nav>
      </header>

      <main className="main-content">
        {activeTab === "upload" && <UploadPanel files={files} setFiles={setFiles} onDone={() => { loadAll(); setActiveTab("flashcards"); }} uploadProgress={uploadProgress} setUploadProgress={setUploadProgress} setUploadedFile={setUploadedFile} />}
        {activeTab === "flashcards" && <Flashcards cards={flashcards} />}
        {activeTab === "quizzes" && <Quizzes quizzes={quizzes} />}
        {activeTab === "planner" && <Planner plan={planner} />}
        {activeTab === "chat" && <Chat />}
      </main>
    </div>
  );
}
