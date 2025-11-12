import axios from "axios";

// Default API instance with 5 minute timeout
const API = axios.create({
  baseURL: "http://localhost:8001",
  timeout: 300000, // 5 minutes (300,000 ms)
});

// Extended timeout for long-running operations (10 minutes)
const LONG_TIMEOUT = 600000; // 10 minutes (600,000 ms)

export const uploadPdf = (file, onUploadProgress) => {
  const fd = new FormData();
  fd.append("file", file);
  return API.post("/upload_pdf", fd, { 
    headers: { "Content-Type": "multipart/form-data" },
    timeout: LONG_TIMEOUT,
    onUploadProgress,
  });
};

export const generateAll = (onProgress) => {
  const eventSource = new EventSource("http://localhost:8001/generate_all");
  eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    onProgress(data);
  };
  eventSource.onerror = (err) => {
    console.error("EventSource failed:", err);
    eventSource.close();
  };
  return eventSource;
};

export const fetchFlashcards = () => API.get("/flashcards");
export const fetchQuizzes = () => API.get("/quizzes");
export const fetchPlanner = () => API.get("/planner");
export const sendChat = (payload) => API.post("/chat", payload);
export const submitAnswer = (payload) => API.post("/submit_answer", payload);
export const downloadPlan = () => API.get("/download_plan", { responseType: 'blob' });
