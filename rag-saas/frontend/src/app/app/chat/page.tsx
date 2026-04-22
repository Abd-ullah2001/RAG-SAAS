"use client";

import { useState, useRef, useEffect } from "react";
import { Send, FileText, Plus, MessageSquare } from "lucide-react";
import { INIT_MSGS, THREADS } from "@/lib/mock-data";

export default function ChatConsole() {
  const [msgs, setMsgs] = useState(INIT_MSGS);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [msgs, loading]);

  const handleSend = () => {
    if (!input.trim() || loading) return;
    
    const newMsg = { id: Date.now(), role: "user", content: input, time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) };
    setMsgs([...msgs, newMsg]);
    setInput("");
    setLoading(true);

    // Simulate AI typing delay and streaming response
    setTimeout(() => {
      setLoading(false);
      const aiMsg = { 
        id: Date.now() + 1, 
        role: "ai", 
        content: "This is a simulated response based on the RAG context. The backend integration will provide the actual semantic search results and LLM generated answers here.",
        sources: [{ page: 1, doc: "Simulated_Source.pdf" }],
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) 
      };
      setMsgs(prev => [...prev, aiMsg]);
    }, 1500);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="cwrap">
      {/* Sidebar for threads */}
      <div className="cside">
        <div className="p16" style={{ borderBottom: "1px solid var(--b)" }}>
          <button className="btn bp wf" style={{ justifyContent: "center" }}>
            <Plus size={14} /> New Chat
          </button>
        </div>
        <div className="f1" style={{ overflowY: "auto", padding: 12 }}>
          <div className="lbl" style={{ padding: "0 8px" }}>Recent Threads</div>
          {THREADS.map(t => (
            <div key={t.id} className={`ni${t.active ? " on" : ""}`} style={{ marginBottom: 4 }}>
              <MessageSquare size={14} />
              <div className="f1 trunc">{t.title}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Main chat area */}
      <div className="cmain">
        <div className="mlist">
          {msgs.map((m, i) => (
            <div key={m.id} style={{ display: "flex", flexDirection: "column" }}>
              <div className={m.role === "user" ? "mu" : "ma"}>
                <div style={{ whiteSpace: "pre-wrap" }}>{m.content}</div>
                {m.sources && m.sources.length > 0 && (
                  <div className="mt12 fx ic gap8" style={{ flexWrap: "wrap" }}>
                    <span className="xs tm">Sources:</span>
                    {m.sources.map((s: any, idx: number) => (
                      <span key={idx} className="spill"><FileText size={10} /> {s.doc} (p.{s.page})</span>
                    ))}
                  </div>
                )}
              </div>
              <div className="xs tm mt4" style={{ alignSelf: m.role === "user" ? "flex-end" : "flex-start", margin: "4px 8px 0" }}>
                {m.time}
              </div>
            </div>
          ))}
          {loading && (
            <div className="ma fx ic gap8">
              <span className="td1" /><span className="td2" /><span className="td3" />
            </div>
          )}
          <div ref={endRef} />
        </div>

        {/* Input bar */}
        <div className="cbar">
          <div className="ciwrap">
            <textarea
              className="cta"
              placeholder="Ask anything about your documents..."
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              rows={1}
            />
            <button 
              className="btn bp sm" 
              style={{ width: 32, height: 32, padding: 0, justifyContent: "center", borderRadius: 8 }}
              onClick={handleSend}
              disabled={!input.trim() || loading}
            >
              <Send size={14} />
            </button>
          </div>
          <div className="xs tm mt8" style={{ textAlign: "center" }}>
            AI can make mistakes. Always verify important information with the cited sources.
          </div>
        </div>
      </div>
    </div>
  );
}
