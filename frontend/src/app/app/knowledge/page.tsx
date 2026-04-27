"use client";

import { useState, useRef, useEffect } from "react";
import { Upload, Search, Trash2, FileText, CheckCircle, XCircle, Clock } from "lucide-react";
import { Btn, Inp, Badge, Toggle } from "@/components/ui/shared";
import { supabase } from "@/lib/supabase";
import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function KnowledgeBase() {
  const [docs, setDocs] = useState<any[]>([]);
  const [q, setQ] = useState("");
  const [over, setOver] = useState(false);
  const [loading, setLoading] = useState(false);
  const ref = useRef<HTMLInputElement>(null);

  const fetchDocs = async () => {
    const { data: { session } } = await supabase.auth.getSession();
    if (!session) return;

    try {
      const res = await axios.get(`${API_URL}/me/documents`, {
        headers: { Authorization: `Bearer ${session.access_token}` }
      });
      setDocs(res.data);
    } catch (err) {
      console.error("Failed to fetch documents", err);
    }
  };

  useEffect(() => {
    fetchDocs();
  }, []);

  const handleUpload = async (files: FileList | null) => {
    if (!files || files.length === 0) return;
    
    const { data: { session } } = await supabase.auth.getSession();
    if (!session) return;

    setLoading(true);
    for (let i = 0; i < files.length; i++) {
      const formData = new FormData();
      formData.append("file", files[i]);

      try {
        await axios.post(`${API_URL}/upload`, formData, {
          headers: { 
            Authorization: `Bearer ${session.access_token}`,
            "Content-Type": "multipart/form-data"
          }
        });
      } catch (err) {
        console.error("Upload failed", err);
        alert(`Failed to upload ${files[i].name}`);
      }
    }
    setLoading(false);
    fetchDocs();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setOver(false);
    handleUpload(e.dataTransfer.files as any);
  };

  const filtered = docs.filter(d => d.filename.toLowerCase().includes(q.toLowerCase()));

  return (
    <div>
      <div className="pghdr fx jb ic">
        <div>
          <h1 className="pgtit">Knowledge Base</h1>
          <p className="pgsub">Upload documents, manage your vector indices, and configure context.</p>
        </div>
        <Btn v="s" onClick={() => window.location.href = `${API_URL}/auth/google-sheets/connect`}>
          <img src="https://upload.wikimedia.org/wikipedia/commons/3/30/Google_Sheets_logo_%282014-2020%29.svg" alt="Sheets" width="16" style={{marginRight: 8}}/>
          Connect Google Sheets
        </Btn>
      </div>

      <div className="sec">
        <div
          className={`dz mb24 ${over ? "over" : ""}`}
          onDragOver={(e) => { e.preventDefault(); setOver(true); }}
          onDragLeave={() => setOver(false)}
          onDrop={handleDrop}
          onClick={() => ref.current?.click()}
        >
          <input type="file" ref={ref} style={{ display: "none" }} multiple onChange={(e) => handleUpload(e.target.files)} />
          <Upload size={32} color="var(--cy)" style={{ margin: "0 auto 16px" }} />
          <div className="w6 base mb4">{loading ? "Uploading and processing..." : "Click or drag files to upload"}</div>
          <div className="xs tm">Supports PDF, DOCX, CSV, TXT (Max 50MB)</div>
        </div>

        <div className="card">
          <div className="fx jb ic p16" style={{ borderBottom: "1px solid var(--b)" }}>
            <div className="w6">Your Documents</div>
            <div className="fx ic gap12">
              <div className="rel">
                <Search size={14} color="var(--tm)" className="abs" style={{ left: 12, top: "50%", transform: "translateY(-50%)" }} />
                <Inp placeholder="Search files..." value={q} onChange={(e: any) => setQ(e.target.value)} style={{ paddingLeft: 34, width: 220 }} />
              </div>
              <Btn v="g" sm><Trash2 size={13} /> Delete all</Btn>
            </div>
          </div>
          <table className="tbl">
            <thead>
              <tr>
                <th>Document</th>
                <th>Status</th>
                <th>Size</th>
                <th>Chunks</th>
                <th>Uploaded</th>
                <th style={{ textAlign: "right" }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(d => (
                <tr key={d.id}>
                  <td>
                    <div className="fx ic gap10">
                      <div style={{ width: 28, height: 28, borderRadius: 6, background: "var(--s2)", border: "1px solid var(--b)", display: "flex", alignItems: "center", justifyContent: "center" }}>
                        <FileText size={14} style={{ color: "var(--cy)" }} />
                      </div>
                      <div className="f1 trunc" style={{ maxWidth: 200 }}>
                        <div className="w5 mb4 trunc">{d.filename}</div>
                        <div className="xs tm">{d.file_type}</div>
                      </div>
                    </div>
                  </td>
                  <td>
                    <Badge t="ok">Indexed</Badge>
                  </td>
                  <td className="tm">{(d.file_size_bytes / 1024).toFixed(1)} KB</td>
                  <td className="tm">{d.chunks_count}</td>
                  <td className="tm">{new Date(d.created_at).toLocaleDateString()}</td>
                  <td>
                    <div className="fx jb ic" style={{ justifyContent: "flex-end" }}>
                      <Trash2 size={14} color="var(--tm)" className="ptr" />
                    </div>
                  </td>
                </tr>
              ))}
              {filtered.length === 0 && (
                <tr>
                  <td colSpan={6} style={{ textAlign: "center", padding: "40px 20px", color: "var(--tm)" }}>No documents found.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
