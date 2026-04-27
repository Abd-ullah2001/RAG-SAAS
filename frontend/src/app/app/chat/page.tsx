"use client";

import { useState, useRef, useEffect } from "react";
import { Send, FileText, Plus, MessageSquare } from "lucide-react";
import { supabase } from "@/lib/supabase";
import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function ChatConsole() {
  const [msgs, setMsgs] = useState<any[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [msgs, loading]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;
    
    const userMsg = { id: Date.now(), role: "user", content: input, time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) };
    setMsgs(prev => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    const { data: { session } } = await supabase.auth.getSession();
    if (!session) {
      alert("Please log in first");
      setLoading(false);
      return;
    }

    try {
      const res = await axios.post(`${API_URL}/query`, {
        question: input,
        top_k: 3
      }, {
        headers: { Authorization: `Bearer ${session.access_token}` }
      });

      const aiMsg = { 
        id: Date.now() + 1, 
        role: "ai", 
        content: res.data.answer,
        sources: res.data.context.map((c: any) => ({ 
          doc: c.metadata?.filename || "Source", 
          page: c.metadata?.page_label || "?" 
        })),
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) 
      };
      setMsgs(prev => [...prev, aiMsg]);
    } catch (err) {
      console.error("Query failed", err);
      const errMsg = { 
        id: Date.now() + 1, 
        role: "ai", 
        content: "Sorry, I encountered an error while processing your request. Please make sure you have uploaded documents and try again.",
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) 
      };
      setMsgs(prev => [...prev, errMsg]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="cwrap">
      <div className="cside">
        <div className="p16" style={{ borderBottom: "1px solid var(--b)" }}>
          <button className="btn bp wf" style={{ justifyContent: "center" }} onClick={() => setMsgs([])}>
            <Plus size={14} /> New Chat
          </button>
        </div>
        <div className="f1" style={{ overflowY: "auto", padding: 12 }}>
          <div className="lbl" style={{ padding: "0 8px" }}>Recent Threads</div>
          <div className="ni on" style={{ marginBottom: 4 }}>
            <MessageSquare size={14} />
            <div className="f1 trunc">Current Session</div>
          </div>
        </div>
      </div>

      <div className="cmain">
        <div className="mlist">
          {msgs.length === 0 && (
            <div style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", opacity: 0.5 }}>
              <MessageSquare size={48} className="mb16" />
              <p>Ask a question about your documents to start chatting.</p>
            </div>
          )}
          {msgs.map((m, i) => (
            <div key={m.id} style={{ display: "flex", flexDirection: "column" }}>
              <div className={m.role === "user" ? "mu" : "ma"}>
                <div style={{ whiteSpace: "pre-wrap" }}>{m.content}</div>
                {m.sources && m.sources.length > 0 && (
                  <div className="mt12 fx ic gap8" style={{ flexWrap: "wrap" }}>
                    <span className="xs tm">Sources:</span>
                    {m.sources.map((s: any, idx: number) => {
                      const isUrl = s.doc.startsWith('http');
                      return isUrl ? (
                        <a key={idx} href={s.doc} target="_blank" rel="noopener noreferrer" className="spill" style={{textDecoration: 'none'}}>
                          <FileText size={10} /> {s.page !== "?" ? `Sheet ${s.page}` : "Link"}
                        </a>
                      ) : (
                        <span key={idx} className="spill"><FileText size={10} /> {s.doc} {s.page !== "?" ? `(p.${s.page})` : ""}</span>
                      );
                    })}
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
