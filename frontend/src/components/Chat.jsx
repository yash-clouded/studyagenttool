import React, { useState, useRef, useEffect } from "react";
import { sendChat } from "../api";

export default function Chat(){
  const [q, setQ] = useState("");
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);
  const historyEndRef = useRef(null);

  const scrollToBottom = () => {
    historyEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [history]);

  const ask = async () => {
    if(!q.trim()) return;

    const userQuestion = q;
    setHistory(h => [...h, { from: "user", text: userQuestion }]);
    setQ("");
    setLoading(true);
    
    try{
      const res = await sendChat({ question: userQuestion, chat_history: history.filter(h => h.from === 'assistant').map(h => [h.q, h.text]) });
      const answer = res.data.answer;
      setHistory(h => [...h, { from: "assistant", text: answer, q: userQuestion }]);
    }catch(e){
      console.error(e);
      setHistory(h => [...h, { from: "assistant", text: "❌ Error contacting server. Please try again." }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if(e.key === "Enter" && e.ctrlKey) {
      ask();
    }
  };

  return (
    <div style={styles.container}>
      <h2 style={styles.title}>Study Assistant Chat</h2>

      {/* Chat History */}
      <div style={styles.chatHistory}>
        {history.length === 0 && (
          <div style={styles.emptyMessage}>
            <p>No conversation yet. Ask your first question below! 💡</p>
          </div>
        )}
        {history.map((h, i) => (
          <div key={i} style={h.from === 'user' ? styles.userMessage : styles.assistantMessage}>
            <div style={h.from === 'user' ? styles.userMessageBubble : styles.assistantMessageBubble}>
              <p style={styles.messageText}>{h.text}</p>
            </div>
          </div>
        ))}
        {loading && (
          <div style={styles.assistantMessage}>
            <div style={styles.assistantMessageBubble}>
              <p style={styles.messageText}>⏳ Thinking...</p>
            </div>
          </div>
        )}
        <div ref={historyEndRef} />
      </div>

      {/* Input Box */}
      <div style={styles.inputSection}>
        <textarea 
          value={q} 
          onChange={e => setQ(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask a question about your study materials... (Ctrl+Enter to send)"
          style={styles.textarea}
          disabled={loading}
        />
        <button 
          onClick={ask} 
          disabled={loading || !q.trim()}
          style={{...styles.sendButton, opacity: (loading || !q.trim()) ? 0.5 : 1}}
        >
          {loading ? "⏳ Sending..." : "Send"}
        </button>
      </div>
    </div>
  );
}

const styles = {
  container: {
    maxWidth: "700px",
    margin: "40px auto",
    padding: "20px",
    display: "flex",
    flexDirection: "column",
    height: "calc(100vh - 200px)",
  },
  title: {
    fontSize: "28px",
    fontWeight: "700",
    color: "#1a1a1a",
    margin: "0 0 24px 0",
  },
  chatHistory: {
    flex: 1,
    overflowY: "auto",
    marginBottom: "16px",
    paddingRight: "8px",
  },
  emptyMessage: {
    textAlign: "center",
    color: "#999",
    padding: "40px 20px",
    fontSize: "14px",
  },
  userMessage: {
    display: "flex",
    justifyContent: "flex-end",
    marginBottom: "8px",
  },
  assistantMessage: {
    display: "flex",
    justifyContent: "flex-start",
    marginBottom: "8px",
  },
  userMessageBubble: {
    maxWidth: "80%",
    padding: "12px 16px",
    borderRadius: "8px",
    backgroundColor: "#3b82f6",
    color: "#fff",
  },
  assistantMessageBubble: {
    maxWidth: "80%",
    padding: "12px 16px",
    borderRadius: "8px",
    backgroundColor: "#eff6ff",
    color: "#1a1a1a",
  },
  messageText: {
    margin: "0",
    fontSize: "14px",
    lineHeight: "1.5",
  },
  inputSection: {
    display: "flex",
    gap: "12px",
    alignItems: "flex-end",
  },
  textarea: {
    flex: 1,
    padding: "12px",
    border: "1px solid #ddd",
    borderRadius: "6px",
    fontSize: "14px",
    fontFamily: "inherit",
    resize: "vertical",
    maxHeight: "100px",
    minHeight: "44px",
  },
  sendButton: {
    padding: "12px 24px",
    backgroundColor: "#3b82f6",
    color: "white",
    border: "none",
    borderRadius: "6px",
    fontSize: "14px",
    fontWeight: "600",
    cursor: "pointer",
    transition: "all 0.2s ease",
    whiteSpace: "nowrap",
  },
};
